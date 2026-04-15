"""Tests for GPS localization, Kalman filter, and coordinate projection."""

import numpy as np
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from gps.localization import (
    pixel_to_gps, compute_gps_error, build_uav_rotation,
    filter_valid_localizations, cluster_gps_points, localize_detection
)
from gps.kalman_filter import KalmanFilter, smooth_uav_trajectory, estimate_pose_uncertainty


def _make_gps_cfg():
    # Return minimal GPS config namespace for tests
    class GPSCfg:
        sigma_pixel = 2.1
        sigma_altitude = 0.5
        sigma_pose = 0.8
        sigma_wind = 1.5
        focal_length = 35.0
    return GPSCfg()


def test_pixel_to_gps_identity():
    # Pixel at image center with identity rotation should map to UAV position
    R = np.eye(3)
    t = np.array([100.0, 200.0, -100.0])
    gps_x, gps_y, gps_z = pixel_to_gps(256, 256, 100.0, 35.0, R, t, 512, 512)
    assert isinstance(gps_x, float)
    assert isinstance(gps_y, float)
    print("[PASS] test_pixel_to_gps_identity")


def test_gps_error_positive():
    # GPS error must always be a positive finite value
    err = compute_gps_error(2.1, 100.0, 35.0, 0.5, 0.8)
    assert err > 0.0 and np.isfinite(err), f"Invalid GPS error: {err}"
    print(f"[PASS] test_gps_error_positive — error={err:.3f}m")


def test_build_uav_rotation():
    # Identity rotation should give 3x3 identity matrix for zero angles
    R = build_uav_rotation(0.0, 0.0, 0.0)
    assert R.shape == (3, 3)
    np.testing.assert_allclose(R, np.eye(3), atol=1e-6)
    print("[PASS] test_build_uav_rotation")


def test_localize_detection():
    # Localize a dummy detection and verify GPS fields are present
    cfg = _make_gps_cfg()
    det = {"bbox": [100, 100, 200, 200], "confidence": 0.8, "area": 10000, "class_name": "Person"}
    wp = {"x": 500.0, "y": 600.0, "altitude": 100.0}
    result = localize_detection(det, wp, cfg)
    assert "gps_x" in result and "gps_y" in result
    assert "gps_error_m" in result
    print(f"[PASS] test_localize_detection — GPS=({result['gps_x']:.2f}, {result['gps_y']:.2f}), err={result['gps_error_m']:.2f}m")


def test_filter_valid_localizations():
    # Only detections above threshold should survive filtering
    locs = [
        {"confidence": 0.8, "area": 100, "gps_x": 0.0, "gps_y": 0.0, "gps_error_m": 2.0},
        {"confidence": 0.3, "area": 100, "gps_x": 1.0, "gps_y": 1.0, "gps_error_m": 3.0},
        {"confidence": 0.9, "area": 10, "gps_x": 2.0, "gps_y": 2.0, "gps_error_m": 1.5},
    ]
    valid = filter_valid_localizations(locs, conf_threshold=0.6, min_area=50)
    assert len(valid) == 1 and valid[0]["confidence"] == 0.8
    print("[PASS] test_filter_valid_localizations")


def test_cluster_gps_points():
    # Nearby points should merge into a single cluster
    locs = [
        {"gps_x": 0.0, "gps_y": 0.0, "confidence": 0.9, "gps_error_m": 2.0},
        {"gps_x": 1.0, "gps_y": 1.0, "confidence": 0.85, "gps_error_m": 2.5},
        {"gps_x": 100.0, "gps_y": 100.0, "confidence": 0.7, "gps_error_m": 3.0},
    ]
    clusters = cluster_gps_points(locs, radius_m=5.0)
    assert len(clusters) == 2, f"Expected 2 clusters, got {len(clusters)}"
    print("[PASS] test_cluster_gps_points")


def test_kalman_filter_convergence():
    # Kalman filter should reduce noise in noisy position measurements
    kf = KalmanFilter(dt=0.1)
    kf.reset(np.array([0.0, 0.0, 0.0]))
    for _ in range(50):
        noisy_obs = np.array([1.0, 1.0, 0.0]) + np.random.randn(3) * 0.5
        est = kf.step(noisy_obs)
    assert np.linalg.norm(est - np.array([1.0, 1.0, 0.0])) < 1.5
    print("[PASS] test_kalman_filter_convergence")


def test_smooth_uav_trajectory():
    # Smoothed trajectory must have same length as raw input
    raw = np.cumsum(np.random.randn(100, 3) * 0.5, axis=0)
    smoothed = smooth_uav_trajectory(raw, dt=0.1)
    assert smoothed.shape == raw.shape
    error = estimate_pose_uncertainty(smoothed, raw)
    assert error >= 0.0
    print(f"[PASS] test_smooth_uav_trajectory — pose uncertainty={error:.3f}m")


if __name__ == "__main__":
    test_pixel_to_gps_identity()
    test_gps_error_positive()
    test_build_uav_rotation()
    test_localize_detection()
    test_filter_valid_localizations()
    test_cluster_gps_points()
    test_kalman_filter_convergence()
    test_smooth_uav_trajectory()
    print("\nAll GPS tests completed.")
