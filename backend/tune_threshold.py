import argparse
from pathlib import Path
import random

import cv2
import numpy as np

from app.services.anomaly_detection import MVTecAnomalyDetector


DATASET_ROOT = Path("dataset/mvtec")

# Candidate multipliers to try. threshold = mean + multiplier * std.
# Lower = more sensitive (catches more defects, more false alarms).
CANDIDATE_MULTIPLIERS = [1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0]


def collect_images(DATASET, seed=42):
    """
    Collect MVTec test images and split them into:
    - validation images: used only for threshold tuning
    - test images: reserved for final evaluation
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

    rng = random.Random(seed)

    rng.shuffle(good_images)
    rng.shuffle(defective_images)

    good_split = len(good_images) // 2
    defective_split = len(defective_images) // 2

    validation_good = good_images[:good_split]
    test_good = good_images[good_split:]

    validation_defective = defective_images[:defective_split]
    test_defective = defective_images[defective_split:]

    return (
        validation_good,
        validation_defective,
        test_good,
        test_defective
    )
def metrics_for_threshold(good_scores, defective_scores, threshold):
    """
    Given raw scores (already computed once) and a candidate
    threshold, compute confusion-matrix metrics without touching
    the model again.
    """

    true_negative = sum(
        1 for score in good_scores if score < threshold
    )
    false_positive = sum(
        1 for score in good_scores if score >= threshold
    )

    true_positive = sum(
        1 for score in defective_scores if score >= threshold
    )
    false_negative = sum(
        1 for score in defective_scores if score < threshold
    )

    total = true_positive + true_negative + false_positive + false_negative

    accuracy = (
        (true_positive + true_negative) / total
        if total
        else 0
    )

    precision = (
        true_positive / (true_positive + false_positive)
        if (true_positive + false_positive)
        else 0
    )

    recall = (
        true_positive / (true_positive + false_negative)
        if (true_positive + false_negative)
        else 0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
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


def main():
    parser = argparse.ArgumentParser(
    description="Tune anomaly threshold for an MVTec category."
    )

    parser.add_argument(
    "--category",
    type=str,
    required=True,
    help="MVTec category, e.g. bottle, cable, capsule."
    )

    args = parser.parse_args()

    DATASET = DATASET_ROOT / args.category


    detector = MVTecAnomalyDetector(
    max_reference_images=209
    )

    reference_count = detector.build_reference(
        DATASET / "train" / "good"
    )

    print(f"Reference images: {reference_count}")

    mean_score = float(np.mean(detector.normal_scores))
    std_score = float(np.std(detector.normal_scores))

    print(f"Normal-score mean: {mean_score:.4f}")
    print(f"Normal-score std:  {std_score:.4f}")

    validation_good, validation_defective, test_good, test_defective = (
    collect_images(DATASET)
)

    print(f"Validation good images: {len(validation_good)}")
    print(f"Validation defective images: {len(validation_defective)}")
    print(f"Test good images: {len(test_good)}")
    print(f"Test defective images: {len(test_defective)}")
    print()
    print("Scoring test images (this only runs the model once)...")

    # Compute raw distance scores ONCE per image. The threshold
    # itself is just arithmetic on top of these, so every candidate
    # multiplier below is nearly free to evaluate.

    validation_good_scores = [
    detector.calculate_score(cv2.imread(str(path)))
    for path in validation_good
    ]

    validation_defective_scores = [
    detector.calculate_score(cv2.imread(str(path)))
    for path in validation_defective
    ]

    results = [
    metrics_for_threshold(
        validation_good_scores,
        validation_defective_scores,
        mean_score + multiplier * std_score
    )
    for multiplier in CANDIDATE_MULTIPLIERS
    ]

    print()
    print("Threshold Sweep")
    print("=" * 88)
    header = (
        f"{'multiplier':>10} | {'threshold':>10} | {'TP':>4} {'TN':>4} "
        f"{'FP':>4} {'FN':>4} | {'accuracy':>8} {'precision':>9} "
        f"{'recall':>7} {'f1':>6}"
    )
    print(header)
    print("-" * 88)

    for multiplier, result in zip(CANDIDATE_MULTIPLIERS, results):
        print(
            f"{multiplier:>10.2f} | {result['threshold']:>10.4f} | "
            f"{result['true_positive']:>4} {result['true_negative']:>4} "
            f"{result['false_positive']:>4} {result['false_negative']:>4} | "
            f"{result['accuracy']:>8.4f} {result['precision']:>9.4f} "
            f"{result['recall']:>7.4f} {result['f1']:>6.4f}"
        )

    best = max(results, key=lambda result: result["f1"])
    best_index = results.index(best)
    best_multiplier = CANDIDATE_MULTIPLIERS[best_index]

    selected_threshold = (
    mean_score + best_multiplier * std_score
    )

    test_good_scores = [
    detector.calculate_score(cv2.imread(str(path)))
    for path in test_good
    ]

    test_defective_scores = [
    detector.calculate_score(cv2.imread(str(path)))
    for path in test_defective
    ]

    test_result = metrics_for_threshold(
    test_good_scores,
    test_defective_scores,
    selected_threshold
    )

    print()
    print("Best multiplier selected on validation set:")
    print(
    f"  multiplier={best_multiplier}, threshold={selected_threshold:.4f}, "
    f"validation_precision={best['precision']:.4f}, "
    f"validation_recall={best['recall']:.4f}, "
    f"validation_f1={best['f1']:.4f}"
    )

    print()
    print("Final Test Evaluation")
    print("=====================")
    print(
    f"  threshold={test_result['threshold']:.4f}"
    )
    print(
    f"  accuracy={test_result['accuracy']:.4f}"
    )
    print(
    f"  precision={test_result['precision']:.4f}"
    )
    print(
    f"  recall={test_result['recall']:.4f}"
    )
    print(
    f"  f1={test_result['f1']:.4f}"
    )
    print()
    print(
        "To apply: pass threshold_std_multiplier="
        f"{best_multiplier} wherever MVTecAnomalyDetector is "
        "constructed (app/routes/inspection.py and evaluate_model.py)."
    )


if __name__ == "__main__":
    main()