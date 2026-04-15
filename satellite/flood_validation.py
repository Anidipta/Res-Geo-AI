"""Xception-based lightweight classifier for flood region validation."""

import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Tuple


class DepthwiseSeparableConv(nn.Module):
    # Depthwise separable convolution block as used in Xception
    def __init__(self, in_c: int, out_c: int, stride: int = 1):
        super().__init__()
        self.depthwise = nn.Conv2d(in_c, in_c, 3, stride=stride, padding=1, groups=in_c)
        self.pointwise = nn.Conv2d(in_c, out_c, 1)
        self.bn = nn.BatchNorm2d(out_c)
        self.relu = nn.ReLU()

    def forward(self, x):
        return self.relu(self.bn(self.pointwise(self.depthwise(x))))


class XceptionBlock(nn.Module):
    # Xception residual block with three depthwise separable convolutions
    def __init__(self, in_c: int, out_c: int, reps: int = 3, stride: int = 1):
        super().__init__()
        self.skip = nn.Sequential(
            nn.Conv2d(in_c, out_c, 1, stride=stride, bias=False),
            nn.BatchNorm2d(out_c)
        ) if in_c != out_c or stride != 1 else nn.Identity()
        layers = [DepthwiseSeparableConv(in_c if i == 0 else out_c, out_c) for i in range(reps)]
        if stride > 1:
            layers.append(nn.MaxPool2d(3, stride=stride, padding=1))
        self.sep_convs = nn.Sequential(*layers)

    def forward(self, x):
        return self.sep_convs(x) + self.skip(x)


class XceptionFloodClassifier(nn.Module):
    # Lightweight Xception classifier outputting flood confidence score
    def __init__(self, num_classes: int = 2):
        super().__init__()
        self.entry = nn.Sequential(
            nn.Conv2d(3, 32, 3, stride=2, padding=1), nn.BatchNorm2d(32), nn.ReLU(),
            nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(),
        )
        self.middle = nn.Sequential(
            XceptionBlock(64, 128, stride=2),
            XceptionBlock(128, 256, stride=2),
            XceptionBlock(256, 728, stride=2),
            *[XceptionBlock(728, 728) for _ in range(8)],
            XceptionBlock(728, 1024, stride=2),
        )
        self.exit_flow = nn.Sequential(
            DepthwiseSeparableConv(1024, 1536),
            DepthwiseSeparableConv(1536, 2048),
            nn.AdaptiveAvgPool2d(1),
        )
        self.classifier = nn.Linear(2048, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Forward pass returning class logits
        x = self.entry(x)
        x = self.middle(x)
        x = self.exit_flow(x)
        x = x.flatten(1)
        return self.classifier(x)

    def predict_confidence(self, x: torch.Tensor) -> torch.Tensor:
        # Return flood confidence probability via sigmoid on flood logit
        logits = self.forward(x)
        return torch.sigmoid(logits[:, 1])


def load_xception_validator(weights_path: str, device: str = "cpu") -> XceptionFloodClassifier:
    # Load Xception classifier from checkpoint path
    model = XceptionFloodClassifier()
    state = torch.load(weights_path, map_location=device)
    model.load_state_dict(state)
    model.eval()
    return model.to(device)


def validate_flood_candidates(
    model: XceptionFloodClassifier,
    candidates: List[Dict],
    tile_images: List[np.ndarray],
    conf_threshold: float = 0.7,
    device: str = "cpu"
) -> List[Dict]:
    # Score each candidate tile and keep those above confidence threshold
    import torch
    import cv2
    validated = []
    for cand, img in zip(candidates, tile_images):
        img_resized = cv2.resize(img, (299, 299)).astype(np.float32) / 255.0
        tensor = torch.from_numpy(img_resized.transpose(2, 0, 1)).unsqueeze(0).to(device)
        with torch.no_grad():
            conf = model.predict_confidence(tensor).item()
        cand["validation_score"] = conf
        cand["validated"] = conf > conf_threshold
        if cand["validated"]:
            validated.append(cand)
    return validated
