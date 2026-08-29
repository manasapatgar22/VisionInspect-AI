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

    for class_directory in sorted(
        DATASET.iterdir()
    ):

        if not class_directory.is_dir():
            continue

        actual_class = class_directory.name

        for image_path in class_directory.glob("*.png"):

            image = cv2.imread(
                str(image_path)
            )

            if image is None:
                continue

            result = classifier.predict(
                image
            )

            predicted_class = result[
                "defect_type"
            ]

            confusion[
                actual_class
            ][predicted_class] += 1

            total += 1

    classes = sorted(
        confusion.keys()
    )

    print()
    print("Classification Metrics")
    print("=======================")

    all_precisions = []
    all_recalls = []
    all_f1 = []

    for class_name in classes:

        true_positive = confusion[
            class_name
        ][class_name]

        false_positive = sum(
            confusion[actual][class_name]
            for actual in classes
            if actual != class_name
        )

        false_negative = sum(
            confusion[class_name][predicted]
            for predicted in classes
            if predicted != class_name
        )

        precision = (
            true_positive /
            (true_positive + false_positive)
            if true_positive + false_positive
            else 0
        )

        recall = (
            true_positive /
            (true_positive + false_negative)
            if true_positive + false_negative
            else 0
        )

        f1 = (
            2 * precision * recall /
            (precision + recall)
            if precision + recall
            else 0
        )

        all_precisions.append(
            precision
        )

        all_recalls.append(
            recall
        )

        all_f1.append(
            f1
        )

        print()
        print(class_name)

        print(
            f"  Precision: {precision:.4f}"
        )

        print(
            f"  Recall:    {recall:.4f}"
        )

        print(
            f"  F1 Score:  {f1:.4f}"
        )

    print()
    print("Macro Average")
    print("-------------")

    print(
        f"Precision: {sum(all_precisions) / len(all_precisions):.4f}"
    )

    print(
        f"Recall:    {sum(all_recalls) / len(all_recalls):.4f}"
    )

    print(
        f"F1 Score:  {sum(all_f1) / len(all_f1):.4f}"
    )


if __name__ == "__main__":
    main()
