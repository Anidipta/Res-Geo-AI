STATES_DATA = {
    "Andhra Pradesh": {"lat": 15.9129, "lng": 79.7400, "zoom": 7},
    "Arunachal Pradesh": {"lat": 28.2180, "lng": 94.7278, "zoom": 7},
    "Assam": {"lat": 26.2006, "lng": 92.9376, "zoom": 7},
    "Bihar": {"lat": 25.0961, "lng": 85.3131, "zoom": 7},
    "Chhattisgarh": {"lat": 21.2787, "lng": 81.8661, "zoom": 7},
    "Goa": {"lat": 15.2993, "lng": 74.1240, "zoom": 9},
    "Gujarat": {"lat": 23.0225, "lng": 72.5714, "zoom": 7},
    "Haryana": {"lat": 29.0588, "lng": 76.0856, "zoom": 8},
    "Himachal Pradesh": {"lat": 31.1048, "lng": 77.1734, "zoom": 7},
    "Jharkhand": {"lat": 23.6102, "lng": 85.2799, "zoom": 7},
    "Karnataka": {"lat": 15.3173, "lng": 75.7139, "zoom": 7},
    "Kerala": {"lat": 10.8505, "lng": 76.2711, "zoom": 7},
    "Madhya Pradesh": {"lat": 22.9734, "lng": 78.6569, "zoom": 6},
    "Maharashtra": {"lat": 19.7515, "lng": 75.7139, "zoom": 6},
    "Manipur": {"lat": 24.6637, "lng": 93.9063, "zoom": 8},
    "Meghalaya": {"lat": 25.4670, "lng": 91.3662, "zoom": 8},
    "Mizoram": {"lat": 23.1645, "lng": 92.9376, "zoom": 8},
    "Nagaland": {"lat": 26.1584, "lng": 94.5624, "zoom": 8},
    "Odisha": {"lat": 20.9517, "lng": 85.0985, "zoom": 7},
    "Punjab": {"lat": 31.1471, "lng": 75.3412, "zoom": 7},
    "Rajasthan": {"lat": 27.0238, "lng": 74.2179, "zoom": 6},
    "Sikkim": {"lat": 27.5330, "lng": 88.5122, "zoom": 9},
    "Tamil Nadu": {"lat": 11.1271, "lng": 78.6569, "zoom": 7},
    "Telangana": {"lat": 18.1124, "lng": 79.0193, "zoom": 7},
    "Tripura": {"lat": 23.9408, "lng": 91.9882, "zoom": 8},
    "Uttar Pradesh": {"lat": 26.8467, "lng": 80.9462, "zoom": 6},
    "Uttarakhand": {"lat": 30.0668, "lng": 79.0193, "zoom": 7},
    "West Bengal": {"lat": 22.9868, "lng": 87.8550, "zoom": 7},
    "Delhi": {"lat": 28.7041, "lng": 77.1025, "zoom": 10},
    "Jammu and Kashmir": {"lat": 34.0837, "lng": 74.7973, "zoom": 7},
    "Ladakh": {"lat": 34.1526, "lng": 77.5771, "zoom": 6}
}

APP_CONFIG = {
    "title": "Res Geo AI",
    "subtitle": "Satellite-to-Drone Dual-Modality System for Flood Detection",
    "models": {
        "segmentation_path": "assets/models/segmentation_model.h5",
        "flood_detection_path": "assets/models/flood_detection_model.h5",
        "person_detection_path": "assets/models/person_detection_model.pt"
    },
    "image_size": {
        "segmentation": (256, 256),
        "flood_detection": (512, 512),
        "thermal": (512, 512)
    },
    "thresholds": {
        "water_coverage": 50,
        "flood_confidence": 0.6,
        "person_confidence": 0.5
    }
}

COLORS = {
    "primary": "#1E88E5",
    "secondary": "#FFC107",
    "success": "#4CAF50",
    "danger": "#F44336",
    "warning": "#FF9800",
    "info": "#2196F3",
    "dark": "#212529",
    "light": "#F8F9FA"
}