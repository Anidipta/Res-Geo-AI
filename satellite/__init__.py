"""Satellite module: tessellation, SegFormer segmentation, flood detection and validation."""
from satellite.tessellation import build_valid_tileset
from satellite.segformer import ModifiedSegFormer, load_segformer
from satellite.flood_detection import batch_detect_floods, select_high_risk_regions
from satellite.flood_validation import XceptionFloodClassifier, validate_flood_candidates
from satellite.pipeline import run_satellite_pipeline
