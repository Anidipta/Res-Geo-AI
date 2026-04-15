"""Flood detection inference: compute per-tile flood probability and coverage."""

import numpy as np
import torch
import torch.nn.functional as F
from typing import Dict, List, Tuple

from satellite.segformer import ModifiedSegFormer


def preprocess_tile(tile_img: np.ndarray, target_size: int = 1024) -> torch.Tensor:
    # Normalize and resize satellite tile to model input format
    import cv2
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    img = cv2.resize(tile_img, (target_size, target_size)).astype(np.float32) / 255.0
    img = (img - mean) / std
    return torch.from_numpy(img.transpose(2, 0, 1)).unsqueeze(0)


def compute_flood_coverage(prob_map: np.ndarray, threshold: float = 0.5) -> float:
    # Calculate percentage of pixels with flood probability above threshold
    flood_mask = prob_map > threshold
    return float(flood_mask.sum()) / flood_mask.size * 100.0


def detect_infrastructure_overlap(flood_mask: np.ndarray, seg_map: np.ndarray) -> bool:
    # Check if detected water overlaps building (class 1) or road (class 2) pixels
    building_road_mask = np.isin(seg_map, [1, 2])
    overlap = np.logical_and(flood_mask, building_road_mask)
    return bool(overlap.sum() > 0)


def run_flood_detection_on_tile(
    model: ModifiedSegFormer,
    tile_img: np.ndarray,
    tile_meta: Dict,
    flood_threshold: float = 0.5,
    device: str = "cpu"
) -> Dict:
    # Run SegFormer inference and return flood metadata for one tile
    tensor = preprocess_tile(tile_img).to(device)
    with torch.no_grad():
        logits = model(tensor)
        seg_map = logits.argmax(dim=1).squeeze(0).cpu().numpy()
        probs = torch.softmax(logits, dim=1)
        flood_prob = probs[0, 3, :, :].cpu().numpy()

    coverage = compute_flood_coverage(flood_prob, flood_threshold)
    flood_mask = flood_prob > flood_threshold
    infra_overlap = detect_infrastructure_overlap(flood_mask, seg_map)

    return {
        "tile_id": tile_meta["id"],
        "bbox": tile_meta["bbox"],
        "flood_coverage": coverage,
        "infra_overlap": infra_overlap,
        "flood_mask": flood_mask,
        "seg_map": seg_map,
        "flood_prob_map": flood_prob,
        "is_candidate": infra_overlap and coverage > 0.0,
    }


def batch_detect_floods(
    model: ModifiedSegFormer,
    tile_images: List[np.ndarray],
    tile_metas: List[Dict],
    flood_threshold: float = 0.5,
    device: str = "cpu"
) -> List[Dict]:
    # Process all valid tiles and collect flood detection results
    results = []
    for img, meta in zip(tile_images, tile_metas):
        result = run_flood_detection_on_tile(model, img, meta, flood_threshold, device)
        results.append(result)
    return results


def select_high_risk_regions(detection_results: List[Dict], coverage_threshold: float = 10.0) -> List[Dict]:
    # Filter tiles where flood coverage exceeds threshold and infra overlap exists
    return [r for r in detection_results if r["flood_coverage"] >= coverage_threshold and r["infra_overlap"]]
