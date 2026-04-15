# Res-GeoAI

Satellite-to-Drone dual-modality system for flood detection and victim localization, implementing the architecture described in the paper by Anidipta Pal (Heritage Institute of Technology, Kolkata).

## Structure

```
├── main.py                        # Entry point
├── requirements.txt
├── configs/
│   ├── config.py                  # Dataclass config + YAML loader
│   └── default.yaml               # Default hyperparameters
├── satellite/
│   ├── tessellation.py            # MBR, grid tessellation, tile filtering
│   ├── segformer.py               # Modified SegFormer with multiscale attention
│   ├── flood_detection.py         # Per-tile flood inference and coverage
│   ├── flood_validation.py        # Xception-based flood region validation
│   └── pipeline.py                # Satellite pipeline orchestrator
├── uav/
│   ├── night_vision.py            # RGB → night vision / thermal / IR transforms
│   ├── varifocalnet.py            # VFNet with Res2Net backbone + varifocal loss
│   ├── victim_detector.py         # Inference, NMS, person-class filtering
│   ├── flight_planner.py          # Spiral UAV path planning
│   └── pipeline.py                # UAV pipeline orchestrator
├── fusion/
│   └── pipeline.py                # Satellite–UAV feature fusion and score merging
├── gps/
│   ├── localization.py            # Pixel→GPS projection, clustering, error propagation
│   └── kalman_filter.py           # 6-DOF Kalman filter for pose smoothing
└── utils/
    ├── logger.py                  # Centralized logger factory
    ├── io.py                      # Image loading, JSON I/O, overlay saving
    ├── metrics.py                 # IoU, mIoU, F1, MPR, GPS error
    └── visualization.py           # Segmentation colorization, cluster plots
```

### Testing

```
testing/
├── run_all_tests.py               # Discovers and runs all test_*.py suites
├── test_segformer.py
├── test_xception.py
├── test_vfnet.py
├── test_gps.py
├── test_tessellation_and_planning.py
└── saved_models/                  # Place .pth checkpoints here before testing
    ├── segformer_flood.pth
    ├── xception_flood.pth
    └── vfnet_res2net101.pth
```

Tests that cannot find a checkpoint emit `[SKIP]` and continue — they do not fail the suite.

## Quick Start

```bash
pip install -r requirements.txt

# Full pipeline
python main.py --region data/region.geojson --output outputs/ --mode full

# Satellite only
python main.py --region data/region.geojson --output outputs/ --mode satellite

# Run tests
cd testing && python run_all_tests.py
```

## Citation

```bibtex
@article{pal2025resgeoai,
  title   = {Updating Soon},
  author  = {Pal, Anidipta},
  year    = {2025}
}
```
