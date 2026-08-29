from pathlib import Path
from typing import Dict, List

import cv2
import numpy as np

from app.services.anomaly_detection import (
    MVTecAnomalyDetector
)


class DefectClassifier:
    """
    Baseline defect-type classifier.

    It creates a prototype feature for each defect class
    from labeled reference images and compares a new image
    against those prototypes.

    This is a classification baseline, not the final trained
    production classifier.
    """

    def __init__(
        self,
        detector: MVTecAnomalyDetector
    ):
        self.detector = detector
        self.prototypes: Dict[str, np.ndarray] = {}

    def build_prototypes(
        self,
        dataset_directory: str,
        max_images_per_class: int = 20
    ) -> Dict[str, int]:

        dataset_path = Path(
            dataset_directory
        )

        counts = {}

        for class_directory in sorted(
            dataset_path.iterdir()
        ):

            if not class_directory.is_dir():
                continue

            class_name = class_directory.name

            image_paths = list(
                class_directory.glob("*.png")
            )

            image_paths += list(
                class_directory.glob("*.jpg")
            )

            image_paths = image_paths[
                :max_images_per_class
            ]

            features: List[np.ndarray] = []

            for image_path in image_paths:

                image = cv2.imread(
                    str(image_path)
                )

                if image is None:
                    continue

                feature = (
                    self.detector.extract_features(
                        image
                    )
                )

                features.append(feature)

            if features:

                self.prototypes[class_name] = (
                    np.mean(
                        features,
                        axis=0
                    )
                )

                counts[class_name] = len(
                    features
                )

        return counts

    def predict(
        self,
        image: np.ndarray
    ) -> Dict:

        if not self.prototypes:
            raise ValueError(
                "Classifier prototypes have not been built."
            )

        feature = (
            self.detector.extract_features(
                image
            )
        )

        distances = {}

        for class_name, prototype in (
            self.prototypes.items()
        ):

            distances[class_name] = float(
                np.linalg.norm(
                    feature - prototype
                )
            )

        predicted_class = min(
            distances,
            key=distances.get
        )

        best_distance = distances[
            predicted_class
        ]

        # Convert relative distance into a simple
        # confidence-like value.
        all_distances = np.array(
            list(distances.values())
        )

        min_distance = np.min(
            all_distances
        )

        max_distance = np.max(
            all_distances
        )

        if max_distance == min_distance:
            confidence = 100.0
        else:
            confidence = (
                1
                - (
                    (best_distance - min_distance)
                    / (max_distance - min_distance)
                )
            ) * 100

        return {
            "defect_type": predicted_class,
            "confidence": round(
                float(confidence),
                2
            ),
            "distances": {
                key: round(
                    value,
                    4
                )
                for key, value in distances.items()
            }
        }
