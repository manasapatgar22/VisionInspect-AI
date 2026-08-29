from datetime import datetime
from typing import Dict, List


inspection_history: List[Dict] = []


def add_inspection(report: Dict) -> Dict:
    """
    Store a completed inspection in memory.
    """

    record = {
        "id": len(inspection_history) + 1,
        "timestamp": datetime.now().isoformat(),
        "filename": report["inspection"]["filename"],
        "defect_type": report["classification"]["defect_type"],
        "confidence": report["classification"]["confidence"],
        "anomaly_score": report["anomaly_detection"]["anomaly_score"],
        "severity": report["severity"]["severity_level"],
        "severity_score": report["severity"]["severity_score"],
        "decision": report["quality_control"]["decision"]
    }

    inspection_history.append(record)

    return record


def get_inspection_history() -> List[Dict]:
    """
    Return all stored inspections.
    """

    return inspection_history


def get_inspection_statistics() -> Dict:
    """
    Calculate basic inspection statistics.
    """

    total = len(inspection_history)

    passed = sum(
        1
        for item in inspection_history
        if item["decision"] == "PASS"
    )

    failed = sum(
        1
        for item in inspection_history
        if item["decision"] == "FAIL"
    )

    critical = sum(
        1
        for item in inspection_history
        if item["severity"] == "Critical"
    )

    defect_counts = {}

    for item in inspection_history:

        defect = item["defect_type"]

        defect_counts[defect] = (
            defect_counts.get(defect, 0) + 1
        )

    most_common_defect = None

    if defect_counts:
        most_common_defect = max(
            defect_counts,
            key=defect_counts.get
        )

    return {
        "total_inspections": total,
        "passed": passed,
        "failed": failed,
        "critical": critical,
        "most_common_defect": most_common_defect,
        "defect_counts": defect_counts
    }
