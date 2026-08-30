from pathlib import Path
import shutil
import tempfile

import cv2
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

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

DATASET_ROOT = Path("dataset/mvtec")

# ---------------------------------------------------------
# PER-CATEGORY MODEL CACHE
#
# Models are built lazily on first request for a category,
# not all at startup — loading all 15 MVTec categories up
# front would be slow and waste memory on categories you
# never use. Once built, a category's models stay cached
# for the life of the server process.
# ---------------------------------------------------------

_detectors = {}
_classifiers = {}
_model_errors = {}


def get_available_categories():
    """Lists MVTec category folders actually present on disk."""

    if not DATASET_ROOT.exists():
        return []

    return sorted([
        p.name for p in DATASET_ROOT.iterdir()
        if p.is_dir()
    ])


def get_models_for_category(category: str):
    """
    Lazily builds (and caches) the anomaly detector and
    classifier for one MVTec category. A category that
    previously failed to load is remembered, so repeated
    bad requests fail fast instead of retrying disk/model
    work every time.
    """

    if category in _model_errors:
        raise _model_errors[category]

    if category in _detectors:
        return _detectors[category], _classifiers[category]

    reference_directory = DATASET_ROOT / category / "train" / "good"
    test_directory = DATASET_ROOT / category / "test"

    try:
        detector = MVTecAnomalyDetector(
            max_reference_images=200
        )

        detector.build_reference(
            reference_directory
        )

        classifier = DefectClassifier(
            detector
        )

        classifier.build_prototypes(
            str(test_directory),
            max_images_per_class=20
        )

        _detectors[category] = detector
        _classifiers[category] = classifier

        return detector, classifier

    except Exception as error:

        wrapped = RuntimeError(
            f"Models for category '{category}' are not ready: {error}"
        )

        _model_errors[category] = wrapped

        raise wrapped


# ---------------------------------------------------------
# CATEGORY LISTING ENDPOINT
# ---------------------------------------------------------

@router.get("/categories")
def list_categories():
    """
    Returns whichever MVTec category folders exist under
    dataset/mvtec/ right now. Used by the frontend to
    populate the category dropdown dynamically — add a new
    category by downloading it into that folder, no code
    change required.
    """

    return {
        "categories": get_available_categories()
    }


# ---------------------------------------------------------
# INSPECTION ENDPOINT
# ---------------------------------------------------------

@router.post("/inspect")
async def inspect_image(
    file: UploadFile = File(...),
    category: str = Form("bottle"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload an image and generate a complete VisionInspect
    inspection report for the given product category.
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

    available_categories = get_available_categories()

    if category not in available_categories:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unknown category '{category}'. "
                f"Available categories: {available_categories}"
            )
        )

    try:
        detector, classifier = get_models_for_category(
            category
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    reference_directory = DATASET_ROOT / category / "train" / "good"

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
            reference_directory.glob("*.png")
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
        #
        # Defect type names differ per MVTec category — a
        # "cable" has bent_wire / cut_outer_insulation /
        # missing_wire, a "capsule" has crack / poke /
        # squeeze, etc. Rather than hardcode every category's
        # defect names, "good" is always low severity and any
        # other predicted type gets a moderate-high default,
        # unless a category has a specific mapping below.
        # Add entries to PER_CATEGORY_SEVERITY as you tune
        # specific categories.
        # -------------------------------------------------

        PER_CATEGORY_SEVERITY = {
            "bottle": {
                "good": 5,
                "broken_small": 60,
                "broken_large": 90,
                "contamination": 75
            }
            # Add other categories here, e.g.:
            # "capsule": {"good": 5, "crack": 70, "poke": 65, "scratch": 55, "squeeze": 80},
        }

        category_severity_map = PER_CATEGORY_SEVERITY.get(
            category,
            {}
        )

        if defect_type == "good":
            defect_type_score = category_severity_map.get(
                "good",
                5
            )
        else:
            defect_type_score = category_severity_map.get(
                defect_type,
                70
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
        report["category"] = category

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