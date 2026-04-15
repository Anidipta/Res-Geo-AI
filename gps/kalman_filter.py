"""Kalman filter for smoothing UAV pose estimates and reducing localization error."""

import numpy as np
from typing import Tuple


class KalmanFilter:
    # 6-DOF Kalman filter tracking UAV position and velocity
    def __init__(self, dt: float = 0.1, sigma_process: float = 0.5, sigma_obs: float = 0.8):
        self.dt = dt
        # State: [x, y, z, vx, vy, vz]
        self.x = np.zeros(6, dtype=np.float64)
        # State transition matrix
        self.F = np.eye(6)
        self.F[0, 3] = dt
        self.F[1, 4] = dt
        self.F[2, 5] = dt
        # Observation matrix (observe position only)
        self.H = np.eye(3, 6)
        # Process noise covariance
        self.Q = np.eye(6) * sigma_process ** 2
        # Observation noise covariance
        self.R = np.eye(3) * sigma_obs ** 2
        # Error covariance
        self.P = np.eye(6) * 1.0

    def predict(self) -> np.ndarray:
        # Kalman predict step: propagate state and error covariance forward
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q
        return self.x[:3]

    def update(self, observation: np.ndarray) -> np.ndarray:
        # Kalman update step: incorporate GPS observation into state estimate
        y = observation - self.H @ self.x
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)
        self.x = self.x + K @ y
        self.P = (np.eye(6) - K @ self.H) @ self.P
        return self.x[:3]

    def step(self, observation: np.ndarray) -> np.ndarray:
        # Combined predict + update for one time step
        self.predict()
        return self.update(observation)

    def reset(self, initial_pos: np.ndarray):
        # Reset filter state to a known initial UAV position
        self.x[:3] = initial_pos
        self.x[3:] = 0.0
        self.P = np.eye(6) * 1.0


def smooth_uav_trajectory(raw_positions: np.ndarray, dt: float = 0.1) -> np.ndarray:
    # Apply Kalman filter across all raw UAV position measurements
    kf = KalmanFilter(dt=dt)
    kf.reset(raw_positions[0])
    smoothed = []
    for pos in raw_positions:
        filtered_pos = kf.step(pos)
        smoothed.append(filtered_pos.copy())
    return np.array(smoothed)


def estimate_pose_uncertainty(smoothed: np.ndarray, raw: np.ndarray) -> float:
    # Compute RMS difference between smoothed and raw to quantify pose noise
    diff = smoothed - raw
    return float(np.sqrt((diff ** 2).mean()))
