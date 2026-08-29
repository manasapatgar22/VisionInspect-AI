from pathlib import Path

import cv2
import numpy as np
import torch
from torchvision import models, transforms


class MVTecAnomalyDetector:

    def __init__(self, max_reference_images=20):

        weights = models.ResNet18_Weights.DEFAULT

        backbone = models.resnet18(weights=weights)

        self.model = torch.nn.Sequential(
            *list(backbone.children())[:-1]
        )

        self.model.eval()

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        self.model = self.model.to(self.device)

        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

        self.reference_features = []
        self.normal_scores = []
        self.threshold = None

        self.max_reference_images = max_reference_images

    def extract_features(self, image):

        image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )

        tensor = self.transform(image)
        tensor = tensor.unsqueeze(0).to(self.device)

        with torch.no_grad():
            features = self.model(tensor)

        return features.flatten().cpu().numpy()

    def build_reference(self, directory):

        directory = Path(directory)

        image_paths = list(
            directory.glob("*.png")
        )

        image_paths += list(
            directory.glob("*.jpg")
        )

        image_paths = image_paths[
            :self.max_reference_images
        ]

        if not image_paths:
            raise ValueError(
                f"No images found in {directory}"
            )

        self.reference_features = []

        for image_path in image_paths:

            image = cv2.imread(
                str(image_path)
            )

            if image is None:
                continue

            features = self.extract_features(
                image
            )

            self.reference_features.append(
                features
            )

        if not self.reference_features:
            raise ValueError(
                "Could not extract reference features."
            )

        # Calculate normal-image scores.
        self.normal_scores = []

        for features in self.reference_features:

            distances = [
                np.linalg.norm(
                    features - reference
                )
                for reference in self.reference_features
            ]

            # Exclude self-distance.
            distances = [
                value
                for value in distances
                if value > 0
            ]

            if distances:
                self.normal_scores.append(
                    float(np.mean(distances))
                )

        if self.normal_scores:

            mean_score = np.mean(
                self.normal_scores
            )

            std_score = np.std(
                self.normal_scores
            )

            # Data-driven threshold.
            self.threshold = float(
                mean_score + 3 * std_score
            )

        return len(self.reference_features)

    def calculate_score(self, image):

        if not self.reference_features:
            raise ValueError(
                "Reference features have not been built."
            )

        features = self.extract_features(
            image
        )

        distances = [
            np.linalg.norm(
                features - reference
            )
            for reference in self.reference_features
        ]

        return float(
            np.mean(distances)
        )

    def is_anomaly(self, score):

        if self.threshold is None:
            raise ValueError(
                "Anomaly threshold has not been calculated."
            )

        return score >= self.threshold
