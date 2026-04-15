"""File I/O utilities: image loading, JSON serialization, and frame reading."""

import os
import json
import numpy as np
from typing import List, Dict, Optional


def load_satellite_tile(path: str, size: int = 1024) -> np.ndarray:
    # Load satellite tile image from disk, returning zero array if missing
    import cv2
    if not os.path.exists(path):
        return np.zeros((size, size, 3), dtype=np.uint8)
    img = cv2.imread(path)
    if img is None:
        return np.zeros((size, size, 3), dtype=np.uint8)
    return cv2.cvtColor(cv2.resize(img, (size, size)), cv2.COLOR_BGR2RGB)


def load_uav_frames(frame_dir: str, max_frames: Optional[int] = None) -> List[np.ndarray]:
    # Load all PNG frames from a UAV frame directory in sorted order
    import cv2
    if not os.path.exists(frame_dir):
        return []
    paths = sorted([
        os.path.join(frame_dir, f) for f in os.listdir(frame_dir)
        if f.endswith(".png") or f.endswith(".jpg")
    ])
    if max_frames:
        paths = paths[:max_frames]
    frames = []
    for p in paths:
        img = cv2.imread(p)
        if img is not None:
            frames.append(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    return frames


def save_json(data: object, path: str, indent: int = 2):
    # Serialize data to JSON file, converting numpy types automatically
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=indent, default=_numpy_default)


def load_json(path: str) -> object:
    # Load and deserialize a JSON file from disk
    with open(path, "r") as f:
        return json.load(f)


def _numpy_default(obj):
    # JSON serializer helper to handle numpy scalar and array types
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def save_detection_overlay(img: np.ndarray, detections: List[Dict], path: str):
    # Draw bounding boxes on image and save annotated result to disk
    import cv2
    canvas = img.copy()
    for det in detections:
        bbox = det.get("bbox", [])
        if len(bbox) == 4:
            x1, y1, x2, y2 = [int(v) for v in bbox]
            label = f"{det.get('class_name', '?')} {det.get('confidence', 0):.2f}"
            cv2.rectangle(canvas, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(canvas, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    cv2.imwrite(path, cv2.cvtColor(canvas, cv2.COLOR_RGB2BGR))


def ensure_dir(path: str):
    # Create directory and all parents if they do not already exist
    os.makedirs(path, exist_ok=True)
