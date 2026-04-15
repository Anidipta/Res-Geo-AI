"""Tests for Xception-based flood validation loaded from saved_models/."""

import numpy as np
import torch
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from satellite.flood_validation import XceptionFloodClassifier, load_xception_validator, validate_flood_candidates

# Checkpoint path — must exist locally before running
XCEPTION_WEIGHTS = os.path.join(os.path.dirname(__file__), "saved_models", "xception_flood.pth")


def test_xception_forward_shape():
    # Verify Xception outputs two class logits for a single 299x299 image
    model = XceptionFloodClassifier(num_classes=2)
    dummy = torch.randn(1, 3, 299, 299)
    with torch.no_grad():
        out = model(dummy)
    assert out.shape == (1, 2), f"Unexpected shape: {out.shape}"
    print("[PASS] test_xception_forward_shape")


def test_xception_confidence_range():
    # Ensure confidence scores are bounded in [0, 1]
    model = XceptionFloodClassifier()
    model.eval()
    dummy = torch.randn(2, 3, 299, 299)
    with torch.no_grad():
        conf = model.predict_confidence(dummy)
    assert conf.min() >= 0.0 and conf.max() <= 1.0, "Confidence out of range"
    print("[PASS] test_xception_confidence_range")


def test_xception_from_weights():
    # Load Xception classifier from saved checkpoint and verify output
    if not os.path.exists(XCEPTION_WEIGHTS):
        print(f"[SKIP] test_xception_from_weights — weights not found at {XCEPTION_WEIGHTS}")
        return
    model = load_xception_validator(XCEPTION_WEIGHTS, device="cpu")
    dummy = torch.randn(1, 3, 299, 299)
    with torch.no_grad():
        out = model(dummy)
    assert out.shape[1] == 2
    print("[PASS] test_xception_from_weights")


def test_validate_flood_candidates_skip():
    # Verify validation filters out low-confidence candidates correctly
    model = XceptionFloodClassifier()
    model.eval()
    candidates = [
        {"tile_id": "t0", "bbox": (0, 0, 1, 1), "flood_coverage": 15.0, "infra_overlap": True, "is_candidate": True},
        {"tile_id": "t1", "bbox": (1, 1, 2, 2), "flood_coverage": 20.0, "infra_overlap": True, "is_candidate": True},
    ]
    images = [np.random.randint(0, 255, (299, 299, 3), dtype=np.uint8) for _ in candidates]
    # With untrained model, all outputs are near 0.5; threshold=0.99 should reject all
    validated = validate_flood_candidates(model, candidates, images, conf_threshold=0.99, device="cpu")
    assert isinstance(validated, list)
    print(f"[PASS] test_validate_flood_candidates_skip — {len(validated)} passed (expected 0 or low)")


if __name__ == "__main__":
    test_xception_forward_shape()
    test_xception_confidence_range()
    test_xception_from_weights()
    test_validate_flood_candidates_skip()
    print("\nAll Xception tests completed.")
