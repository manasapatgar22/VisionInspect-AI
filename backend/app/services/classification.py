from typing import Dict


DEFECT_TYPES = {
    "broken_large": {
        "name": "Large Break",
        "base_severity": 90
    },
    "broken_small": {
        "name": "Small Break",
        "base_severity": 70
    },
    "contamination": {
        "name": "Contamination",
        "base_severity": 65
    },
    "crack": {
        "name": "Crack",
        "base_severity": 95
    },
    "damage": {
        "name": "Surface Damage",
        "base_severity": 75
    },
    "faulty_imprint": {
        "name": "Faulty Imprint",
        "base_severity": 60
    },
    "good": {
        "name": "No Defect",
        "base_severity": 0
    }
}


def classify_defect(
    defect_type: str,
    confidence: float
) -> Dict:
    """
    Convert a detected MVTec defect category into
    a structured classification result.
    """

    defect = DEFECT_TYPES.get(
        defect_type,
        {
            "name": "Unknown Defect",
            "base_severity": 50
        }
    )

    confidence = max(
        0.0,
        min(100.0, confidence)
    )

    return {
        "defect_type": defect_type,
        "defect_name": defect["name"],
        "base_severity": defect["base_severity"],
        "confidence": round(confidence, 2)
    }
