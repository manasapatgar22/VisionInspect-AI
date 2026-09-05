from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.inspection import InspectionRecord

router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"]
)


@router.get("/history")
def inspection_history(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Returns the most recent inspections, newest first —
    the feed the monitoring dashboard displays.
    """

    records = (
        db.query(InspectionRecord)
        .order_by(InspectionRecord.created_at.desc())
        .limit(limit)
        .all()
    )

    return {
        "inspections": [
            {
                "id": record.id,
                "filename": record.filename,
                "category": record.category,
                "defect_type": record.defect_type,
                "confidence": record.confidence,
                "anomaly_score": record.anomaly_score,
                "severity_score": record.severity_score,
                "severity_level": record.severity_level,
                "decision": record.decision,
                "inspected_by": record.inspected_by,
                "created_at": record.created_at.isoformat() if record.created_at else None,
            }
            for record in records
        ]
    }


@router.get("/statistics")
def inspection_statistics(
    db: Session = Depends(get_db)
):
    """
    Aggregate stats computed directly from the database,
    so they survive server restarts (unlike the old
    in-memory version).
    """

    total = db.query(InspectionRecord).count()

    passed = (
        db.query(InspectionRecord)
        .filter(InspectionRecord.decision == "PASS")
        .count()
    )

    failed = (
        db.query(InspectionRecord)
        .filter(InspectionRecord.decision == "FAIL")
        .count()
    )

    critical = (
        db.query(InspectionRecord)
        .filter(InspectionRecord.severity_level == "Critical")
        .count()
    )

    return {
        "total_inspections": total,
        "passed": passed,
        "failed": failed,
        "critical": critical
    }