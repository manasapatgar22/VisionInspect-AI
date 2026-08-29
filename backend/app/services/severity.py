from typing import Dict


def calculate_size_score(defect_area_percent: float) -> float:
    """
    Convert defect area percentage into a severity score.
    """

    defect_area_percent = max(
        0.0,
        min(100.0, defect_area_percent)
    )

    # Larger defect area = higher severity.
    return round(defect_area_percent, 2)


def calculate_severity(
    size_score: float,
    location_score: float,
    defect_type_score: float,
    confidence_score: float
) -> Dict:
    """
    Calculate severity using the project weighting:

    Size       = 30%
    Location   = 25%
    Defect Type = 25%
    Confidence = 20%
    """

    scores = [
        size_score,
        location_score,
        defect_type_score,
        confidence_score
    ]

    scores = [
        max(0.0, min(100.0, score))
        for score in scores
    ]

    (
        size_score,
        location_score,
        defect_type_score,
        confidence_score
    ) = scores

    severity_score = (
        size_score * 0.30
        + location_score * 0.25
        + defect_type_score * 0.25
        + confidence_score * 0.20
    )

    severity_score = round(
        severity_score,
        2
    )

    if severity_score >= 80:
        level = "Critical"
        action = "Reject Product and Trigger Quality Inspection Workflow"

    elif severity_score >= 60:
        level = "High"
        action = "Repair or Rework Recommended"

    elif severity_score >= 40:
        level = "Medium"
        action = "Inspection Review Required"

    else:
        level = "Low"
        action = "Product Generally Acceptable"

    return {
        "severity_score": severity_score,
        "severity_level": level,
        "recommended_action": action
    }
