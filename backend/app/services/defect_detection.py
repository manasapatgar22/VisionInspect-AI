import numpy as np
import cv2
import numpy as np

def calculate_anomaly_score(
    image: np.ndarray,
    reference: np.ndarray
) -> float:
    """
    Calculate a simple anomaly score based on
    pixel-level difference between an image and
    a reference image.

    Returns a score from 0 to 100.
    """

    if image.shape != reference.shape:
        raise ValueError("Images must have the same dimensions.")

    difference = np.abs(image - reference)

    mean_difference = float(np.mean(difference))

    score = min(mean_difference * 100.0, 100.0)

    return round(score, 2)


def classify_anomaly(score: float) -> str:
    """
    Convert anomaly score into a simple inspection result.
    """

    if score >= 60:
        return "defective"

    if score >= 30:
        return "suspicious"

    return "normal"


def detect_defect(
    image: np.ndarray,
    reference: np.ndarray
) -> dict:
    """
    Perform basic anomaly detection.
    """

    score = calculate_anomaly_score(
        image,
        reference
    )

    result = classify_anomaly(score)

    return {
        "anomaly_score": score,
        "result": result
    }
def localize_defect(
    image: np.ndarray,
    reference: np.ndarray,
    threshold: int = 30
) -> dict:
    """
    Locate the region with the largest visual difference
    between the inspected image and a reference image.

    Returns a bounding box and defect area percentage.
    """

    if image.shape != reference.shape:
        raise ValueError(
            "Images must have the same dimensions."
        )

    # Calculate absolute pixel difference.
    difference = cv2.absdiff(
        image,
        reference
    )

    # Convert difference to grayscale.
    gray_difference = cv2.cvtColor(
        difference,
        cv2.COLOR_BGR2GRAY
    )

    # Threshold the difference.
    _, mask = cv2.threshold(
        gray_difference,
        threshold,
        255,
        cv2.THRESH_BINARY
    )

    # Remove small noise.
    kernel = np.ones(
        (5, 5),
        np.uint8
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel
    )

    # Find connected regions.
    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return {
            "detected": False,
            "bounding_box": None,
            "defect_area_percent": 0.0
        }

    # Select the largest suspicious region.
    largest_contour = max(
        contours,
        key=cv2.contourArea
    )

    area = cv2.contourArea(
        largest_contour
    )

    image_area = (
        image.shape[0] *
        image.shape[1]
    )

    area_percent = (
        area / image_area
    ) * 100.0

    x, y, width, height = cv2.boundingRect(
        largest_contour
    )

    return {
        "detected": True,
        "bounding_box": {
            "x": int(x),
            "y": int(y),
            "width": int(width),
            "height": int(height)
        },
        "defect_area_percent": round(
            float(area_percent),
            2
        )
    }
