from pathlib import Path
from collections import defaultdict
import random

import cv2
import numpy as np

from app.services.anomaly_detection import MVTecAnomalyDetector
from app.services.defect_classifier import DefectClassifier


# ============================================================
# CONFIGURATION
# ============================================================

DATASET_ROOT = Path("dataset/mvtec")

# Threshold candidates.
# threshold = mean(normal reference scores)
#           + multiplier * std(normal reference scores)
CANDIDATE_MULTIPLIERS = [
    1.5,
    1.75,
    2.0,
    2.25,
    2.5,
    2.75,
    3.0,
]

# Validation / final-test split
VALIDATION_RATIO = 0.70
FINAL_TEST_RATIO = 0.30

# Classification support/query split
SUPPORT_RATIO = 0.70
QUERY_RATIO = 0.30

# Reproducibility
RANDOM_SEED = 42

# Maximum number of reference images used by anomaly detector
MAX_REFERENCE_IMAGES = 200


# ============================================================
# CATEGORY DISCOVERY
# ============================================================

def get_available_categories():
    """
    Return all MVTec category folders available on disk.
    """

    if not DATASET_ROOT.exists():
        return []

    return sorted([
        p.name
        for p in DATASET_ROOT.iterdir()
        if p.is_dir()
    ])


# ============================================================
# IMAGE COLLECTION
# ============================================================

def get_class_images(class_directory):
    """
    Return sorted PNG images from a class directory.
    """

    return sorted(class_directory.glob("*.png"))


def collect_test_images(test_directory):
    """
    Collect all images from the category test directory.

    Returns:
        dictionary:
            {
                "good": [...],
                "defect_class_1": [...],
                ...
            }
    """

    class_images = {}

    if not test_directory.exists():
        return class_images

    for directory in sorted(test_directory.iterdir()):

        if not directory.is_dir():
            continue

        images = get_class_images(directory)

        if images:
            class_images[directory.name] = images

    return class_images


# ============================================================
# REPRODUCIBLE SPLIT
# ============================================================

def split_images(images, ratio=0.70, seed=42):
    """
    Reproducibly split images into two sets.

    Returns:
        first_set, second_set
    """

    images = list(images)

    rng = random.Random(seed)
    rng.shuffle(images)

    if len(images) < 2:
        return images, []

    split_index = int(len(images) * ratio)

    # Make sure neither side is empty when possible
    split_index = max(1, min(split_index, len(images) - 1))

    first_set = images[:split_index]
    second_set = images[split_index:]

    return first_set, second_set


def split_category_test_data(class_images, seed=42):
    """
    Split every class independently into:

        validation
        final_test

    This preserves representation of every defect class.
    """

    validation = {}
    final_test = {}

    for class_name in sorted(class_images.keys()):

        images = class_images[class_name]

        class_seed = seed + sum(ord(c) for c in class_name)

        validation_images, final_test_images = split_images(
            images,
            ratio=VALIDATION_RATIO,
            seed=class_seed
        )

        validation[class_name] = validation_images
        final_test[class_name] = final_test_images

    return validation, final_test


# ============================================================
# METRICS
# ============================================================

