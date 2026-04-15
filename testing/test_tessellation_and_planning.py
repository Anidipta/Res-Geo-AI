"""Tests for spatial tessellation, tile filtering, and flight path planning."""

import numpy as np
import os
import sys
import json
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from satellite.tessellation import (
    compute_mbr, tessellate_grid, filter_valid_tiles,
    get_tile_centroid, load_region_polygons
)
from uav.flight_planner import (
    generate_spiral_path, plan_uav_mission,
    compute_coverage_area, estimate_mission_time
)
from utils.metrics import (
    compute_iou, compute_miou, compute_f1,
    compute_mpr, compute_detection_metrics, compute_gps_localization_error
)


def _write_temp_geojson(polygons):
    # Write a temporary GeoJSON file with given polygon list and return path
    features = [{"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [poly]}, "properties": {}}
                for poly in polygons]
    data = {"type": "FeatureCollection", "features": features}
    tmp = tempfile.NamedTemporaryFile(suffix=".geojson", mode="w", delete=False)
    json.dump(data, tmp)
    tmp.close()
    return tmp.name


def test_compute_mbr():
    # MBR should exactly bound the given polygon vertices
    polys = [[(0, 0), (10, 0), (10, 10), (0, 10)]]
    xmin, xmax, ymin, ymax = compute_mbr(polys)
    assert xmin == 0 and xmax == 10 and ymin == 0 and ymax == 10
    print("[PASS] test_compute_mbr")


def test_tessellate_grid_count():
    # n×n grid should produce exactly n*n tiles
    tiles = tessellate_grid(0, 10, 0, 10, n=4)
    assert len(tiles) == 16, f"Expected 16, got {len(tiles)}"
    print("[PASS] test_tessellate_grid_count")


def test_filter_valid_tiles():
    # Only tiles intersecting the polygon should be retained
    tiles = tessellate_grid(0, 10, 0, 10, n=10)
    polygon = [[(2.0, 2.0), (4.0, 2.0), (4.0, 4.0), (2.0, 4.0), (2.0, 2.0)]]
    valid = filter_valid_tiles(tiles, polygon)
    assert len(valid) > 0, "Expected at least one valid tile"
    assert len(valid) < len(tiles), "Expected fewer valid tiles than total"
    print(f"[PASS] test_filter_valid_tiles — {len(valid)}/{len(tiles)} valid")


def test_load_region_polygons():
    # GeoJSON polygons should parse correctly from temp file
    polygon = [[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]
    path = _write_temp_geojson([polygon])
    polys = load_region_polygons(path)
    os.unlink(path)
    assert len(polys) == 1
    assert len(polys[0]) == 5
    print("[PASS] test_load_region_polygons")


def test_get_tile_centroid():
    # Centroid of unit tile should be (0.5, 0.5)
    tile = {"xmin": 0.0, "xmax": 1.0, "ymin": 0.0, "ymax": 1.0}
    cx, cy = get_tile_centroid(tile)
    assert abs(cx - 0.5) < 1e-6 and abs(cy - 0.5) < 1e-6
    print("[PASS] test_get_tile_centroid")


def test_spiral_path_generation():
    # Spiral path should have more than 10 waypoints and all at specified altitude
    wps = generate_spiral_path(0.0, 0.0, radius_step=5.0, angular_step=0.1,
                                max_radius=100.0, altitude=80.0)
    assert len(wps) > 10
    assert all(abs(wp["altitude"] - 80.0) < 1e-6 for wp in wps)
    print(f"[PASS] test_spiral_path_generation — {len(wps)} waypoints")


def test_coverage_area_estimation():
    # Coverage area should be positive for a non-trivial path
    wps = generate_spiral_path(0.0, 0.0, radius_step=5.0, max_radius=50.0)
    area = compute_coverage_area(wps, sensor_fov_m=30.0)
    assert area > 0.0
    print(f"[PASS] test_coverage_area_estimation — area={area:.1f} m²")


def test_mission_time_estimate():
    # Mission time must be positive and scale with path length
    wps = generate_spiral_path(0.0, 0.0, radius_step=5.0, max_radius=50.0)
    t = estimate_mission_time(wps, speed_mps=10.0)
    assert t > 0.0
    print(f"[PASS] test_mission_time_estimate — time={t:.1f}s")


def test_iou_metric():
    # Perfect prediction should yield IoU=1, no overlap should yield IoU=0
    pred = np.array([[0, 1, 1], [0, 0, 2]])
    true = np.array([[0, 1, 1], [0, 0, 2]])
    assert abs(compute_iou(pred, true, class_id=1) - 1.0) < 1e-6
    blank_pred = np.zeros((2, 3), dtype=int)
    assert compute_iou(blank_pred, true, class_id=1) == 0.0
    print("[PASS] test_iou_metric")


def test_f1_and_mpr():
    # F1 and MPR should be correctly computed from known TP/FP/FN values
    prec = compute_f1(0.8, 0.8)
    assert abs(prec - 0.8) < 1e-6
    mpr = compute_mpr(tp_person=80, fn_person=20)
    assert abs(mpr - 0.2) < 1e-6
    print("[PASS] test_f1_and_mpr")


def test_detection_metrics_perfect():
    # Perfect detections with exact GT boxes should give F1=1.0
    boxes = [{"bbox": [10, 10, 50, 50], "class_name": "Person"}]
    dets = [{"bbox": [10, 10, 50, 50], "confidence": 0.9, "class_name": "Person"}]
    metrics = compute_detection_metrics(dets, boxes, iou_threshold=0.5)
    assert metrics["f1"] == 1.0, f"Expected F1=1.0, got {metrics['f1']}"
    print("[PASS] test_detection_metrics_perfect")


if __name__ == "__main__":
    test_compute_mbr()
    test_tessellate_grid_count()
    test_filter_valid_tiles()
    test_load_region_polygons()
    test_get_tile_centroid()
    test_spiral_path_generation()
    test_coverage_area_estimation()
    test_mission_time_estimate()
    test_iou_metric()
    test_f1_and_mpr()
    test_detection_metrics_perfect()
    print("\nAll tessellation/planning/metrics tests completed.")
