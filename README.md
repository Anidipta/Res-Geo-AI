# Res-GeoAI: A Satellite-to-Drone Dual-Modality System for Flood Detection and Victim Localization in Disaster Response

---
**Presented at:** CVIP 2025 (10th International Conference on Computer Vision and Image Processing 2025)

Rapid and effective disaster response remains a critical challenge, particularly during floods, where timely identification of affected areas and victims can save lives. Existing systems often rely solely on either satellite imagery or ground-based sensors, limiting their ability to quickly and accurately pinpoint flooded zones and locate stranded individuals.

To address this gap, we propose **Res-GeoAI**, a geospatial AI system that integrates satellite-based flood detection with drone-assisted victim identification. Our system operates in three hierarchical stages:

1. **Satellite Flood Mapping** — Semantic segmentation of satellite imagery to detect flooded zones
2. **Flood Validation** — CNN-based classification to validate candidate flood regions  
3. **UAV Victim Detection & Localization** — Thermal imaging and object detection for victim identification with GPS coordinates

By combining these capabilities, Res-GeoAI enhances the speed and precision of humanitarian interventions, providing a scalable solution for disaster management.

---

## System Overview

![Res-GeoAI System Workflow](https://github.com/Anidipta/Res-Geo-AI/blob/main/images/fig1.png)

**Figure 1.** End-to-end system workflow for flood victim detection and localization. Level 1 (top): satellite segmentation and flood coverage analysis across large geographic regions. Level 2 (bottom): UAV victim detection via thermal imaging and GPS localization for coordinated rescue operations.

---

## Experimental Results

### 1. Semantic Segmentation — LoveDA Dataset

Comparison of segmentation models for 7-class land-use classification on satellite imagery:

| Model | Background | Building | Road | Water | Barren | Forest | Agriculture | **mIoU** |
|-------|-----------|----------|------|-------|--------|--------|-------------|---------|
| UNet | 43.46 | 60.59 | 52.35 | 69.22 | 46.60 | 24.23 | 41.88 | 48.95 |
| Semantic FPN | 60.70 | 50.92 | 51.36 | 73.93 | 52.05 | 56.24 | 76.94 | 57.98 |
| FuseNet | 47.19 | 50.77 | 61.36 | 68.21 | 31.71 | 47.71 | 57.45 | 52.62 |
| HRNet | 54.61 | 55.34 | 57.42 | 73.36 | 46.78 | 45.87 | 69.88 | 59.40 |
| **Ours (CNN+SegFormer)** | **60.68** | **63.25** | **62.08** | **76.47** | **47.93** | **47.82** | **72.75** | **66.30** |

Our modified CNN+SegFormer architecture achieves the highest mIoU (66.30%) with superior water class detection (76.47%), critical for flood mapping.

### 2. Flood Validation — FloodNet Dataset

Binary classification accuracy for flood region validation using Xception-based classifier:

| Model | Training Accuracy | Test Accuracy |
|-------|------------------|---------------|
| InceptionNetV3 | 0.990 | 0.844 |
| ResNet50 | 0.974 | 0.937 |
| **Xception (Ours)** | **0.998** | **0.946** |

The Xception-based validator achieves 94.6% test accuracy, effectively reducing false positives in flood detection and triggering UAV deployment only when confidence exceeds 0.7.

### 3. Victim Detection — HIT-MOB Dataset (Multi-Modality)

VFNet victim detection performance across different imaging modes (RGB, Thermal, Infrared, Night Vision):

| Model | RGB | Thermal | Infrared | Night Vision |
|-------|-----|---------|----------|--------------|
| YOLOv8 (mF1 / MPR) | 0.841 / 0.136 | 0.846 / 0.136 | 0.850 / 0.133 | 0.857 / 0.131 |
| **VFNet (mF1 / MPR)** | **0.858 / 0.117** | **0.863 / 0.114** | **0.860 / 0.115** | **0.865 / 0.111** |

Night vision mode achieves the highest mF1 score (0.865), optimal for low-visibility disaster scenarios with improved victim detection and minimal false alarms.

### 4. System Performance

End-to-end pipeline execution metrics on a 1000 km² region (Zoom Level 11):

| Module | Input Size | Execution Time | Memory Usage | Accuracy |
|--------|-----------|-----------------|--------------|----------|
| Tile Generation | 1024×1024 | 0.80s | 17.5 MB | 1.00 |
| Flood Detection | 1024×1024 | 0.05s | 4.5 MB | 0.66 |
| Flood Validation | 1024×1024 | 0.02s | 1.5 MB | 0.95 |
| Victim Detection | 512×512 | 0.04s | 2.0 MB | 0.86 |
| GPS Localization | — | 0.01s | 0.1 MB | ±3.2m |
| **Total** | **—** | **0.92s** | **25.6 MB** | **Efficient** |

---

## Repository Structure

```
Res-Geo-AI/
├── main.py                        # Entry point for full pipeline
├── requirements.txt               # Python dependencies
├── README.md                      # This file
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
├── utils/
│   ├── logger.py                  # Centralized logger factory
│   ├── io.py                      # Image loading, JSON I/O, overlay saving
│   ├── metrics.py                 # IoU, mIoU, F1, MPR, GPS error calculation
│   └── visualization.py           # Segmentation colorization, cluster plots
├── dataset/
│   └── __init__.py
├── images/
│   └── fig1.png                   # System workflow diagram
└── testing/
    ├── run_all_tests.py           # Test suite runner
    ├── test_segformer.py          # SegFormer architecture tests
    ├── test_xception.py           # Flood validator tests
    ├── test_vfnet.py              # VFNet victim detector tests
    ├── test_gps.py                # GPS localization tests
    ├── test_tessellation_and_planning.py
    └── saved_models/              # Place .pth checkpoints here
        ├── segformer_flood.pth
        ├── xception_flood.pth
        └── vfnet_res2net101.pth
```

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Anidipta/Res-Geo-AI.git
cd Res-Geo-AI

# Install dependencies
pip install -r requirements.txt
```

### Usage Examples

```bash
# Full end-to-end pipeline (satellite + UAV + GPS)
python main.py --region data/region.geojson --output outputs/ --mode full

# Satellite-only mode (flood detection & validation)
python main.py --region data/region.geojson --output outputs/ --mode satellite

# UAV victim detection mode (from pre-detected flood regions)
python main.py --flood-tiles outputs/flood_tiles.json --output outputs/ --mode uav

# Run complete test suite
cd testing && python run_all_tests.py
```

---

## Citation

If you find this work useful in your research, please cite:

```bibtex
@article{pal2025resgeoai,
  title     = {Res-GeoAI: A Satellite-to-Drone Dual-Modality System
               for Flood Detection and Victim Localization
               in Disaster Response},
  author    = {Pal, Anidipta},
  year      = {2025},
  url       = {https://doi.org/10.13140/RG.2.2.32814.88642}
}
```

---

## Contact & Resources

- **Author:** Anidipta Pal
- **GitHub:** [Anidipta/Res-Geo-AI](https://github.com/Anidipta/Res-Geo-AI)
- **Dataset:** [HIT-MOB on Kaggle](https://www.kaggle.com/dsv/12184019)
- **Preprint DOI:** [10.13140/RG.2.2.32814.88642](https://doi.org/10.13140/RG.2.2.32814.88642)

