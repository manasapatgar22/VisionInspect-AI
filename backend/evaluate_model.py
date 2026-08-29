from pathlib import Path

import cv2
import numpy as np

from app.services.anomaly_detection import MVTecAnomalyDetector


DATASET = Path("dataset/mvtec/bottle")

# Start with this threshold.
# We'll improve it based on the evaluation results.



def collect_images():
    """
    Collect normal and defective MVTec test images.
    """

    good_images = list(
        (DATASET / "test" / "good").glob("*.png")
    )

    defective_images = []

    test_directory = DATASET / "test"

    for folder in test_directory.iterdir():

        if not folder.is_dir():
            continue

        if folder.name == "good":
            continue

        defective_images.extend(
            folder.glob("*.png")
        )

    return good_images, defective_images


def main():

    detector = MVTecAnomalyDetector(
    max_reference_images=209
    )

    reference_count = detector.build_reference(
        DATASET / "train" / "good"
    )

    print(
        f"Reference images: {reference_count}"
    )

    good_images, defective_images = (
        collect_images()
    )

    print(
        f"Good test images: {len(good_images)}"
    )

    print(
        f"Defective test images: {len(defective_images)}"
    )

    true_positive = 0
    true_negative = 0
    false_positive = 0
    false_negative = 0

    # Evaluate normal images.
    for image_path in good_images:

        image = cv2.imread(
            str(image_path)
        )

        score = detector.calculate_score(
            image
        )

        predicted_defect = detector.is_anomaly(score)

        if predicted_defect:
            false_positive += 1
        else:
            true_negative += 1

    # Evaluate defective images.
    for image_path in defective_images:

        image = cv2.imread(
            str(image_path)
        )

        score = detector.calculate_score(
            image
        )

        predicted_defect = detector.is_anomaly(score)

        if predicted_defect:
            true_positive += 1
        else:
            false_negative += 1

    total = (
        true_positive
        + true_negative
        + false_positive
        + false_negative
    )

    accuracy = (
        (true_positive + true_negative)
        / total
        if total
        else 0
    )

    precision = (
        true_positive
        / (true_positive + false_positive)
        if (true_positive + false_positive)
        else 0
    )

    recall = (
        true_positive
        / (true_positive + false_negative)
        if (true_positive + false_negative)
        else 0
    )

    f1 = (
        2 * precision * recall
        / (precision + recall)
        if (precision + recall)
        else 0
    )

    print()
    print("Model Evaluation")
    print("=================")

    print(
    f"Threshold: {detector.threshold:.4f}"
    )

    print(
        f"True Positive: {true_positive}"
    )

    print(
        f"True Negative: {true_negative}"
    )

    print(
        f"False Positive: {false_positive}"
    )

    print(
        f"False Negative: {false_negative}"
    )

    print(
        f"Accuracy:  {accuracy:.4f}"
    )

    print(
        f"Precision: {precision:.4f}"
    )

    print(
        f"Recall:    {recall:.4f}"
    )

    print(
        f"F1 Score:  {f1:.4f}"
    )


if __name__ == "__main__":
    main()
