# backend/app/services/image_quality.py

import cv2
import numpy as np


MIN_WIDTH = 200
MIN_HEIGHT = 200

BLUR_THRESHOLD = 100.0       # Laplacian variance below this = blurry
DARK_THRESHOLD = 40.0        # mean brightness (0-255) below this = too dark
BRIGHT_THRESHOLD = 220.0     # mean brightness above this = overexposed
LOW_CONTRAST_THRESHOLD = 20.0  # std dev of pixel intensities below this = flat/low contrast


def _sharpness_score(gray: np.ndarray) -> float:
    """Variance of the Laplacian — a standard blur detector.
    Lower values mean a blurrier image."""
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def _brightness_score(gray: np.ndarray) -> float:
    return float(np.mean(gray))


def _contrast_score(gray: np.ndarray) -> float:
    return float(np.std(gray))


def analyze_image_quality(image: np.ndarray) -> dict:
    """
    Runs a set of image-quality checks on the raw uploaded image
    (before preprocessing) and returns a report the frontend/report
    can surface. This does not block inspection — it flags issues
    so a human can judge whether to trust a borderline result.
    """

    height, width = image.shape[:2]

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    sharpness = _sharpness_score(gray)
    brightness = _brightness_score(gray)
    contrast = _contrast_score(gray)

    issues = []

    if width < MIN_WIDTH or height < MIN_HEIGHT:
        issues.append("low_resolution")

    if sharpness < BLUR_THRESHOLD:
        issues.append("blurry")

    if brightness < DARK_THRESHOLD:
        issues.append("too_dark")
    elif brightness > BRIGHT_THRESHOLD:
        issues.append("overexposed")

    if contrast < LOW_CONTRAST_THRESHOLD:
        issues.append("low_contrast")

    quality_score = 100.0
    quality_score -= 30 if "low_resolution" in issues else 0
    quality_score -= 30 if "blurry" in issues else 0
    quality_score -= 20 if ("too_dark" in issues or "overexposed" in issues) else 0
    quality_score -= 20 if "low_contrast" in issues else 0
    quality_score = max(0.0, quality_score)

    if quality_score >= 80:
        rating = "good"
    elif quality_score >= 50:
        rating = "acceptable"
    else:
        rating = "poor"

    return {
        "quality_score": round(quality_score, 1),
        "rating": rating,
        "resolution": {"width": width, "height": height},
        "sharpness": round(sharpness, 2),
        "brightness": round(brightness, 2),
        "contrast": round(contrast, 2),
        "issues": issues
    }