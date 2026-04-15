"""GPS coordinate computation from UAV pose, camera intrinsics, and pixel detections."""

import numpy as np
from typing import Dict, List, Tuple


def build_camera_intrinsics(focal_length: float, cx: float, cy: float) -> np.ndarray:
    # Build 3x3 camera intrinsic matrix K from focal length and principal point
    return np.array([
        [focal_length, 0, cx],
        [0, focal_length, cy],
        [0, 0, 1]
    ], dtype=np.float64)


def pixel_to_gps(
    u: float, v: float,
    altitude: float,
    focal_length: float,
    R_uav: np.ndarray,
    t_uav: np.ndarray,
    img_w: int = 512,
    img_h: int = 512
) -> Tuple[float, float, float]:
    # Project pixel (u,v) to GPS coords using UAV extrinsics and altitude
    K = build_camera_intrinsics(focal_length, img_w / 2.0, img_h / 2.0)
    K_inv = np.linalg.inv(K)
    pixel_hom = np.array([u, v, 1.0], dtype=np.float64)
    ray_cam = K_inv @ pixel_hom
    scale = altitude / focal_length
    pos_world = R_uav @ (ray_cam * scale) + t_uav
    return float(pos_world[0]), float(pos_world[1]), float(pos_world[2])


def compute_gps_error(
    sigma_pixel: float,
    altitude: float,
    focal_length: float,
    sigma_altitude: float,
    sigma_pose: float,
    sigma_calib: float = 0.3,
    sigma_env: float = 1.5
) -> float:
    # Root-sum-square GPS localization error from all uncertainty sources
    pixel_contrib = sigma_pixel * (altitude / focal_length)
    total = np.sqrt(
        pixel_contrib ** 2 +
        sigma_altitude ** 2 +
        sigma_pose ** 2 +
        sigma_calib ** 2 +
        sigma_env ** 2
    )
    return float(total)


def build_uav_rotation(roll: float, pitch: float, yaw: float) -> np.ndarray:
    # Build 3x3 rotation matrix from UAV Euler angles in radians
    Rx = np.array([[1, 0, 0],
                   [0, np.cos(roll), -np.sin(roll)],
                   [0, np.sin(roll),  np.cos(roll)]])
    Ry = np.array([[ np.cos(pitch), 0, np.sin(pitch)],
                   [0, 1, 0],
                   [-np.sin(pitch), 0, np.cos(pitch)]])
    Rz = np.array([[np.cos(yaw), -np.sin(yaw), 0],
                   [np.sin(yaw),  np.cos(yaw), 0],
                   [0, 0, 1]])
    return Rz @ Ry @ Rx


def localize_detection(detection: Dict, waypoint: Dict, gps_cfg, img_size: int = 512) -> Dict:
    # Convert bounding box center pixel to GPS coordinates and attach error estimate
    bbox = detection.get("bbox", [0, 0, img_size, img_size])
    u = (bbox[0] + bbox[2]) / 2.0
    v = (bbox[1] + bbox[3]) / 2.0
    altitude = waypoint.get("altitude", 100.0)
    # Default identity rotation and waypoint-based translation
    R_uav = build_uav_rotation(0.0, 0.0, 0.0)
    t_uav = np.array([waypoint.get("x", 0.0), waypoint.get("y", 0.0), -altitude])
    gps_x, gps_y, gps_z = pixel_to_gps(u, v, altitude, gps_cfg.focal_length, R_uav, t_uav, img_size, img_size)
    error = compute_gps_error(
        gps_cfg.sigma_pixel, altitude, gps_cfg.focal_length,
        gps_cfg.sigma_altitude, gps_cfg.sigma_pose,
        sigma_env=gps_cfg.sigma_wind
    )
    return {
        **detection,
        "gps_x": gps_x,
        "gps_y": gps_y,
        "gps_z": gps_z,
        "gps_error_m": error,
        "pixel_u": u,
        "pixel_v": v,
    }


def filter_valid_localizations(localizations: List[Dict], conf_threshold: float = 0.6, min_area: int = 50) -> List[Dict]:
    # Keep only detections meeting confidence and bounding box area thresholds
    return [
        loc for loc in localizations
        if loc.get("confidence", 0.0) > conf_threshold and loc.get("area", 0) >= min_area
    ]


def cluster_gps_points(localizations: List[Dict], radius_m: float = 5.0) -> List[Dict]:
    # Merge nearby GPS points within radius_m into single rescue target
    if not localizations:
        return []
    clusters = []
    used = [False] * len(localizations)
    for i, loc in enumerate(localizations):
        if used[i]:
            continue
        group = [loc]
        used[i] = True
        for j, other in enumerate(localizations[i + 1:], start=i + 1):
            dist = np.sqrt((loc["gps_x"] - other["gps_x"]) ** 2 + (loc["gps_y"] - other["gps_y"]) ** 2)
            if dist <= radius_m:
                group.append(other)
                used[j] = True
        cx = float(np.mean([g["gps_x"] for g in group]))
        cy = float(np.mean([g["gps_y"] for g in group]))
        clusters.append({
            "cluster_gps_x": cx,
            "cluster_gps_y": cy,
            "victim_count": len(group),
            "avg_confidence": float(np.mean([g["confidence"] for g in group])),
            "avg_error_m": float(np.mean([g["gps_error_m"] for g in group])),
            "members": group,
        })
    return clusters


def run_gps_localization(cfg, fused_detections: List[Dict], output_dir: str) -> List[Dict]:
    # Localize all fused detections to GPS, filter, cluster, and save results
    import os
    from utils.io import save_json
    from utils.logger import get_logger
    logger = get_logger(__name__)

    localizations = []
    for det in fused_detections:
        wp = det.get("waypoint", {"x": 0.0, "y": 0.0, "altitude": 100.0})
        loc = localize_detection(det, wp, cfg.gps)
        localizations.append(loc)

    valid = filter_valid_localizations(localizations, cfg.uav.conf_threshold, cfg.uav.min_box_area)
    clusters = cluster_gps_points(valid)
    logger.info(f"GPS clusters (rescue targets): {len(clusters)}")

    os.makedirs(output_dir, exist_ok=True)
    save_json(localizations, os.path.join(output_dir, "gps_localizations.json"))
    save_json(clusters, os.path.join(output_dir, "rescue_targets.json"))
    return clusters
