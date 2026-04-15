"""UAV flight path planning using spiral search pattern from flood region centroid."""

import numpy as np
from typing import List, Tuple, Dict


def compute_uav_deploy_point(flood_region: Dict) -> Tuple[float, float]:
    # Compute UAV deployment centroid from flood region bounding box
    xmin, ymin, xmax, ymax = flood_region["bbox"]
    return (xmin + xmax) / 2.0, (ymin + ymax) / 2.0


def generate_spiral_path(
    center_x: float,
    center_y: float,
    radius_step: float = 5.0,
    angular_step: float = 0.1,
    max_radius: float = 200.0,
    altitude: float = 100.0
) -> List[Dict]:
    # Generate spiral waypoints starting from centroid expanding outward
    waypoints = []
    t = 0.0
    while True:
        r = radius_step * t
        if r > max_radius:
            break
        x = center_x + r * np.cos(angular_step * t)
        y = center_y + r * np.sin(angular_step * t)
        waypoints.append({
            "x": float(x),
            "y": float(y),
            "altitude": altitude,
            "t": float(t),
            "radius": float(r)
        })
        t += 1.0
    return waypoints


def plan_uav_mission(flood_region: Dict, uav_cfg) -> Dict:
    # Create full mission plan: deploy point, spiral path, altitude range
    cx, cy = compute_uav_deploy_point(flood_region)
    waypoints = generate_spiral_path(
        cx, cy,
        radius_step=uav_cfg.spiral_radius_step,
        angular_step=uav_cfg.angular_step,
        altitude=(uav_cfg.altitude_min + uav_cfg.altitude_max) / 2.0
    )
    return {
        "region_id": flood_region["tile_id"],
        "deploy_point": {"x": cx, "y": cy},
        "waypoints": waypoints,
        "total_waypoints": len(waypoints),
        "altitude_range": (uav_cfg.altitude_min, uav_cfg.altitude_max),
    }


def compute_coverage_area(waypoints: List[Dict], sensor_fov_m: float = 50.0) -> float:
    # Estimate search area coverage from waypoints and sensor footprint
    if len(waypoints) < 2:
        return 0.0
    total_dist = sum(
        np.sqrt((waypoints[i]["x"] - waypoints[i - 1]["x"]) ** 2 +
                (waypoints[i]["y"] - waypoints[i - 1]["y"]) ** 2)
        for i in range(1, len(waypoints))
    )
    return float(total_dist * sensor_fov_m)


def estimate_mission_time(waypoints: List[Dict], speed_mps: float = 10.0) -> float:
    # Estimate total UAV mission duration in seconds
    total_dist = sum(
        np.sqrt((waypoints[i]["x"] - waypoints[i - 1]["x"]) ** 2 +
                (waypoints[i]["y"] - waypoints[i - 1]["y"]) ** 2)
        for i in range(1, len(waypoints))
    )
    return float(total_dist / speed_mps)
