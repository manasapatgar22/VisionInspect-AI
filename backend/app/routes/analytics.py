from datetime import date
from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.inspection import InspectionRecord

import csv
import io
from datetime import datetime

from fastapi.responses import StreamingResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

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


@router.get("/trend")
def inspection_trend(
    db: Session = Depends(get_db)
):
    """
    Daily counts of PASS / FAIL / REVIEW decisions, for the
    trend chart. Grouped in Python rather than SQL to stay
    database-agnostic (works the same on SQLite or Postgres).
    """

    records = (
        db.query(
            InspectionRecord.created_at,
            InspectionRecord.decision
        )
        .all()
    )

    daily = defaultdict(lambda: {"PASS": 0, "FAIL": 0, "REVIEW": 0})

    for created_at, decision in records:
        if not created_at or not decision:
            continue
        day_key = created_at.date().isoformat()
        if decision in daily[day_key]:
            daily[day_key][decision] += 1

    trend = [
        {"date": day, **counts}
        for day, counts in sorted(daily.items())
    ]

    return {"trend": trend}


@router.get("/defect-distribution")
def defect_distribution(
    db: Session = Depends(get_db)
):
    """
    Count of inspections per defect_type, for the
    defect-distribution chart.
    """

    rows = (
        db.query(
            InspectionRecord.defect_type,
            func.count(InspectionRecord.id)
        )
        .group_by(InspectionRecord.defect_type)
        .all()
    )

    return {
        "distribution": [
            {"defect_type": defect_type or "unknown", "count": count}
            for defect_type, count in rows
        ]
    }


@router.get("/severity-distribution")
def severity_distribution(
    db: Session = Depends(get_db)
):
    """
    Count of inspections per severity_level, for the
    severity-distribution chart.
    """

    rows = (
        db.query(
            InspectionRecord.severity_level,
            func.count(InspectionRecord.id)
        )
        .group_by(InspectionRecord.severity_level)
        .all()
    )

    return {
        "distribution": [
            {"severity_level": severity_level or "unknown", "count": count}
            for severity_level, count in rows
        ]
    }
@router.get("/export/csv")
def export_csv(
    db: Session = Depends(get_db)
):
    """
    Streams all inspection records as a downloadable CSV —
    the raw production quality report.
    """

    records = (
        db.query(InspectionRecord)
        .order_by(InspectionRecord.created_at.desc())
        .all()
    )

    buffer = io.StringIO()
    writer = csv.writer(buffer)

    writer.writerow([
        "ID", "Filename", "Category", "Defect Type", "Confidence",
        "Anomaly Score", "Severity Score", "Severity Level",
        "Decision", "Inspected By", "Created At"
    ])

    for record in records:
        writer.writerow([
            record.id,
            record.filename,
            record.category,
            record.defect_type,
            record.confidence,
            record.anomaly_score,
            record.severity_score,
            record.severity_level,
            record.decision,
            record.inspected_by,
            record.created_at.isoformat() if record.created_at else ""
        ])

    buffer.seek(0)

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=visioninspect_report.csv"
        }
    )

@router.get("/export/pdf")
def export_pdf(
    db: Session = Depends(get_db)
):
    """
    Generates a formatted PDF summary report — aggregate stats
    plus a table of recent inspections, suitable for handing
    to management.
    """

    total = db.query(InspectionRecord).count()
    passed = db.query(InspectionRecord).filter(InspectionRecord.decision == "PASS").count()
    failed = db.query(InspectionRecord).filter(InspectionRecord.decision == "FAIL").count()
    review = db.query(InspectionRecord).filter(InspectionRecord.decision == "REVIEW").count()
    critical = db.query(InspectionRecord).filter(InspectionRecord.severity_level == "Critical").count()

    recent = (
        db.query(InspectionRecord)
        .order_by(InspectionRecord.created_at.desc())
        .limit(25)
        .all()
    )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("VisionInspect AI — Production Quality Report", styles["Title"]))
    elements.append(Paragraph(
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        styles["Normal"]
    ))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Summary", styles["Heading2"]))

    summary_data = [
        ["Total Inspections", "Passed", "Failed", "Review", "Critical"],
        [str(total), str(passed), str(failed), str(review), str(critical)]
    ]

    summary_table = Table(summary_data, hAlign="LEFT")
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Recent Inspections", styles["Heading2"]))

    table_data = [["Filename", "Category", "Defect Type", "Severity", "Decision", "Date"]]

    for record in recent:
        table_data.append([
            record.filename or "",
            record.category or "",
            record.defect_type or "",
            record.severity_level or "",
            record.decision or "",
            record.created_at.strftime("%Y-%m-%d") if record.created_at else ""
        ])

    detail_table = Table(table_data, hAlign="LEFT")
    detail_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))
    elements.append(detail_table)

    doc.build(elements)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=visioninspect_report.pdf"
        }
    )