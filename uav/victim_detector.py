"""Run VarifocalNet inference on night-vision UAV frames for victim detection."""

import numpy as np
import torch
import torch.nn.functional as F
from typing import List, Dict, Tuple

from uav.varifocalnet import VarifocalNet
from uav.night_vision import preprocess_for_detection


# HIT-MOB class labels indexed 0-8
CLASS_LABELS = ["Person", "Car", "Bicycle", "OtherVehicle", "DontCare",
                "Boat", "LifeBuoy", "Surfboard", "Wood"]


def preprocess_frame(frame: np.ndarray, size: int = 512) -> torch.Tensor:
    # Resize and normalize UAV frame for VFNet input
    import cv2
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    resized = cv2.resize(frame, (size, size)).astype(np.float32) / 255.0
    normalized = (resized - mean) / std
    return torch.from_numpy(normalized.transpose(2, 0, 1)).unsqueeze(0)


def decode_predictions(
    head_outputs: List[Tuple],
    orig_h: int, orig_w: int,
    conf_threshold: float = 0.6,
    min_box_area: int = 50
) -> List[Dict]:
    # Decode VFNet head outputs into filtered bounding box detections
    detections = []
    strides = [8, 16, 32, 64]
    for (cls_out, reg_out, iou_out), stride in zip(head_outputs, strides):
        cls_probs = torch.sigmoid(cls_out[0])
        iou = iou_out[0, 0]
        reg = reg_out[0]
        # Combine cls prob and iou for varifocal score
        scores = cls_probs * iou.unsqueeze(0)
        max_scores, class_ids = scores.max(dim=0)
        pos_mask = max_scores > conf_threshold
        if not pos_mask.any():
            continue
        ys, xs = pos_mask.nonzero(as_tuple=True)
        for y, x in zip(ys.tolist(), xs.tolist()):
            score = max_scores[y, x].item()
            cls_id = class_ids[y, x].item()
            dx1, dy1, dx2, dy2 = reg[:, y, x].tolist()
            cx_px, cy_px = x * stride, y * stride
            x1 = int((cx_px - dx1) * orig_w / 512)
            y1 = int((cy_px - dy1) * orig_h / 512)
            x2 = int((cx_px + dx2) * orig_w / 512)
            y2 = int((cy_px + dy2) * orig_h / 512)
            area = max(0, x2 - x1) * max(0, y2 - y1)
            if area < min_box_area:
                continue
            detections.append({
                "class_id": cls_id,
                "class_name": CLASS_LABELS[cls_id] if cls_id < len(CLASS_LABELS) else "Unknown",
                "confidence": score,
                "bbox": [x1, y1, x2, y2],
                "area": area,
            })
    return detections


def detect_victims_in_frame(
    model: VarifocalNet,
    frame_rgb: np.ndarray,
    uav_cfg,
    imaging_mode: str = "night_vision",
    device: str = "cpu"
) -> List[Dict]:
    # Transform frame → night vision → VFNet inference → filter person detections
    transformed = preprocess_for_detection(frame_rgb, mode=imaging_mode,
                                           gamma_min=uav_cfg.gamma_min,
                                           gamma_max=uav_cfg.gamma_max)
    h, w = frame_rgb.shape[:2]
    tensor = preprocess_frame(transformed, size=uav_cfg.image_size).to(device)
    with torch.no_grad():
        head_outputs = model(tensor)
    dets = decode_predictions(head_outputs, h, w, uav_cfg.conf_threshold, uav_cfg.min_box_area)
    # Return only Person class detections for victim localization
    return [d for d in dets if d["class_name"] == "Person"]


def detect_victims_batch(
    model: VarifocalNet,
    frames: List[np.ndarray],
    waypoints: List[Dict],
    uav_cfg,
    device: str = "cpu"
) -> List[Dict]:
    # Run victim detection across all UAV frames, tagging each with waypoint info
    all_detections = []
    for frame, wp in zip(frames, waypoints):
        dets = detect_victims_in_frame(model, frame, uav_cfg, device=device)
        for det in dets:
            det["waypoint"] = wp
        all_detections.extend(dets)
    return all_detections


def apply_nms(detections: List[Dict], iou_threshold: float = 0.5) -> List[Dict]:
    # Apply non-maximum suppression to remove duplicate victim detections
    if not detections:
        return []
    boxes = torch.tensor([d["bbox"] for d in detections], dtype=torch.float32)
    scores = torch.tensor([d["confidence"] for d in detections], dtype=torch.float32)
    x1, y1, x2, y2 = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
    areas = (x2 - x1) * (y2 - y1)
    _, order = scores.sort(descending=True)
    keep = []
    while order.numel() > 0:
        i = order[0].item()
        keep.append(i)
        if order.numel() == 1:
            break
        inter_x1 = x1[order[1:]].clamp(min=x1[i].item())
        inter_y1 = y1[order[1:]].clamp(min=y1[i].item())
        inter_x2 = x2[order[1:]].clamp(max=x2[i].item())
        inter_y2 = y2[order[1:]].clamp(max=y2[i].item())
        inter = (inter_x2 - inter_x1).clamp(0) * (inter_y2 - inter_y1).clamp(0)
        iou = inter / (areas[i] + areas[order[1:]] - inter + 1e-6)
        order = order[1:][iou <= iou_threshold]
    return [detections[k] for k in keep]
