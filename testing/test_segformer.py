"""Tests for SegFormer flood detection model loaded from saved_models/."""

import numpy as np
import torch
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from satellite.segformer import ModifiedSegFormer, load_segformer
from satellite.flood_detection import (
    preprocess_tile, compute_flood_coverage,
    detect_infrastructure_overlap, run_flood_detection_on_tile
)

# Path to pretrained weights — must exist locally before running
SEGFORMER_WEIGHTS = os.path.join(os.path.dirname(__file__), "saved_models", "segformer_flood.pth")


def test_segformer_forward_pass():
    # Verify SegFormer produces correct output shape on dummy input
    model = ModifiedSegFormer(num_classes=7)
    dummy = torch.randn(1, 3, 256, 256)
    with torch.no_grad():
        out = model(dummy)
    assert out.shape == (1, 7, 256, 256), f"Unexpected shape: {out.shape}"
    print("[PASS] test_segformer_forward_pass")


def test_segformer_from_weights():
    # Load SegFormer from saved checkpoint and run a forward pass
    if not os.path.exists(SEGFORMER_WEIGHTS):
        print(f"[SKIP] test_segformer_from_weights — weights not found at {SEGFORMER_WEIGHTS}")
        return
    model = load_segformer(SEGFORMER_WEIGHTS, num_classes=7, device="cpu")
    dummy = torch.randn(1, 3, 512, 512)
    with torch.no_grad():
        out = model(dummy)
    assert out.shape[1] == 7, "Wrong number of output classes"
    print("[PASS] test_segformer_from_weights")


def test_preprocess_tile():
    # Ensure preprocessing normalizes and resizes tile correctly
    img = np.random.randint(0, 255, (800, 800, 3), dtype=np.uint8)
    tensor = preprocess_tile(img, target_size=512)
    assert tensor.shape == (1, 3, 512, 512), f"Unexpected tensor shape: {tensor.shape}"
    print("[PASS] test_preprocess_tile")


def test_compute_flood_coverage():
    # Verify coverage calculation at known thresholds
    prob_map = np.zeros((100, 100), dtype=np.float32)
    prob_map[:50, :50] = 0.9  # 25% flooded
    coverage = compute_flood_coverage(prob_map, threshold=0.5)
    assert abs(coverage - 25.0) < 0.5, f"Coverage error: {coverage}"
    print("[PASS] test_compute_flood_coverage")


def test_infrastructure_overlap_detection():
    # Check overlap detection between flood mask and infra classes
    flood_mask = np.zeros((100, 100), dtype=bool)
    flood_mask[20:60, 20:60] = True
    seg_map = np.zeros((100, 100), dtype=int)
    seg_map[30:50, 30:50] = 1  # Building inside flood zone
    assert detect_infrastructure_overlap(flood_mask, seg_map) is True
    seg_map_clear = np.zeros((100, 100), dtype=int)
    assert detect_infrastructure_overlap(flood_mask, seg_map_clear) is False
    print("[PASS] test_infrastructure_overlap_detection")


def test_flood_detection_on_tile():
    # End-to-end tile detection with untrained model on random input
    model = ModifiedSegFormer(num_classes=7)
    model.eval()
    img = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
    meta = {"id": "tile_0_0", "bbox": (0.0, 0.0, 1.0, 1.0)}
    result = run_flood_detection_on_tile(model, img, meta, flood_threshold=0.5, device="cpu")
    assert "flood_coverage" in result
    assert "is_candidate" in result
    print("[PASS] test_flood_detection_on_tile")


if __name__ == "__main__":
    test_segformer_forward_pass()
    test_segformer_from_weights()
    test_preprocess_tile()
    test_compute_flood_coverage()
    test_infrastructure_overlap_detection()
    test_flood_detection_on_tile()
    print("\nAll SegFormer tests completed.")