def metrics_for_threshold(
    good_scores,
    defective_scores,
    threshold
):
    """
    Calculate binary anomaly-detection metrics.
    """

    true_negative = sum(
        1 for score in good_scores
        if score < threshold
    )

    false_positive = sum(
        1 for score in good_scores
        if score >= threshold
    )

    true_positive = sum(
        1 for score in defective_scores
        if score >= threshold
    )

    false_negative = sum(
        1 for score in defective_scores
        if score < threshold
    )

    total = (
        true_positive
        + true_negative
        + false_positive
        + false_negative
    )

    accuracy = (
        (true_positive + true_negative) / total
        if total
        else 0
    )

    precision = (
        true_positive /
        (true_positive + false_positive)
        if (true_positive + false_positive)
        else 0
    )

    recall = (
        true_positive /
        (true_positive + false_negative)
        if (true_positive + false_negative)
        else 0
    )

    f1 = (
        2 * precision * recall /
        (precision + recall)
        if (precision + recall)
        else 0
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


# ============================================================
# SCORE IMAGES
# ============================================================

def calculate_scores(detector, image_paths):
    """
    Calculate anomaly scores for a list of images.
    """

    scores = []

    for image_path in image_paths:

        image = cv2.imread(str(image_path))

        if image is None:
            continue

        score = detector.calculate_score(image)

        scores.append(float(score))

    return scores


def flatten_class_images(class_images):
    """
    Flatten:

        {
            class1: [images],
            class2: [images]
        }

    into one list.
    """

    images = []

    for paths in class_images.values():
        images.extend(paths)

    return images


# ============================================================
# ANOMALY DETECTION
# ============================================================

def evaluate_anomaly_detection_holdout(category):
    """
    Proper anomaly-detection evaluation.

    1. Build reference using train/good.
    2. Split test images into validation/final test.
    3. Select threshold ONLY on validation data.
    4. Evaluate selected threshold ONLY on final test data.
    """

    train_directory = (
        DATASET_ROOT
        / category
        / "train"
        / "good"
    )

    test_directory = (
        DATASET_ROOT
        / category
        / "test"
    )

    if not train_directory.exists():
        print("  Missing train/good directory.")
        return None

    if not test_directory.exists():
        print("  Missing test directory.")
        return None

    # --------------------------------------------------------
    # Build normal reference
    # --------------------------------------------------------

    detector = MVTecAnomalyDetector(
        max_reference_images=MAX_REFERENCE_IMAGES
    )

    detector.build_reference(train_directory)

    if not detector.normal_scores:

        print("  Could not build normal reference.")
        return None

    mean_score = float(
        np.mean(detector.normal_scores)
    )

    std_score = float(
        np.std(detector.normal_scores)
    )

    # --------------------------------------------------------
    # Collect test images
    # --------------------------------------------------------

    class_images = collect_test_images(test_directory)

    if "good" not in class_images:

        print("  No good test images.")
        return None

    defect_classes = [
        class_name
        for class_name in class_images
        if class_name != "good"
    ]

    if not defect_classes:

        print("  No defective test images.")
        return None

    # --------------------------------------------------------
    # Split test → validation + final test
    # --------------------------------------------------------

    validation_data, final_test_data = (
        split_category_test_data(
            class_images,
            seed=RANDOM_SEED
        )
    )

    # --------------------------------------------------------
    # VALIDATION SCORES
    # --------------------------------------------------------

    validation_good_scores = calculate_scores(
        detector,
        validation_data["good"]
    )

    validation_defective_paths = []

    for defect_class in defect_classes:
        validation_defective_paths.extend(
            validation_data[defect_class]
        )

    validation_defective_scores = calculate_scores(
        detector,
        validation_defective_paths
    )

    if (
        not validation_good_scores
        or not validation_defective_scores
    ):
        print("  Validation split does not contain enough images.")
        return None

    # --------------------------------------------------------
    # THRESHOLD SELECTION
    # --------------------------------------------------------

    validation_results = []

    for multiplier in CANDIDATE_MULTIPLIERS:

        threshold = (
            mean_score
            + multiplier * std_score
        )

        result = metrics_for_threshold(
            validation_good_scores,
            validation_defective_scores,
            threshold
        )

        result["multiplier"] = multiplier

        validation_results.append(result)

    best_validation = max(
        validation_results,
        key=lambda result: result["f1"]
    )

    selected_multiplier = (
        best_validation["multiplier"]
    )

    selected_threshold = (
        best_validation["threshold"]
    )

    # --------------------------------------------------------
    # FINAL TEST SCORES
    # --------------------------------------------------------

    final_good_scores = calculate_scores(
        detector,
        final_test_data["good"]
    )

    final_defective_paths = []

    for defect_class in defect_classes:
        final_defective_paths.extend(
            final_test_data[defect_class]
        )

    final_defective_scores = calculate_scores(
        detector,
        final_defective_paths
    )

    if (
        not final_good_scores
        or not final_defective_scores
    ):
        print("  Final test split does not contain enough images.")
        return None

    final_result = metrics_for_threshold(
        final_good_scores,
        final_defective_scores,
        selected_threshold
    )

    return {
        "detector": detector,

        "mean_score": mean_score,
        "std_score": std_score,

        "best_multiplier": selected_multiplier,
        "threshold": selected_threshold,

        "validation_result": best_validation,
        "final_result": final_result,

        "validation_good_count": len(
            validation_data["good"]
        ),

        "validation_defective_count": len(
            validation_defective_paths
        ),

        "final_good_count": len(
            final_test_data["good"]
        ),

        "final_defective_count": len(
            final_defective_paths
        ),
    }


# ============================================================
# CLASSIFICATION
# ============================================================

def evaluate_classifier_holdout(
    category,
    detector
):
    """
    Proper support/query evaluation.

    For every defect class:

        70% support → build prototype
        30% query   → evaluate

    Query images are never used to build prototypes.
    """

    test_directory = (
        DATASET_ROOT
        / category
        / "test"
    )

    class_images = collect_test_images(
        test_directory
    )

    if not class_images:
        return None

    # --------------------------------------------------------
    # Split each class into support/query
    # --------------------------------------------------------

    support_data = {}
    query_data = {}

    for class_name in sorted(class_images.keys()):

        images = class_images[class_name]

        class_seed = (
            RANDOM_SEED
            + 1000
            + sum(ord(c) for c in class_name)
        )

        support_images, query_images = split_images(
            images,
            ratio=SUPPORT_RATIO,
            seed=class_seed
        )

        support_data[class_name] = support_images
        query_data[class_name] = query_images

    # --------------------------------------------------------
    # IMPORTANT
    #
    # DefectClassifier expects a directory structure.
    #
    # Instead of modifying your existing classifier class,
    # we construct prototypes directly using its detector.
    # --------------------------------------------------------

    classifier = DefectClassifier(detector)

    # --------------------------------------------------------
    # Build prototypes from SUPPORT images only
    # --------------------------------------------------------

    prototypes = {}

    for class_name in sorted(support_data.keys()):

        support_images = support_data[class_name]

        if not support_images:
            continue

        features = []

        for image_path in support_images:

            image = cv2.imread(str(image_path))

            if image is None:
                continue

            try:
                feature = detector.extract_features(
                    image
                )
            except AttributeError:
                # If your detector exposes feature extraction
                # differently, use the classifier's helper.
                feature = classifier.extract_features(
                    image
                )

            if feature is not None:
                features.append(
                    np.asarray(feature)
                )

        if not features:
            continue

        prototypes[class_name] = np.mean(
            np.stack(features),
            axis=0
        )

    if not prototypes:
        print("  Could not build classification prototypes.")
        return None

    # --------------------------------------------------------
    # QUERY EVALUATION
    # --------------------------------------------------------

    confusion = defaultdict(
        lambda: defaultdict(int)
    )

    total = 0
    correct = 0

    for actual_class in sorted(query_data.keys()):

        for image_path in query_data[actual_class]:

            image = cv2.imread(
                str(image_path)
            )

            if image is None:
                continue

            try:
                feature = detector.extract_features(
                    image
                )
            except AttributeError:
                feature = classifier.extract_features(
                    image
                )

            if feature is None:
                continue

            feature = np.asarray(feature)

            # ------------------------------------------------
            # Nearest prototype
            # ------------------------------------------------

            distances = {}

            for class_name, prototype in prototypes.items():

                distance = np.linalg.norm(
                    feature - prototype
                )

                distances[class_name] = distance

            predicted_class = min(
                distances,
                key=distances.get
            )

            confusion[actual_class][
                predicted_class
            ] += 1

            total += 1

            if predicted_class == actual_class:
                correct += 1

    accuracy = (
        correct / total
        if total
        else 0
    )

    # --------------------------------------------------------
    # Macro F1
    # --------------------------------------------------------

    classes = sorted(
        set(confusion.keys())
        | {
            predicted
            for actual in confusion
            for predicted in confusion[actual]
        }
    )

    all_f1 = []

    for class_name in classes:

        true_positive = (
            confusion[class_name][class_name]
        )

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
            if (
                true_positive
                + false_positive
            )
            else 0
        )

        recall = (
            true_positive /
            (true_positive + false_negative)
            if (
                true_positive
                + false_negative
            )
            else 0
        )

        f1 = (
            2 * precision * recall /
            (precision + recall)
            if precision + recall
            else 0
        )

        all_f1.append(f1)

    macro_f1 = (
        sum(all_f1) / len(all_f1)
        if all_f1
        else 0
    )

    return {
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "total": total,
        "correct": correct,
        "confusion": confusion,

        "support_counts": {
            class_name: len(images)
            for class_name, images
            in support_data.items()
        },

        "query_counts": {
            class_name: len(images)
            for class_name, images
            in query_data.items()
        },
    }


