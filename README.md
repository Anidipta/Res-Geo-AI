# Res-Geo-AI


```
res_geo_ai/
├── main.py                    # Main Streamlit app
├── config.py                  # Configuration and constants
├── models/
│   ├── __init__.py
│   ├── segmentation.py        # Model 1 - Segmentation
│   ├── flood_detection.py     # Model 2 - Flood Detection
│   └── person_detection.py    # Model 3 - Person Detection (YOLO)
├── utils/
│   ├── __init__.py
│   ├── image_processing.py    # Image processing utilities
│   ├── thermal_processing.py  # Thermal night vision processing
│   ├── geo_utils.py          # Geographic utilities
│   └── ui_styles.py          # UI styling functions
├── data/
│   ├── india_states.json     # States data with coordinates
│   └── satellite_maps/       # Cached satellite maps
├── assets/
│   └── models/              # Model files (.pt, .h5, etc.)
└── requirements.txt         # Dependencies
```

## Key Features:
- **Model 1**: Segmentation model trained on LoveDa Dataset
- **Model 2**: Xception-based flood detection model
- **Model 3**: YOLO model for person detection
- **Interactive satellite maps** with state selection
- **Thermal night vision processing** for enhanced detection
- **Geographic coordinate tracking** and distance calculations
- **Modern React-like UI styling** using Streamlit components
