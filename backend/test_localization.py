import cv2

from app.services.defect_detection import (
    localize_defect
)


IMAGE_PATH = (
    "dataset/mvtec/bottle/test/"
    "broken_large/000.png"
)

REFERENCE_PATH = (
    "dataset/mvtec/bottle/train/good/"
    "000.png"
)


def main():

    image = cv2.imread(
        IMAGE_PATH
    )

    reference = cv2.imread(
        REFERENCE_PATH
    )

    if image is None:
        raise ValueError(
            "Could not read test image."
        )

    if reference is None:
        raise ValueError(
            "Could not read reference image."
        )

    # Make dimensions identical.
    image = cv2.resize(
        image,
        (256, 256)
    )

    reference = cv2.resize(
        reference,
        (256, 256)
    )

    result = localize_defect(
        image,
        reference
    )

    print()
    print("Defect Localization")
    print("===================")
    print(result)


if __name__ == "__main__":
    main()
