from pathlib import Path

import cv2
import numpy as np


ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}


def validate_image(image_path: str) -> bool:
    """
    Validate that the file exists and has a supported image extension.
    """
    path = Path(image_path)

    if not path.exists():
        return False

    return path.suffix.lower() in ALLOWED_EXTENSIONS


def load_image(image_path: str) -> np.ndarray:
    """
    Load an image using OpenCV.
    """
    if not validate_image(image_path):
        raise ValueError("Invalid or unsupported image file.")

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Unable to read image.")

    return image


def resize_image(
    image: np.ndarray,
    width: int = 256,
    height: int = 256
) -> np.ndarray:
    """
    Resize image to the required model input size.
    """
    return cv2.resize(image, (width, height))


def remove_noise(image: np.ndarray) -> np.ndarray:
    """
    Apply Gaussian blur to reduce image noise.
    """
    return cv2.GaussianBlur(image, (5, 5), 0)


def enhance_image(image: np.ndarray) -> np.ndarray:
    """
    Improve local contrast using CLAHE.
    """
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

    l_channel, a_channel, b_channel = cv2.split(lab)

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced_l = clahe.apply(l_channel)

    enhanced = cv2.merge(
        (enhanced_l, a_channel, b_channel)
    )

    return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)


def normalize_image(image: np.ndarray) -> np.ndarray:
    """
    Normalize pixel values from 0-255 to 0-1.
    """
    return image.astype(np.float32) / 255.0


def preprocess_image(
    image_path: str,
    width: int = 256,
    height: int = 256
) -> np.ndarray:
    """
    Complete preprocessing pipeline:
    validation → loading → resizing → noise removal
    → enhancement → normalization.
    """
    image = load_image(image_path)

    image = resize_image(
        image,
        width,
        height
    )

    image = remove_noise(image)

    image = enhance_image(image)

    image = normalize_image(image)

    return image
