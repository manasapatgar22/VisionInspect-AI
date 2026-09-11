# backend/app/models/inspection.py

from sqlalchemy import Column, Integer, String, Float, DateTime, func

from app.database import Base


class InspectionRecord(Base):
    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    category = Column(String, nullable=True)
    defect_type = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    anomaly_score = Column(Float, nullable=True)
    severity_score = Column(Float, nullable=True)
    severity_level = Column(String, nullable=True)
    decision = Column(String, nullable=True)
    image_quality_score = Column(Float, nullable=True)
    image_quality_rating = Column(String, nullable=True)
    image_quality_issues = Column(String, nullable=True)  # comma-separated
    inspected_by = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())