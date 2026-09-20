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
    Localize defects using spatial ResNet18 feature maps.

    Unlike raw pixel difference, this compares spatial deep
    features between the inspected image and a normal reference.
    """

    import torch
    from torchvision import models, transforms

    if image is None or reference is None:
        return {
            "detected": False,
            "bounding_box": None,
            "defect_area_percent": 0.0
        }

    # Resize both images to the ResNet input size.
    image_resized = cv2.resize(
        image,
        (224, 224)
    )

    reference_resized = cv2.resize(
        reference,
        (224, 224)
    )

    # Convert BGR -> RGB.
    image_rgb = cv2.cvtColor(
        image_resized,
        cv2.COLOR_BGR2RGB
    )

    reference_rgb = cv2.cvtColor(
        reference_resized,
        cv2.COLOR_BGR2RGB
    )

    # ImageNet preprocessing.
    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    image_tensor = transform(
        image_rgb
    ).unsqueeze(0)

    reference_tensor = transform(
        reference_rgb
    ).unsqueeze(0)

    device = torch.device(
        "cuda" if torch.cuda.is_available()
        else "cpu"
    )

    # ResNet18 up to layer3.
    backbone = models.resnet18(
        weights=models.ResNet18_Weights.DEFAULT
    )

    feature_extractor = torch.nn.Sequential(
        *list(backbone.children())[:-3]
    )

    feature_extractor = feature_extractor.to(
        device
    )

    feature_extractor.eval()

    image_tensor = image_tensor.to(device)
    reference_tensor = reference_tensor.to(device)

    with torch.no_grad():

        image_features = feature_extractor(
            image_tensor
        )

        reference_features = feature_extractor(
            reference_tensor
        )

    # Spatial feature difference.
    difference = torch.abs(
        image_features - reference_features
    )

    # Average the 256 feature channels.
    heatmap = difference.mean(
        dim=1
    ).squeeze()

    heatmap = heatmap.cpu().numpy()

    # Normalize heatmap to 0-255.
    heatmap_min = heatmap.min()
    heatmap_max = heatmap.max()

    if heatmap_max - heatmap_min < 1e-8:
        return {
            "detected": False,
            "bounding_box": None,
            "defect_area_percent": 0.0
        }

    heatmap = (
        (heatmap - heatmap_min)
        / (heatmap_max - heatmap_min)
        * 255
    ).astype(np.uint8)

    # Resize heatmap back to image coordinates.
    heatmap = cv2.resize(
        heatmap,
        (256, 256),
        interpolation=cv2.INTER_CUBIC
    )

    # Use an adaptive threshold based on the heatmap.
    threshold_value = max(
        30,
        int(np.mean(heatmap) + 2 * np.std(heatmap))
    )

    _, mask = cv2.threshold(
        heatmap,
        threshold_value,
        255,
        cv2.THRESH_BINARY
    )

    # Remove small isolated noise.
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

    # Find candidate defect regions.
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

    # Ignore tiny regions.
    image_area = 256 * 256

    valid_contours = [
        contour
        for contour in contours
        if cv2.contourArea(contour)
        >= image_area * 0.002
    ]

    if not valid_contours:
        return {
            "detected": False,
            "bounding_box": None,
            "defect_area_percent": 0.0
        }

    # Select the strongest/largest candidate.
    largest_contour = max(
        valid_contours,
        key=cv2.contourArea
    )

    area = cv2.contourArea(
        largest_contour
    )

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
            float((area / image_area) * 100.0),
            2
        )
    }
def localize_defect_multi_reference(
    image: np.ndarray,
    references: list[np.ndarray]
) -> dict:
    """
    Localize defects using multiple normal reference images
    and spatial ResNet18 feature maps.
    """

    import torch
    from torchvision import models, transforms

    if image is None or not references:
        return {
            "detected": False,
            "bounding_box": None,
            "defect_area_percent": 0.0
        }

    device = torch.device(
        "cuda" if torch.cuda.is_available()
        else "cpu"
    )

    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    backbone = models.resnet18(
        weights=models.ResNet18_Weights.DEFAULT
    )

    feature_extractor = torch.nn.Sequential(
        *list(backbone.children())[:-3]
    )

    feature_extractor = feature_extractor.to(device)
    feature_extractor.eval()

    image_resized = cv2.resize(
        image,
        (224, 224)
    )

    image_rgb = cv2.cvtColor(
        image_resized,
        cv2.COLOR_BGR2RGB
    )

    image_tensor = transform(
        image_rgb
    ).unsqueeze(0).to(device)

    with torch.no_grad():
        image_features = feature_extractor(
            image_tensor
        )

    reference_heatmaps = []

    for reference in references:

        if reference is None:
            continue

        reference_resized = cv2.resize(
            reference,
            (224, 224)
        )

        reference_rgb = cv2.cvtColor(
            reference_resized,
            cv2.COLOR_BGR2RGB
        )

        reference_tensor = transform(
            reference_rgb
        ).unsqueeze(0).to(device)

        with torch.no_grad():
            reference_features = feature_extractor(
                reference_tensor
            )

        difference = torch.abs(
            image_features - reference_features
        )

        heatmap = difference.mean(
            dim=1
        ).squeeze()

        reference_heatmaps.append(
            heatmap
        )

    if not reference_heatmaps:
        return {
            "detected": False,
            "bounding_box": None,
            "defect_area_percent": 0.0
        }

    heatmaps = torch.stack(
        reference_heatmaps
    )

    heatmap = torch.min(
        heatmaps,
        dim=0
    ).values

    heatmap = heatmap.cpu().numpy()

    minimum = heatmap.min()
    maximum = heatmap.max()

    if maximum - minimum < 1e-8:
        return {
            "detected": False,
            "bounding_box": None,
            "defect_area_percent": 0.0
        }

    heatmap = (
        (heatmap - minimum)
        / (maximum - minimum)
        * 255
    ).astype(np.uint8)

    heatmap = cv2.resize(
        heatmap,
        (256, 256),
        interpolation=cv2.INTER_CUBIC
    )

    threshold_value = max(
        30,
        int(
            np.mean(heatmap)
            + 2 * np.std(heatmap)
        )
    )

    _, mask = cv2.threshold(
        heatmap,
        threshold_value,
        255,
        cv2.THRESH_BINARY
    )

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

    image_area = 256 * 256

    valid_contours = [
        contour
        for contour in contours
        if cv2.contourArea(contour)
        >= image_area * 0.002
    ]

    if not valid_contours:
        return {
            "detected": False,
            "bounding_box": None,
            "defect_area_percent": 0.0
        }

    largest_contour = max(
        valid_contours,
        key=cv2.contourArea
    )

    area = cv2.contourArea(
        largest_contour
    )

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
            float(
                (area / image_area) * 100.0
            ),
            2
        )
    }