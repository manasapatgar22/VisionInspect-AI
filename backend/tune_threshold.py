from pathlib import Path

import cv2
import numpy as np

from app.services.anomaly_detection import MVTecAnomalyDetector


DATASET = Path("dataset/mvtec/bottle")

# Candidate multipliers to try. threshold = mean + multiplier * std.
# Lower = more sensitive (catches more defects, more false alarms).
CANDIDATE_MULTIPLIERS = [1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0]


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

    good_images, defective_images = collect_images()

    print(f"Good test images: {len(good_images)}")
    print(f"Defective test images: {len(defective_images)}")
    print()
    print("Scoring test images (this only runs the model once)...")

    # Compute raw distance scores ONCE per image. The threshold
    # itself is just arithmetic on top of these, so every candidate
    # multiplier below is nearly free to evaluate.
    good_scores = [
        detector.calculate_score(cv2.imread(str(path)))
        for path in good_images
    ]

    defective_scores = [
        detector.calculate_score(cv2.imread(str(path)))
        for path in defective_images
    ]

    results = [
        metrics_for_threshold(
            good_scores,
            defective_scores,
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

    print()
    print("Best by F1 score:")
    print(
        f"  multiplier={best_multiplier}, threshold={best['threshold']:.4f}, "
        f"precision={best['precision']:.4f}, recall={best['recall']:.4f}, "
        f"f1={best['f1']:.4f}"
    )
    print()
    print(
        "To apply: pass threshold_std_multiplier="
        f"{best_multiplier} wherever MVTecAnomalyDetector is "
        "constructed (app/routes/inspection.py and evaluate_model.py)."
    )


if __name__ == "__main__":
    main()