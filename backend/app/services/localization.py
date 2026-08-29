from pathlib import Path

import cv2
import numpy as np


def load_ground_truth_mask(mask_path: str) -> np.ndarray:
    """
    Load an MVTec ground-truth defect mask.
    """

    path = Path(mask_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Mask not found: {mask_path}"
        )

    mask = cv2.imread(
        str(path),
        cv2.IMREAD_GRAYSCALE
    )

    if mask is None:
        raise ValueError(
            f"Unable to read mask: {mask_path}"
        )

    return mask


def get_defect_bounding_box(
    mask: np.ndarray
) -> dict:
    """
    Find the bounding box surrounding the defect.
    """

    # Convert mask to binary.
    binary = np.where(
        mask > 0,
        255,
        0
    ).astype(np.uint8)

    coordinates = cv2.findNonZero(
        binary
    )

    if coordinates is None:
        return {
            "detected": False,
            "x": 0,
            "y": 0,
            "width": 0,
            "height": 0
        }

    x, y, width, height = cv2.boundingRect(
        coordinates
    )

    return {
        "detected": True,
        "x": int(x),
        "y": int(y),
        "width": int(width),
        "height": int(height)
    }


def calculate_defect_area(
    mask: np.ndarray
) -> float:
    """
    Calculate percentage of the image covered by the defect.
    """

    defect_pixels = np.count_nonzero(
        mask > 0
    )

    total_pixels = mask.shape[0] * mask.shape[1]

    if total_pixels == 0:
        return 0.0

    return round(
        (defect_pixels / total_pixels) * 100,
        2
    )


def localize_defect(
    mask_path: str
) -> dict:
    """
    Complete MVTec defect localization.
    """

    mask = load_ground_truth_mask(
        mask_path
    )

    bounding_box = get_defect_bounding_box(
        mask
    )

    defect_area = calculate_defect_area(
        mask
    )

    return {
        "bounding_box": bounding_box,
        "defect_area_percent": defect_area
    }
