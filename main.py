"""Res-GeoAI: Satellite-to-Drone dual-modality flood detection and victim localization pipeline."""

import argparse
from configs.config import load_config
from satellite.pipeline import run_satellite_pipeline
from uav.pipeline import run_uav_pipeline
from fusion.pipeline import run_fusion_pipeline
from gps.localization import run_gps_localization
from utils.logger import get_logger

logger = get_logger(__name__)


def parse_args():
    # Parse CLI arguments for pipeline control
    parser = argparse.ArgumentParser(description="Res-GeoAI Disaster Response System")
    parser.add_argument("--config", type=str, default="configs/default.yaml", help="Config file path")
    parser.add_argument("--mode", type=str, choices=["satellite", "uav", "full"], default="full")
    parser.add_argument("--region", type=str, required=True, help="GeoJSON region file path")
    parser.add_argument("--output", type=str, default="outputs/", help="Output directory")
    return parser.parse_args()


def run_full_pipeline(cfg, region_path, output_dir):
    # Execute complete satellite → UAV → fusion → GPS pipeline
    logger.info("Starting full Res-GeoAI pipeline")
    flood_regions = run_satellite_pipeline(cfg, region_path, output_dir)
    victim_detections = run_uav_pipeline(cfg, flood_regions, output_dir)
    fused_results = run_fusion_pipeline(cfg, flood_regions, victim_detections)
    gps_coords = run_gps_localization(cfg, fused_results, output_dir)
    logger.info(f"Pipeline complete. {len(gps_coords)} victims localized.")
    return gps_coords


def main():
    # Main entry; dispatch to appropriate pipeline mode
    args = parse_args()
    cfg = load_config(args.config)
    if args.mode == "satellite":
        run_satellite_pipeline(cfg, args.region, args.output)
    elif args.mode == "uav":
        run_uav_pipeline(cfg, [], args.output)
    else:
        run_full_pipeline(cfg, args.region, args.output)


if __name__ == "__main__":
    main()