# ============================================================
# MAIN
# ============================================================

def main():

    categories = get_available_categories()

    if not categories:

        print(
            "No MVTec categories found under "
            "dataset/mvtec/"
        )

        return

    print("=" * 110)
    print("MVTec 15-Category Held-Out Evaluation")
    print("=" * 110)

    print(
        f"Found {len(categories)} categories:"
    )

    print(
        ", ".join(categories)
    )

    print()

    print(
        f"Validation ratio: {VALIDATION_RATIO:.0%}"
    )

    print(
        f"Final test ratio: {FINAL_TEST_RATIO:.0%}"
    )

    print(
        f"Classification support ratio: "
        f"{SUPPORT_RATIO:.0%}"
    )

    print(
        f"Classification query ratio: "
        f"{QUERY_RATIO:.0%}"
    )

    print(
        f"Random seed: {RANDOM_SEED}"
    )

    print()

    summary_rows = []

    # ========================================================
    # PROCESS EVERY CATEGORY
    # ========================================================

    for category in categories:

        print("=" * 110)
        print(
            f"Category: {category}"
        )
        print("=" * 110)

        # ----------------------------------------------------
        # ANOMALY DETECTION
        # ----------------------------------------------------

        anomaly_result = (
            evaluate_anomaly_detection_holdout(
                category
            )
        )

        if anomaly_result is None:

            print(
                "  Anomaly detection skipped."
            )

            print()

            continue

        validation = (
            anomaly_result[
                "validation_result"
            ]
        )

        final = (
            anomaly_result[
                "final_result"
            ]
        )

        print()
        print(
            "  Threshold selection "
            "(VALIDATION SET):"
        )

        print(
            f"    best multiplier = "
            f"{anomaly_result['best_multiplier']:.2f}"
        )

        print(
            f"    threshold = "
            f"{anomaly_result['threshold']:.6f}"
        )

        print(
            f"    validation accuracy = "
            f"{validation['accuracy']:.4f}"
        )

        print(
            f"    validation precision = "
            f"{validation['precision']:.4f}"
        )

        print(
            f"    validation recall = "
            f"{validation['recall']:.4f}"
        )

        print(
            f"    validation F1 = "
            f"{validation['f1']:.4f}"
        )

        print()
        print(
            "  FINAL anomaly detection "
            "(UNTOUCHED TEST SET):"
        )

        print(
            f"    accuracy = "
            f"{final['accuracy']:.4f}"
        )

        print(
            f"    precision = "
            f"{final['precision']:.4f}"
        )

        print(
            f"    recall = "
            f"{final['recall']:.4f}"
        )

        print(
            f"    F1 = "
            f"{final['f1']:.4f}"
        )

        print(
            f"    TP={final['true_positive']} "
            f"TN={final['true_negative']} "
            f"FP={final['false_positive']} "
            f"FN={final['false_negative']}"
        )

        print(
            f"    final good images = "
            f"{anomaly_result['final_good_count']}"
        )

        print(
            f"    final defective images = "
            f"{anomaly_result['final_defective_count']}"
        )

        # ----------------------------------------------------
        # CLASSIFICATION
        # ----------------------------------------------------

        classifier_result = (
            evaluate_classifier_holdout(
                category,
                anomaly_result["detector"]
            )
        )

        if classifier_result is None:

            print()
            print(
                "  Classification skipped."
            )

            continue

        print()
        print(
            "  FINAL defect classification "
            "(SUPPORT → QUERY):"
        )

        print(
            f"    accuracy = "
            f"{classifier_result['accuracy']:.4f}"
        )

        print(
            f"    macro F1 = "
            f"{classifier_result['macro_f1']:.4f}"
        )

        print(
            f"    correct = "
            f"{classifier_result['correct']}/"
            f"{classifier_result['total']}"
        )

        print()
        print("    Support images:")

        for class_name in sorted(
            classifier_result["support_counts"]
        ):

            print(
                f"      {class_name:<25} "
                f"{classifier_result['support_counts'][class_name]}"
            )

        print()
        print("    Query images:")

        for class_name in sorted(
            classifier_result["query_counts"]
        ):

            print(
                f"      {class_name:<25} "
                f"{classifier_result['query_counts'][class_name]}"
            )

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        summary_rows.append({

            "category": category,

            "threshold_multiplier":
                anomaly_result[
                    "best_multiplier"
                ],

            "threshold":
                anomaly_result[
                    "threshold"
                ],

            "validation_f1":
                validation[
                    "f1"
                ],

            "anomaly_accuracy":
                final[
                    "accuracy"
                ],

            "anomaly_precision":
                final[
                    "precision"
                ],

            "anomaly_recall":
                final[
                    "recall"
                ],

            "anomaly_f1":
                final[
                    "f1"
                ],

            "classification_accuracy":
                classifier_result[
                    "accuracy"
                ],

            "classification_macro_f1":
                classifier_result[
                    "macro_f1"
                ],
        })

        print()

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    if not summary_rows:

        print(
            "No categories produced results."
        )

        return

    print()
    print("=" * 110)
    print(
        "FINAL HOLD-OUT SUMMARY"
    )
    print("=" * 110)

    print(
        f"{'category':<15} "
        f"{'mult':>5} | "
        f"{'anom_acc':>8} "
        f"{'anom_prec':>9} "
        f"{'anom_rec':>8} "
        f"{'anom_f1':>8} | "
        f"{'cls_acc':>8} "
        f"{'cls_f1':>8}"
    )

    print("-" * 110)

    for row in summary_rows:

        print(
            f"{row['category']:<15} "
            f"{row['threshold_multiplier']:>5.2f} | "
            f"{row['anomaly_accuracy']:>8.4f} "
            f"{row['anomaly_precision']:>9.4f} "
            f"{row['anomaly_recall']:>8.4f} "
            f"{row['anomaly_f1']:>8.4f} | "
            f"{row['classification_accuracy']:>8.4f} "
            f"{row['classification_macro_f1']:>8.4f}"
        )

    # ========================================================
    # MACRO AVERAGES ACROSS CATEGORIES
    # ========================================================

    anomaly_accuracy = np.mean([
        row["anomaly_accuracy"]
        for row in summary_rows
    ])

    anomaly_precision = np.mean([
        row["anomaly_precision"]
        for row in summary_rows
    ])

    anomaly_recall = np.mean([
        row["anomaly_recall"]
        for row in summary_rows
    ])

    anomaly_f1 = np.mean([
        row["anomaly_f1"]
        for row in summary_rows
    ])

    classification_accuracy = np.mean([
        row["classification_accuracy"]
        for row in summary_rows
    ])

    classification_f1 = np.mean([
        row["classification_macro_f1"]
        for row in summary_rows
    ])

    print("-" * 110)

    print(
        f"{'MACRO AVG':<15} "
        f"{'':>5} | "
        f"{anomaly_accuracy:>8.4f} "
        f"{anomaly_precision:>9.4f} "
        f"{anomaly_recall:>8.4f} "
        f"{anomaly_f1:>8.4f} | "
        f"{classification_accuracy:>8.4f} "
        f"{classification_f1:>8.4f}"
    )

    print()
    print("=" * 110)
    print(
        "Evaluation completed."
    )
    print("=" * 110)

    print()
    print(
        "IMPORTANT:"
    )

    print(
        "• Thresholds were selected using validation data."
    )

    print(
        "• Final anomaly metrics were calculated on "
        "a separate test split."
    )

    print(
        "• Classification prototypes were built "
        "using support images only."
    )

    print(
        "• Classification metrics were calculated "
        "using separate query images."
    )

    print(
        "• Random seed is fixed at 42 for reproducibility."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()