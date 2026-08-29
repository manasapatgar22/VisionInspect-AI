from pathlib import Path
from collections import defaultdict

import cv2

from app.services.anomaly_detection import (
    MVTecAnomalyDetector
)

from app.services.defect_classifier import (
    DefectClassifier
)


DATASET = Path(
    "dataset/mvtec/bottle/test"
)


def main():

    detector = MVTecAnomalyDetector(
        max_reference_images=209
    )

    detector.build_reference(
        "dataset/mvtec/bottle/train/good"
    )

    classifier = DefectClassifier(
        detector
    )

    classifier.build_prototypes(
        str(DATASET),
        max_images_per_class=20
    )

    confusion = defaultdict(
        lambda: defaultdict(int)
    )

    total = 0
    correct = 0

    for class_directory in sorted(
        DATASET.iterdir()
    ):

        if not class_directory.is_dir():
            continue

        actual_class = (
            class_directory.name
        )

        image_paths = list(
            class_directory.glob("*.png")
        )

        for image_path in image_paths:

            image = cv2.imread(
                str(image_path)
            )

            if image is None:
                continue

            result = classifier.predict(
                image
            )

            predicted_class = (
                result["defect_type"]
            )

            confusion[
                actual_class
            ][predicted_class] += 1

            total += 1

            if predicted_class == actual_class:
                correct += 1

    accuracy = (
        correct / total
        if total
        else 0
    )

    print()
    print("Defect Classification Evaluation")
    print("=================================")

    print(
        f"Total images: {total}"
    )

    print(
        f"Correct predictions: {correct}"
    )

    print(
        f"Accuracy: {accuracy:.4f}"
    )

    print()
    print("Confusion Matrix")
    print("----------------")

    classes = sorted(
        confusion.keys()
    )

    for actual in classes:

        print(
            f"{actual}: "
            f"{dict(confusion[actual])}"
        )


if __name__ == "__main__":
    main()
