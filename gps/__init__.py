"""GPS module: pixel-to-GPS projection, Kalman filtering, clustering, and localization."""
from gps.localization import run_gps_localization, localize_detection, cluster_gps_points
from gps.kalman_filter import KalmanFilter, smooth_uav_trajectory
