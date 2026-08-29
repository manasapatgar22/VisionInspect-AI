import cv2

from app.services.anomaly_detection import (
    MVTecAnomalyDetector
)

from app.services.defect_classifier import (
    DefectClassifier
)


DATASET = "dataset/mvtec/bottle/test"


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

    counts = classifier.build_prototypes(
        DATASET,
        max_images_per_class=20
    )

    print("Prototype classes:")
    print(counts)

    image_path = (
        "dataset/mvtec/bottle/test/"
        "broken_large/000.png"
    )

    image = cv2.imread(
        image_path
    )

    if image is None:
        raise ValueError(
            f"Could not read {image_path}"
        )

    result = classifier.predict(
        image
    )

    print()
    print("Classification result:")
    print(result)


if __name__ == "__main__":
    main()
