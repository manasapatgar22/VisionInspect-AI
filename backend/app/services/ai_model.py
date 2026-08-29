import torch
import torch.nn as nn
from torchvision import models


class FeatureExtractor(nn.Module):
    """
    Pretrained ResNet18 used as a feature extractor.
    """

    def __init__(self):
        super().__init__()

        weights = models.ResNet18_Weights.DEFAULT

        model = models.resnet18(weights=weights)

        self.features = nn.Sequential(
            *list(model.children())[:-1]
        )

        self.features.eval()

        for parameter in self.features.parameters():
            parameter.requires_grad = False

    def forward(self, x):
        with torch.no_grad():
            features = self.features(x)

        return features.flatten(1)


def create_model():
    """
    Create the pretrained feature-extraction model.
    """

    model = FeatureExtractor()

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    model = model.to(device)

    return model, device
