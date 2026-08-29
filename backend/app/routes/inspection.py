from pathlib import Path
import shutil
import tempfile

import cv2
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.models.user import User
from app.routes.auth import get_current_user

from sqlalchemy.orm import Session

from app.database import get_db
from app.models.inspection import InspectionRecord

from app.services.image_processing import preprocess_image
from app.services.anomaly_detection import MVTecAnomalyDetector
from app.services.defect_classifier import DefectClassifier
from app.services.severity import calculate_severity
from app.services.quality_control import make_quality_decision
from app.services.inspection_report import create_inspection_report
from app.services.defect_detection import localize_defect
from app.services.inspection_history import (
    add_inspection
)

router = APIRouter(
    prefix="/api/inspection",
    tags=["Inspection"]
)


# ---------------------------------------------------------
# AI MODELS
# ---------------------------------------------------------

detector = MVTecAnomalyDetector(
    max_reference_images=209
)

REFERENCE_DIRECTORY = Path(
    "dataset/mvtec/bottle/train/good"
)

try:
    detector.build_reference(
        REFERENCE_DIRECTORY
    )

    classifier = DefectClassifier(
        detector
    )

    classifier.build_prototypes(
        "dataset/mvtec/bottle/test",
        max_images_per_class=20
    )

    models_ready = True

except Exception as error:
    print(
        f"Model initialization failed: {error}"
    )

    classifier = None
    models_ready = False


# ---------------------------------------------------------
# INSPECTION ENDPOINT
# ---------------------------------------------------------

@router.post("/inspect")
async def inspect_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload an image and generate a complete
    VisionInspect inspection report.
    """
    if current_user.role not in ("quality_engineer", "factory_supervisor"):
        raise HTTPException(
            status_code=403,
            detail="Only quality engineers or factory supervisors can run inspections."
        )

    allowed_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp"
    }

    extension = Path(
        file.filename or ""
    ).suffix.lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image format."
        )

    if not models_ready:
        raise HTTPException(
            status_code=500,
            detail="Inspection models are not ready."
        )

    image_path = None

    try:

        # -------------------------------------------------
        # Save uploaded image temporarily
        # -------------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension
        ) as temp_file:

            shutil.copyfileobj(
                file.file,
                temp_file
            )

            image_path = temp_file.name

        # -------------------------------------------------
        # Read image
        # -------------------------------------------------

        image = cv2.imread(
            image_path
        )

        if image is None:
            raise ValueError(
                "Unable to read uploaded image."
            )

        # -------------------------------------------------
        # Preprocess image
        # -------------------------------------------------

        processed_image = preprocess_image(
            image_path
        )

        # -------------------------------------------------
        # Anomaly detection
        # -------------------------------------------------

        anomaly_score = detector.calculate_score(
            image
        )

        anomaly_detected = detector.is_anomaly(
            anomaly_score
        )

        # -------------------------------------------------
        # Defect classification
        # -------------------------------------------------

        classification = classifier.predict(
            image
        )
        
        # -------------------------------------------------
        # Defect localization
        # -------------------------------------------------

        reference_paths = list(
            REFERENCE_DIRECTORY.glob("*.png")
        )

        if reference_paths:

            reference_image = cv2.imread(
                str(reference_paths[0])
            )

            reference_image = cv2.resize(
                reference_image,
                (256, 256)
            )

            localization = localize_defect(
                image=cv2.resize(
                    image,
                    (256, 256)
                ),
                reference=reference_image
            )

        else:

            localization = {
                "detected": False,
                "bounding_box": None,
                "defect_area_percent": 0.0
            }




        defect_type = classification[
            "defect_type"
        ]

        confidence = classification[
            "confidence"
        ]

        # -------------------------------------------------
        # Determine defect type severity
        # -------------------------------------------------

        defect_severity_map = {
            "good": 5,
            "broken_small": 60,
            "broken_large": 90,
            "contamination": 75
        }

        defect_type_score = defect_severity_map.get(
            defect_type,
            50
        )

        # -------------------------------------------------
        # Estimate anomaly/location contribution
        # -------------------------------------------------

        if anomaly_detected:
            location_score = min(
                100.0,
                anomaly_score * 10
            )
        else:
            location_score = 10.0

        # -------------------------------------------------
        # Baseline defect area estimate
        #
        # A predicted mask model will replace this later.
        # -------------------------------------------------

        if anomaly_detected:
            size_score = min(
                100.0,
                anomaly_score * 5
            )
        else:
            size_score = 0.0

        # -------------------------------------------------
        # Severity
        # -------------------------------------------------

        severity = calculate_severity(
            size_score=size_score,
            location_score=location_score,
            defect_type_score=defect_type_score,
            confidence_score=confidence
        )

        # -------------------------------------------------
        # Quality decision
        # -------------------------------------------------

        quality = make_quality_decision(
            anomaly_score=anomaly_score,
            severity_score=severity[
                "severity_score"
            ]
        )

        # -------------------------------------------------
        # Final inspection report
        # -------------------------------------------------

        # Add localization information
        localization_result = {
            "detected": localization["detected"],
            "bounding_box": localization["bounding_box"],
            "defect_area_percent": localization[
                "defect_area_percent"
            ]
        }

        report = create_inspection_report(
            filename=file.filename,
            anomaly_score=round(
                anomaly_score,
                4
            ),
            classification={
                "defect_type": defect_type,
                "confidence": confidence,
                "anomaly_detected": anomaly_detected
            },
            severity=severity,
            quality=quality
        )
        report["localization"] = localization_result
        add_inspection(report)
        db.add(
            InspectionRecord(
                filename=file.filename,
                defect_type=defect_type,
                confidence=confidence,
                anomaly_score=round(anomaly_score, 4),
                severity_score=severity["severity_score"],
                severity_level=severity["severity_level"],
                decision=quality["decision"],
                inspected_by=current_user.username,
            )
        )
        db.commit()
        report["processing"] = {
            "image_shape": list(
                processed_image.shape
            ),
            "device": str(
                detector.device
            )
        }

        return report

    except HTTPException:
        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    finally:

        if image_path:

            Path(
                image_path
            ).unlink(
                missing_ok=True
            )
