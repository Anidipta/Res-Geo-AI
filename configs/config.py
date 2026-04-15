"""Configuration management for Res-GeoAI system."""

import yaml
import os
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SatelliteConfig:
    # Satellite segmentation model settings
    model_name: str = "segformer_b4"
    num_classes: int = 7
    image_size: int = 1024
    tile_grid_n: int = 5
    flood_threshold: float = 0.5
    coverage_threshold: float = 10.0
    deploy_confidence: float = 0.7
    weights_path: str = "saved_models/segformer_flood.pth"


@dataclass
class ValidationConfig:
    # Xception-based flood validation settings
    model_name: str = "xception"
    weights_path: str = "saved_models/xception_flood.h5"
    confidence_threshold: float = 0.7
    input_size: int = 299


@dataclass
class UAVConfig:
    # UAV flight and detection settings
    altitude_min: float = 60.0
    altitude_max: float = 130.0
    spiral_radius_step: float = 5.0
    angular_step: float = 0.1
    detection_model: str = "varifocalnet"
    backbone: str = "res2net101_dcn"
    weights_path: str = "saved_models/vfnet_res2net101.pth"
    image_size: int = 512
    conf_threshold: float = 0.6
    min_box_area: int = 50
    gamma_min: float = 0.3
    gamma_max: float = 0.7


@dataclass
class GPSConfig:
    # GPS localization and error settings
    sigma_pixel: float = 2.1
    sigma_altitude: float = 0.5
    sigma_pose: float = 0.8
    sigma_wind: float = 1.5
    focal_length: float = 35.0


@dataclass
class ResGeoAIConfig:
    # Top-level configuration container
    satellite: SatelliteConfig = field(default_factory=SatelliteConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    uav: UAVConfig = field(default_factory=UAVConfig)
    gps: GPSConfig = field(default_factory=GPSConfig)
    output_dir: str = "outputs/"
    log_level: str = "INFO"
    device: str = "cuda"


def load_config(config_path: str) -> ResGeoAIConfig:
    # Load YAML config and merge with dataclass defaults
    cfg = ResGeoAIConfig()
    if not os.path.exists(config_path):
        return cfg
    with open(config_path, "r") as f:
        data = yaml.safe_load(f)
    if data is None:
        return cfg
    if "satellite" in data:
        cfg.satellite = SatelliteConfig(**data["satellite"])
    if "validation" in data:
        cfg.validation = ValidationConfig(**data["validation"])
    if "uav" in data:
        cfg.uav = UAVConfig(**data["uav"])
    if "gps" in data:
        cfg.gps = GPSConfig(**data["gps"])
    return cfg


def save_config(cfg: ResGeoAIConfig, path: str):
    # Serialize config to YAML for reproducibility
    import dataclasses
    with open(path, "w") as f:
        yaml.dump(dataclasses.asdict(cfg), f)
