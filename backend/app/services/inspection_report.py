from datetime import datetime
from typing import Dict


def create_inspection_report(
    filename: str,
    anomaly_score: float,
    classification: Dict,
    severity: Dict,
    quality: Dict
) -> Dict:
    """
    Create a structured inspection report.
    """

    return {
        "inspection": {
            "filename": filename,
            "timestamp": datetime.utcnow().isoformat()
        },
        "anomaly_detection": {
            "anomaly_score": anomaly_score
        },
        "classification": classification,
        "severity": severity,
        "quality_control": quality
    }
