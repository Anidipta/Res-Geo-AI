"""Tests for VarifocalNet victim detection loaded from saved_models/."""

import numpy as np
import torch
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from uav.varifocalnet import VarifocalNet, load_vfnet, VarifocalLoss
from uav.victim_detector import (
    preprocess_frame, decode_predictions,
    detect_victims_in_frame, apply_nms
)
from uav.night_vision import transform_to_night_vision, preprocess_for_detection

# Checkpoint path — must exist locally before running
VFNET_WEIGHTS = os.path.join(os.path.dirname(__file__), "saved_models", "vfnet_res2net101.pth")


def _make_dummy_uav_cfg():
    # Return a minimal config-like namespace for UAV settings
    class Cfg:
        conf_threshold = 0.3
        min_box_area = 10
        image_size = 512
        gamma_min = 0.3
        gamma_max = 0.7
    return Cfg()


def test_vfnet_forward():
    # Confirm VFNet produces multi-scale head outputs with correct structure
    model = VarifocalNet(num_classes=9)
    dummy = torch.randn(1, 3, 512, 512)
    with torch.no_grad():
        outputs = model(dummy)
    assert len(outputs) == 4, "Expected 4 FPN levels"
    cls_out, reg_out, iou_out = outputs[0]
    assert cls_out.shape[1] == 9, "Expected 9 class channels"
    print("[PASS] test_vfnet_forward")


def test_vfnet_from_weights():
    # Load VFNet from saved checkpoint and run inference
    if not os.path.exists(VFNET_WEIGHTS):
        print(f"[SKIP] test_vfnet_from_weights — weights not found at {VFNET_WEIGHTS}")
        return
    model = load_vfnet(VFNET_WEIGHTS, num_classes=9, device="cpu")
    dummy = torch.randn(1, 3, 512, 512)
    with torch.no_grad():
        outputs = model(dummy)
    assert len(outputs) == 4
    print("[PASS] test_vfnet_from_weights")


def test_varifocal_loss():
    # Verify varifocal loss computes finite scalar value
    loss_fn = VarifocalLoss(alpha=0.75, gamma=2.0, beta=1.5)
    pred = torch.randn(4, 9, 64, 64)
    iou = torch.rand(4, 1, 64, 64)
    label = torch.randint(0, 2, (4, 9, 64, 64)).float()
    loss = loss_fn(pred, iou, label)
    assert torch.isfinite(loss), "Loss is not finite"
    print("[PASS] test_varifocal_loss")


def test_night_vision_transform():
    # Ensure night vision output has same spatial dimensions as input
    img = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
    nv = transform_to_night_vision(img)
    assert nv.shape[:2] == img.shape[:2], "Shape mismatch after NV transform"
    print("[PASS] test_night_vision_transform")


def test_preprocess_for_detection_modes():
    # Verify all imaging modes run without error and return correct shape
    img = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
    for mode in ["night_vision", "thermal", "infrared", "rgb"]:
        out = preprocess_for_detection(img, mode=mode)
        assert out.shape[:2] == (512, 512), f"Shape error in mode {mode}"
    print("[PASS] test_preprocess_for_detection_modes")


def test_detect_victims_in_frame():
    # Run full victim detection pipeline on random frame with untrained model
    model = VarifocalNet(num_classes=9)
    model.eval()
    cfg = _make_dummy_uav_cfg()
    img = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
    dets = detect_victims_in_frame(model, img, cfg, imaging_mode="night_vision", device="cpu")
    assert isinstance(dets, list)
    print(f"[PASS] test_detect_victims_in_frame — {len(dets)} persons detected")


def test_apply_nms():
    # Confirm NMS removes overlapping boxes and keeps distinct detections
    detections = [
        {"bbox": [10, 10, 50, 50], "confidence": 0.9, "class_name": "Person", "area": 1600},
        {"bbox": [12, 12, 52, 52], "confidence": 0.7, "class_name": "Person", "area": 1600},
        {"bbox": [200, 200, 250, 250], "confidence": 0.85, "class_name": "Person", "area": 2500},
    ]
    kept = apply_nms(detections, iou_threshold=0.5)
    assert len(kept) == 2, f"Expected 2 after NMS, got {len(kept)}"
    print("[PASS] test_apply_nms")


if __name__ == "__main__":
    test_vfnet_forward()
    test_vfnet_from_weights()
    test_varifocal_loss()
    test_night_vision_transform()
    test_preprocess_for_detection_modes()
    test_detect_victims_in_frame()
    test_apply_nms()
    print("\nAll VFNet tests completed.")
