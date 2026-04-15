"""Orchestrates the full satellite-based flood detection pipeline."""

import os
import numpy as np
from typing import List, Dict

from configs.config import ResGeoAIConfig
from satellite.tessellation import build_valid_tileset, get_tile_centroid
from satellite.segformer import load_segformer
from satellite.flood_detection import batch_detect_floods, select_high_risk_regions
from satellite.flood_validation import load_xception_validator, validate_flood_candidates
from utils.logger import get_logger
from utils.io import load_satellite_tile, save_json

logger = get_logger(__name__)


def load_tile_images(tiles: List[Dict], image_dir: str) -> List[np.ndarray]:
    # Load RGB images corresponding to each tile from a directory
    images = []
    for tile in tiles:
        img_path = os.path.join(image_dir, f"{tile['id']}.png")
        img = load_satellite_tile(img_path)
        images.append(img)
    return images


def compute_deploy_decision(region: Dict, cfg: ResGeoAIConfig) -> bool:
    # Apply threshold logic: deploy UAV only when validation score and coverage pass
    return (
        region.get("validation_score", 0) > cfg.satellite.deploy_confidence
        and region.get("flood_coverage", 0) > cfg.satellite.coverage_threshold
    )


def run_satellite_pipeline(cfg: ResGeoAIConfig, region_geojson: str, output_dir: str) -> List[Dict]:
    # Full satellite stage: tile → detect → validate → return flood regions for UAV
    logger.info(f"Loading tiles from region: {region_geojson}")
    tiles = build_valid_tileset(region_geojson, cfg.satellite.tile_grid_n)
    logger.info(f"Valid tiles: {len(tiles)}")

    # Load tile images (assumes image_dir adjacent to geojson)
    image_dir = os.path.dirname(region_geojson)
    tile_images = load_tile_images(tiles, image_dir)

    # Flood segmentation
    logger.info("Running SegFormer flood detection...")
    segformer = load_segformer(cfg.satellite.weights_path, cfg.satellite.num_classes, cfg.device)
    detection_results = batch_detect_floods(
        segformer, tile_images, tiles,
        flood_threshold=cfg.satellite.flood_threshold,
        device=cfg.device
    )

    # Filter high-risk candidates
    candidates = select_high_risk_regions(detection_results, cfg.satellite.coverage_threshold)
    logger.info(f"Flood candidate tiles: {len(candidates)}")

    # Validate with Xception
    logger.info("Validating with Xception classifier...")
    candidate_images = [tile_images[tiles.index(c)] for c in candidates if c in tiles]
    xception = load_xception_validator(cfg.validation.weights_path, cfg.device)
    validated_regions = validate_flood_candidates(
        xception, candidates, candidate_images,
        conf_threshold=cfg.validation.confidence_threshold,
        device=cfg.device
    )

    # Decide UAV deployment per region
    deploy_regions = []
    for region in validated_regions:
        region["centroid"] = get_tile_centroid({"xmin": region["bbox"][0], "xmax": region["bbox"][2],
                                                "ymin": region["bbox"][1], "ymax": region["bbox"][3]})
        region["deploy_uav"] = compute_deploy_decision(region, cfg)
        if region["deploy_uav"]:
            deploy_regions.append(region)

    logger.info(f"Regions flagged for UAV deployment: {len(deploy_regions)}")
    os.makedirs(output_dir, exist_ok=True)
    save_json(deploy_regions, os.path.join(output_dir, "flood_regions.json"))
    return deploy_regions
