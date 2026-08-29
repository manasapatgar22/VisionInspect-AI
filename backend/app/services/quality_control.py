from typing import Dict


def make_quality_decision(
    anomaly_score: float,
    severity_score: float
) -> Dict:
    """
    Generate a quality-control pass/fail decision.
    """

    if severity_score >= 80:
        decision = "FAIL"
        reason = "Critical defect detected."

    elif severity_score >= 60:
        decision = "FAIL"
        reason = "High-severity quality issue detected."

    elif anomaly_score >= 60:
        decision = "FAIL"
        reason = "Significant anomaly detected."

    elif severity_score >= 40:
        decision = "REVIEW"
        reason = "Moderate quality concern requires inspection."

    else:
        decision = "PASS"
        reason = "No significant quality issue detected."

    return {
        "decision": decision,
        "reason": reason
    }
