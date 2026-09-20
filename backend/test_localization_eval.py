import cv2
import glob
import os

from app.services.localization import get_defect_bounding_box
from app.services.defect_detection import localize_defect


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

    intersection_width = max(0, x2 - x1)
    intersection_height = max(0, y2 - y1)

    intersection = (
        intersection_width *
        intersection_height
    )

    area1 = box1["width"] * box1["height"]
    area2 = box2["width"] * box2["height"]

    union = area1 + area2 - intersection

    if union == 0:
        return 0.0

    return intersection / union


def main():

    reference = cv2.imread(
        "dataset/mvtec/bottle/train/good/050.png"
    )

    total_iou = 0.0
    count = 0

    for defect_type in [
        "broken_large",
        "broken_small",
        "contamination"
    ]:

        image_paths = glob.glob(
            f"dataset/mvtec/bottle/test/{defect_type}/*.png"
        )[:3]

        print()
        print(defect_type)
        print("-" * 40)

        for image_path in image_paths:

            filename = os.path.basename(
                image_path
            )

            image = cv2.imread(
                image_path
            )

            image = cv2.resize(
                image,
                (256, 256)
            )

            ref = cv2.resize(
                reference,
                (256, 256)
            )

            predicted = localize_defect(
                image,
                ref
            )

            mask_path = (
                "dataset/mvtec/bottle/"
                f"ground_truth/{defect_type}/"
                f"{filename.replace('.png', '_mask.png')}"
            )

            mask = cv2.imread(
                mask_path,
                cv2.IMREAD_GRAYSCALE
            )

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
                count += 1

                print(
                    filename,
                    "IoU =",
                    round(iou, 3)
                )

            else:
                print(
                    filename,
                    "Localization failed"
                )

    if count > 0:

        print()
        print("=" * 40)
        print(
            "Mean IoU =",
            round(total_iou / count, 3)
        )
        print(
            "Images evaluated =",
            count
        )


if __name__ == "__main__":
    main()