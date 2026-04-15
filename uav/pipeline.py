"""Orchestrates UAV deployment, frame capture simulation, and victim detection."""

import os
import numpy as np
from typing import List, Dict

from configs.config import ResGeoAIConfig
from uav.flight_planner import plan_uav_mission
from uav.varifocalnet import load_vfnet
from uav.victim_detector import detect_victims_batch, apply_nms
from utils.logger import get_logger
from utils.io import load_uav_frames, save_json

logger = get_logger(__name__)


def simulate_uav_frames(waypoints: List[Dict], frame_dir: str) -> List[np.ndarray]:
    # Load or synthesize UAV frames corresponding to each waypoint
    import cv2
    frames = []
    for i, _ in enumerate(waypoints):
        frame_path = os.path.join(frame_dir, f"frame_{i:05d}.png")
        if os.path.exists(frame_path):
            frames.append(cv2.cvtColor(cv2.imread(frame_path), cv2.COLOR_BGR2RGB))
        else:
            # Generate placeholder when actual frame not available
            frames.append(np.zeros((512, 512, 3), dtype=np.uint8))
    return frames


def run_uav_pipeline(cfg: ResGeoAIConfig, flood_regions: List[Dict], output_dir: str) -> List[Dict]:
    # Plan missions, simulate frames, run VFNet detection, return all victim detections
    if not flood_regions:
        logger.warning("No flood regions to deploy UAVs to.")
        return []

    logger.info(f"Loading VFNet from {cfg.uav.weights_path}")
    model = load_vfnet(cfg.uav.weights_path, num_classes=9, device=cfg.device)

    all_victim_detections = []
    for region in flood_regions:
        logger.info(f"Planning UAV mission for region: {region['tile_id']}")
        mission = plan_uav_mission(region, cfg.uav)
        waypoints = mission["waypoints"]

        frame_dir = os.path.join(output_dir, "uav_frames", region["tile_id"])
        frames = simulate_uav_frames(waypoints, frame_dir)

        logger.info(f"Detecting victims across {len(frames)} UAV frames...")
        detections = detect_victims_batch(model, frames, waypoints, cfg.uav, cfg.device)
        detections = apply_nms(detections)

        for det in detections:
            det["region_id"] = region["tile_id"]
            det["region_bbox"] = region["bbox"]

        logger.info(f"Victims detected in region {region['tile_id']}: {len(detections)}")
        all_victim_detections.extend(detections)

    os.makedirs(output_dir, exist_ok=True)
    save_json(all_victim_detections, os.path.join(output_dir, "victim_detections.json"))
    return all_victim_detections
