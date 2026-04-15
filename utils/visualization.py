"""Visualization tools: flood maps, detection overlays, GPS cluster plots."""

import numpy as np
import os
from typing import List, Dict, Optional, Tuple


def colorize_segmentation(seg_map: np.ndarray, num_classes: int = 7) -> np.ndarray:
    # Map class indices to distinct RGB colors for visualization
    palette = np.array([
        [0,   0,   0],    # Background
        [255, 0,   0],    # Building
        [255, 255, 0],    # Road
        [0,   0,   255],  # Water
        [165, 42,  42],   # Barren
        [0,   128, 0],    # Forest
        [0,   255, 0],    # Agriculture
    ], dtype=np.uint8)
    h, w = seg_map.shape
    color_map = np.zeros((h, w, 3), dtype=np.uint8)
    for c in range(min(num_classes, len(palette))):
        color_map[seg_map == c] = palette[c]
    return color_map


def overlay_flood_mask(img_rgb: np.ndarray, flood_mask: np.ndarray,
                        alpha: float = 0.4) -> np.ndarray:
    # Blend blue flood mask onto original RGB image with given transparency
    overlay = img_rgb.copy()
    overlay[flood_mask] = (overlay[flood_mask] * (1 - alpha) + np.array([0, 0, 255]) * alpha).astype(np.uint8)
    return overlay


def draw_bounding_boxes(img: np.ndarray, detections: List[Dict],
                         color: Tuple[int, int, int] = (0, 255, 0)) -> np.ndarray:
    # Draw detection bounding boxes with class label and confidence score
    import cv2
    canvas = img.copy()
    for det in detections:
        bbox = det.get("bbox", [])
        if len(bbox) != 4:
            continue
        x1, y1, x2, y2 = [int(v) for v in bbox]
        label = f"{det.get('class_name', '?')} {det.get('confidence', 0):.2f}"
        cv2.rectangle(canvas, (x1, y1), (x2, y2), color, 2)
        cv2.putText(canvas, label, (x1, max(y1 - 6, 0)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)
    return canvas


def plot_gps_clusters(clusters: List[Dict], output_path: str,
                       region_bbox: Optional[Tuple] = None):
    # Generate matplotlib scatter plot of GPS rescue target clusters
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return
    fig, ax = plt.subplots(figsize=(8, 8))
    if region_bbox:
        xmin, ymin, xmax, ymax = region_bbox
        rect = plt.Rectangle((xmin, ymin), xmax - xmin, ymax - ymin,
                               fill=False, edgecolor="blue", linewidth=2, label="Flood Region")
        ax.add_patch(rect)
    xs = [c["cluster_gps_x"] for c in clusters]
    ys = [c["cluster_gps_y"] for c in clusters]
    counts = [c["victim_count"] for c in clusters]
    sc = ax.scatter(xs, ys, c=counts, cmap="Reds", s=100, zorder=5, label="Rescue Targets")
    plt.colorbar(sc, ax=ax, label="Victim Count")
    ax.set_xlabel("GPS X")
    ax.set_ylabel("GPS Y")
    ax.set_title("Res-GeoAI: GPS Rescue Target Clusters")
    ax.legend()
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()


def save_segmentation_visual(img_rgb: np.ndarray, seg_map: np.ndarray,
                              flood_mask: np.ndarray, output_path: str):
    # Save side-by-side original, segmentation, and flood overlay image
    import cv2
    colored = colorize_segmentation(seg_map)
    overlaid = overlay_flood_mask(img_rgb, flood_mask)
    combined = np.concatenate([img_rgb, colored, overlaid], axis=1)
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    cv2.imwrite(output_path, cv2.cvtColor(combined, cv2.COLOR_RGB2BGR))
