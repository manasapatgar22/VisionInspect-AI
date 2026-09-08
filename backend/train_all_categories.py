from pathlib import Path
from collections import defaultdict

import cv2
import numpy as np

from app.services.anomaly_detection import MVTecAnomalyDetector
from app.services.defect_classifier import DefectClassifier


DATASET_ROOT = Path("dataset/mvtec")

# Candidate multipliers to try per category. threshold = mean + multiplier * std.
CANDIDATE_MULTIPLIERS = [1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0]

# Same 20-images-per-class cap used by evaluate_classifier*.py, and the
# same known caveat applies here: prototypes are built from the same
# test/ images being scored, so classifier accuracy below is optimistic
# until the held-out split fix is done (see README "Known gaps").
MAX_IMAGES_PER_CLASS = 20


def get_available_categories():
    """Lists MVTec category folders actually present on disk."""

    if not DATASET_ROOT.exists():
        return []

    return sorted([
        p.name for p in DATASET_ROOT.iterdir() if p.is_dir()
    ])


def collect_test_images(test_directory):

    good_images = list(
        (test_directory / "good").glob("*.png")
    )

    defective_images = []

    for folder in test_directory.iterdir():

        if not folder.is_dir():
            continue

        if folder.name == "good":
            continue

        defective_images.extend(
            folder.glob("*.png")
        )

    return good_images, defective_images


def metrics_for_threshold(good_scores, defective_scores, threshold):

    true_negative = sum(1 for s in good_scores if s < threshold)
    false_positive = sum(1 for s in good_scores if s >= threshold)

    true_positive = sum(1 for s in defective_scores if s >= threshold)
    false_negative = sum(1 for s in defective_scores if s < threshold)

    total = true_positive + true_negative + false_positive + false_negative

    accuracy = (
        (true_positive + true_negative) / total if total else 0
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

    return {
        "threshold": threshold,
        "true_positive": true_positive,
        "true_negative": true_negative,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def evaluate_anomaly_detection(category):
    """
    Builds the reference set for one category, sweeps threshold
    multipliers against its labeled test images, and returns the
    best-by-F1 result plus the built detector (reused below so the
    classifier doesn't have to re-extract features).
    """

    train_directory = DATASET_ROOT / category / "train" / "good"
    test_directory = DATASET_ROOT / category / "test"

    if not train_directory.exists() or not test_directory.exists():
        return None

    detector = MVTecAnomalyDetector(max_reference_images=200)
    detector.build_reference(train_directory)

    if not detector.normal_scores:
        return None

    mean_score = float(np.mean(detector.normal_scores))
    std_score = float(np.std(detector.normal_scores))

    good_images, defective_images = collect_test_images(test_directory)

    if not good_images or not defective_images:
        return None

    good_scores = [
        detector.calculate_score(cv2.imread(str(path)))
        for path in good_images
    ]

    defective_scores = [
        detector.calculate_score(cv2.imread(str(path)))
        for path in defective_images
    ]

    sweep = [
        metrics_for_threshold(
            good_scores,
            defective_scores,
            mean_score + multiplier * std_score
        )
        for multiplier in CANDIDATE_MULTIPLIERS
    ]

    best_index = max(
        range(len(sweep)),
        key=lambda i: sweep[i]["f1"]
    )

    return {
        "detector": detector,
        "best_multiplier": CANDIDATE_MULTIPLIERS[best_index],
        "best_result": sweep[best_index],
        "good_count": len(good_images),
        "defective_count": len(defective_images),
    }


def evaluate_classifier(category, detector):
    """
    Builds classifier prototypes and scores every test image for
    one category, reusing the already-built detector.
    """

    test_directory = DATASET_ROOT / category / "test"

    classifier = DefectClassifier(detector)

    classifier.build_prototypes(
        str(test_directory),
        max_images_per_class=MAX_IMAGES_PER_CLASS
    )

    confusion = defaultdict(lambda: defaultdict(int))

    total = 0
    correct = 0

    for class_directory in sorted(test_directory.iterdir()):

        if not class_directory.is_dir():
            continue

        actual_class = class_directory.name

        for image_path in class_directory.glob("*.png"):

            image = cv2.imread(str(image_path))

            if image is None:
                continue

            result = classifier.predict(image)
            predicted_class = result["defect_type"]

            confusion[actual_class][predicted_class] += 1
            total += 1

            if predicted_class == actual_class:
                correct += 1

    accuracy = correct / total if total else 0

    classes = sorted(confusion.keys())
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

        all_f1.append(f1)

    macro_f1 = sum(all_f1) / len(all_f1) if all_f1 else 0

    return {
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "total": total,
        "correct": correct,
        "confusion": confusion,
    }


def main():

    categories = get_available_categories()

    if not categories:
        print(
            "No category folders found under dataset/mvtec/. "
            "Download at least one MVTec AD category first, e.g. "
            "dataset/mvtec/<category>/train/good/*.png and "
            "dataset/mvtec/<category>/test/<defect_type>/*.png"
        )
        return

    print(f"Found {len(categories)} categories: {', '.join(categories)}")
    print()

    summary_rows = []

    for category in categories:

        print("=" * 92)
        print(f"Category: {category}")
        print("=" * 92)

        anomaly_result = evaluate_anomaly_detection(category)

        if anomaly_result is None:
            print("  Skipped — missing or empty train/good or test data.")
            print()
            continue

        best = anomaly_result["best_result"]

        print(
            f"  Anomaly detection "
            f"(best multiplier={anomaly_result['best_multiplier']}):"
        )
        print(
            f"    accuracy={best['accuracy']:.4f} "
            f"precision={best['precision']:.4f} "
            f"recall={best['recall']:.4f} "
            f"f1={best['f1']:.4f}"
        )
        print(
            f"    good images={anomaly_result['good_count']} "
            f"defective images={anomaly_result['defective_count']}"
        )

        classifier_result = evaluate_classifier(
            category,
            anomaly_result["detector"]
        )

        print("  Defect classification:")
        print(
            f"    accuracy={classifier_result['accuracy']:.4f} "
            f"macro_f1={classifier_result['macro_f1']:.4f} "
            f"({classifier_result['correct']}/{classifier_result['total']})"
        )

        print()

        summary_rows.append({
            "category": category,
            "best_multiplier": anomaly_result["best_multiplier"],
            "anomaly_accuracy": best["accuracy"],
            "anomaly_precision": best["precision"],
            "anomaly_recall": best["recall"],
            "anomaly_f1": best["f1"],
            "classifier_accuracy": classifier_result["accuracy"],
            "classifier_macro_f1": classifier_result["macro_f1"],
        })

    if not summary_rows:
        print("No categories produced results.")
        return

    print("=" * 92)
    print("Summary across all categories")
    print("=" * 92)
    print(
        f"{'category':<15} {'mult':>5} | {'anom_acc':>8} "
        f"{'anom_prec':>9} {'anom_rec':>8} {'anom_f1':>7} | "
        f"{'cls_acc':>7} {'cls_f1':>6}"
    )
    print("-" * 92)

    for row in summary_rows:
        print(
            f"{row['category']:<15} {row['best_multiplier']:>5.2f} | "
            f"{row['anomaly_accuracy']:>8.4f} "
            f"{row['anomaly_precision']:>9.4f} "
            f"{row['anomaly_recall']:>8.4f} "
            f"{row['anomaly_f1']:>7.4f} | "
            f"{row['classifier_accuracy']:>7.4f} "
            f"{row['classifier_macro_f1']:>6.4f}"
        )


if __name__ == "__main__":
    main()