"""
Held-out defect classification evaluation.

Unlike evaluate_classifier_metrics.py, this script never lets the
classifier see an image during evaluation that it also used to build
its prototypes. Each class folder under dataset/mvtec/bottle/test is
split deterministically into:

  - a "support" set  -> used ONLY to build prototypes
  - a "query" set     -> used ONLY to compute metrics

This gives an honest accuracy/precision/recall/F1/confusion-matrix,
instead of the optimistic number you get from scoring the classifier
on the same images it was built from.

Run from inside backend/:

    python evaluate_classifier_holdout.py

Optional:

    python evaluate_classifier_holdout.py --support-per-class 10 --seed 42
"""

import argparse
import random
from collections import defaultdict
from pathlib import Path

import cv2

from app.services.anomaly_detection import MVTecAnomalyDetector
from app.services.defect_classifier import DefectClassifier


DATASET = Path("dataset/mvtec/bottle/test")
TRAIN_GOOD = Path("dataset/mvtec/bottle/train/good")


def collect_class_images(dataset_dir: Path):
    """
    Returns {class_name: [image_path, ...]} for every class folder
    under dataset_dir, sorted for reproducibility.
    """

    class_images = {}

    for class_dir in sorted(dataset_dir.iterdir()):

        if not class_dir.is_dir():
            continue

        image_paths = sorted(class_dir.glob("*.png"))
        image_paths += sorted(class_dir.glob("*.jpg"))

        class_images[class_dir.name] = image_paths

    return class_images


def split_support_query(class_images, support_per_class: int, seed: int):
    """
    Deterministically shuffles each class's images and splits them
    into a support set (for prototypes) and a query set (for eval).
    No image ever appears in both sets.
    """

    rng = random.Random(seed)

    support = {}
    query = {}

    for class_name, image_paths in class_images.items():

        shuffled = list(image_paths)
        rng.shuffle(shuffled)

        support[class_name] = shuffled[:support_per_class]
        query[class_name] = shuffled[support_per_class:]

    return support, query


def build_prototypes_from_split(classifier: DefectClassifier, support: dict):
    """
    Builds prototypes directly from an in-memory support split,
    instead of DefectClassifier.build_prototypes(directory), since
    we need class folders divided by our own split rather than by
    "every image in the folder".
    """

    counts = {}

    for class_name, image_paths in support.items():

        features = []

        for image_path in image_paths:

            image = cv2.imread(str(image_path))

            if image is None:
                continue

            features.append(classifier.detector.extract_features(image))

        if features:
            import numpy as np
            classifier.prototypes[class_name] = np.mean(features, axis=0)
            counts[class_name] = len(features)
        else:
            counts[class_name] = 0

    return counts


def evaluate(classifier: DefectClassifier, query: dict):

    classes = sorted(query.keys())
    confusion = defaultdict(lambda: defaultdict(int))

    total = 0
    correct = 0

    for actual_class, image_paths in query.items():

        for image_path in image_paths:

            image = cv2.imread(str(image_path))

            if image is None:
                continue

            result = classifier.predict(image)
            predicted_class = result["defect_type"]

            confusion[actual_class][predicted_class] += 1
            total += 1

            if predicted_class == actual_class:
                correct += 1

    return classes, confusion, total, correct


def print_confusion_matrix(classes, confusion):

    print()
    print("Confusion Matrix (rows = actual, columns = predicted)")
    print("-------------------------------------------------------")

    header = "actual \\ predicted".ljust(20) + "".join(c[:12].rjust(14) for c in classes)
    print(header)

    for actual in classes:
        row = actual.ljust(20)
        for predicted in classes:
            row += str(confusion[actual][predicted]).rjust(14)
        print(row)


def print_metrics(classes, confusion):

    print()
    print("Per-Class Metrics")
    print("------------------")

    all_precisions = []
    all_recalls = []
    all_f1 = []

    for class_name in classes:

        true_positive = confusion[class_name][class_name]

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
            true_positive / (true_positive + false_positive)
            if (true_positive + false_positive) else 0
        )

        recall = (
            true_positive / (true_positive + false_negative)
            if (true_positive + false_negative) else 0
        )

        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) else 0
        )

        all_precisions.append(precision)
        all_recalls.append(recall)
        all_f1.append(f1)

        support_count = sum(confusion[class_name].values())

        print()
        print(f"{class_name}  (n={support_count})")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall:    {recall:.4f}")
        print(f"  F1 Score:  {f1:.4f}")

    print()
    print("Macro Average")
    print("-------------")
    print(f"Precision: {sum(all_precisions) / len(all_precisions):.4f}")
    print(f"Recall:    {sum(all_recalls) / len(all_recalls):.4f}")
    print(f"F1 Score:  {sum(all_f1) / len(all_f1):.4f}")


def main():

    parser = argparse.ArgumentParser(
        description="Held-out defect classification evaluation."
    )
    parser.add_argument(
        "--support-per-class",
        type=int,
        default=10,
        help="Images per class used ONLY to build prototypes (default: 10).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for the support/query split (default: 42).",
    )
    args = parser.parse_args()

    detector = MVTecAnomalyDetector(max_reference_images=209)
    detector.build_reference(str(TRAIN_GOOD))

    classifier = DefectClassifier(detector)

    class_images = collect_class_images(DATASET)

    print("Class image counts (before split):")
    for class_name, paths in class_images.items():
        print(f"  {class_name}: {len(paths)}")

    too_small = [
        class_name
        for class_name, paths in class_images.items()
        if len(paths) <= args.support_per_class
    ]

    if too_small:
        print()
        print("WARNING: these classes have too few images to leave any")
        print("held-out query images at the current --support-per-class:")
        for class_name in too_small:
            print(f"  {class_name}: {len(class_images[class_name])} images")
        print("Reduce --support-per-class or add more images for these classes.")

    support, query = split_support_query(
        class_images,
        support_per_class=args.support_per_class,
        seed=args.seed,
    )

    print()
    print("Support set (used to build prototypes) / Query set (held-out eval):")
    for class_name in class_images:
        print(f"  {class_name}: support={len(support[class_name])}, query={len(query[class_name])}")

    build_prototypes_from_split(classifier, support)

    classes, confusion, total, correct = evaluate(classifier, query)

    accuracy = correct / total if total else 0

    print()
    print("Held-Out Defect Classification Evaluation")
    print("==========================================")
    print(f"Query (held-out) images evaluated: {total}")
    print(f"Correct predictions: {correct}")
    print(f"Accuracy: {accuracy:.4f}")

    print_confusion_matrix(classes, confusion)
    print_metrics(classes, confusion)


if __name__ == "__main__":
    main()