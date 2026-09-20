import cv2
import glob
import os

from app.services.localization import get_defect_bounding_box
from app.services.defect_detection import (
    localize_defect_multi_reference
)


DATASET_ROOT = "dataset/mvtec"

CATEGORIES = [
    "bottle",
    "cable",
    "capsule",
    "carpet",
    "grid",
    "hazelnut",
    "leather",
    "metal_nut",
    "pill",
    "screw",
    "tile",
    "toothbrush",
    "transistor",
    "wood",
    "zipper",
]


def calculate_iou(box1, box2):

    x1 = max(box1["x"], box2["x"])
    y1 = max(box1["y"], box2["y"])

    x2 = min(
        box1["x"] + box1["width"],
        box2["x"] + box2["width"]
    )

    y2 = min(
        box1["y"] + box1["height"],
        box2["y"] + box2["height"]
    )

    intersection = (
        max(0, x2 - x1) *
        max(0, y2 - y1)
    )

    area1 = box1["width"] * box1["height"]
    area2 = box2["width"] * box2["height"]

    union = area1 + area2 - intersection

    if union == 0:
        return 0.0

    return intersection / union


def main():

    results = []

    for category in CATEGORIES:

        category_path = os.path.join(
            DATASET_ROOT,
            category
        )

        good_images = glob.glob(
            os.path.join(
                category_path,
                "train",
                "good",
                "*.png"
            )
        )

        if not good_images:
            print(category, "SKIPPED - no reference images")
            continue

        reference_paths = good_images[:20]

        references = [
        cv2.imread(path)
        for path in reference_paths
    ]

        references = [
        ref for ref in references
        if ref is not None
    ]

        if not references:
            print(category, "SKIPPED - reference unreadable")
            continue

        total_iou = 0.0
        evaluated = 0

        test_path = os.path.join(
            category_path,
            "test"
        )

        defect_types = [
            d for d in os.listdir(test_path)
            if d != "good"
            and os.path.isdir(
                os.path.join(test_path, d)
            )
        ]

        for defect_type in defect_types:

            image_paths = glob.glob(
                os.path.join(
                    test_path,
                    defect_type,
                    "*.png"
                )
            )

            # First 3 images per defect type.
            image_paths = image_paths[:3]

            for image_path in image_paths:

                filename = os.path.basename(
                    image_path
                )

                image = cv2.imread(
                    image_path
                )

                if image is None:
                    continue

                image = cv2.resize(
                    image,
                    (256, 256)
                )

                

                from app.services.defect_detection import (
                localize_defect_multi_reference
                )

                resized_references = [
                cv2.resize(
                ref,
                (256, 256)
                )
                for ref in references
                ]

                predicted = localize_defect_multi_reference(
                image,
                resized_references
                )

                mask_path = os.path.join(
                    category_path,
                    "ground_truth",
                    defect_type,
                    filename.replace(
                        ".png",
                        "_mask.png"
                    )
                )

                mask = cv2.imread(
                    mask_path,
                    cv2.IMREAD_GRAYSCALE
                )

                if mask is None:
                    continue

                mask = cv2.resize(
                    mask,
                    (256, 256),
                    interpolation=cv2.INTER_NEAREST
                )

                ground_truth = get_defect_bounding_box(
                    mask
                )

                if (
                    predicted["detected"]
                    and ground_truth["detected"]
                ):

                    iou = calculate_iou(
                        predicted["bounding_box"],
                        ground_truth
                    )

                    total_iou += iou
                    evaluated += 1

        mean_iou = (
            total_iou / evaluated
            if evaluated > 0
            else 0.0
        )

        results.append(
            (category, evaluated, mean_iou)
        )

    print()
    print("=" * 60)
    print("15-CATEGORY LOCALIZATION EVALUATION")
    print("=" * 60)

    total_iou = 0.0
    total_images = 0

    for category, count, mean_iou in results:

        print(
            f"{category:12} "
            f"images={count:3} "
            f"mean IoU={mean_iou:.3f}"
        )

        total_iou += mean_iou * count
        total_images += count

    overall_iou = (
        total_iou / total_images
        if total_images > 0
        else 0.0
    )

    print("-" * 60)
    print(
        f"Overall Mean IoU = {overall_iou:.3f}"
    )
    print(
        f"Total images evaluated = {total_images}"
    )


if __name__ == "__main__":
    main()