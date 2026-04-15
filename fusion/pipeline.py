"""Satellite-UAV feature fusion for refined victim detection and region correlation."""

import numpy as np
import torch
import torch.nn as nn
from typing import List, Dict, Tuple


class FeatureFusionModule(nn.Module):
    # Concatenation-based feature fusion with channel attention refinement
    def __init__(self, sat_dim: int = 512, uav_dim: int = 256, fused_dim: int = 256):
        super().__init__()
        self.sat_proj = nn.Linear(sat_dim, fused_dim)
        self.uav_proj = nn.Linear(uav_dim, fused_dim)
        self.channel_attn = nn.Sequential(
            nn.Linear(fused_dim * 2, fused_dim),
            nn.ReLU(),
            nn.Linear(fused_dim, fused_dim * 2),
            nn.Sigmoid(),
        )
        self.fuse = nn.Sequential(
            nn.Linear(fused_dim * 2, fused_dim),
            nn.LayerNorm(fused_dim),
            nn.ReLU(),
        )

    def forward(self, sat_feat: torch.Tensor, uav_feat: torch.Tensor) -> torch.Tensor:
        # Project, attend, and fuse satellite and UAV feature vectors
        s = self.sat_proj(sat_feat)
        u = self.uav_proj(uav_feat)
        concat = torch.cat([s, u], dim=-1)
        attn = self.channel_attn(concat)
        attended = concat * attn
        return self.fuse(attended)


def extract_region_feature_vector(flood_region: Dict) -> np.ndarray:
    # Build a fixed-size feature vector from flood detection metadata
    coverage = flood_region.get("flood_coverage", 0.0)
    val_score = flood_region.get("validation_score", 0.0)
    infra = float(flood_region.get("infra_overlap", False))
    bbox = flood_region.get("bbox", [0, 0, 1, 1])
    area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
    cx, cy = (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2
    # Pad to 512 dims (simulation of SegFormer feature embedding)
    base = np.array([coverage, val_score, infra, area, cx, cy], dtype=np.float32)
    padded = np.zeros(512, dtype=np.float32)
    padded[:len(base)] = base
    return padded


def extract_detection_feature_vector(detection: Dict) -> np.ndarray:
    # Build feature vector from victim detection bounding box and confidence
    bbox = detection.get("bbox", [0, 0, 1, 1])
    area = detection.get("area", 0.0)
    conf = detection.get("confidence", 0.0)
    cx = (bbox[0] + bbox[2]) / 2.0
    cy = (bbox[1] + bbox[3]) / 2.0
    base = np.array([conf, area, cx, cy], dtype=np.float32)
    padded = np.zeros(256, dtype=np.float32)
    padded[:len(base)] = base
    return padded


def correlate_detections_to_regions(
    detections: List[Dict],
    flood_regions: List[Dict]
) -> List[Dict]:
    # Assign each detection to its parent flood region based on region_id field
    region_map = {r["tile_id"]: r for r in flood_regions}
    correlated = []
    for det in detections:
        region_id = det.get("region_id")
        region = region_map.get(region_id)
        if region:
            det["region_coverage"] = region.get("flood_coverage", 0.0)
            det["region_val_score"] = region.get("validation_score", 0.0)
            correlated.append(det)
    return correlated


def fuse_multimodal_scores(detections: List[Dict]) -> List[Dict]:
    # Multiply detection confidence by region validation score for joint score
    for det in detections:
        sat_confidence = det.get("region_val_score", 1.0)
        uav_confidence = det.get("confidence", 0.0)
        det["fused_score"] = float(sat_confidence * uav_confidence)
    return sorted(detections, key=lambda d: d["fused_score"], reverse=True)


def run_fusion_pipeline(cfg, flood_regions: List[Dict], detections: List[Dict]) -> List[Dict]:
    # Correlate detections with regions, compute fused scores, return ranked results
    correlated = correlate_detections_to_regions(detections, flood_regions)
    fused = fuse_multimodal_scores(correlated)
    return fused
