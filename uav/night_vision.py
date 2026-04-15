"""RGB-to-night-vision transformation for improved low-light victim detection."""

import numpy as np
import cv2
from typing import Tuple


def rgb_to_luminance(img: np.ndarray) -> np.ndarray:
    # Convert RGB image to luminance channel using ITU-R BT.601 coefficients
    return 0.299 * img[:, :, 0] + 0.587 * img[:, :, 1] + 0.114 * img[:, :, 2]


def compute_adaptive_gamma(luminance: np.ndarray, gamma_min: float = 0.3, gamma_max: float = 0.7) -> float:
    # Derive adaptive gamma from scene mean luminance; darker scenes get lower gamma
    mean_lum = luminance.mean() / 255.0
    return gamma_max - (gamma_max - gamma_min) * mean_lum


def apply_gamma_correction(luminance: np.ndarray, gamma: float) -> np.ndarray:
    # Apply gamma correction formula: I_night = (L / L_max)^gamma * L_max
    lmax = float(luminance.max()) if luminance.max() > 0 else 1.0
    return np.power(luminance / lmax, gamma) * lmax


def luminance_to_night_vision(luminance: np.ndarray, gamma: float) -> np.ndarray:
    # Apply adaptive gamma and map grayscale luminance to green-tinted night vision
    corrected = apply_gamma_correction(luminance, gamma).astype(np.uint8)
    night_bgr = np.zeros((*corrected.shape, 3), dtype=np.uint8)
    night_bgr[:, :, 1] = corrected
    return night_bgr


def rgb_to_thermal(img: np.ndarray) -> np.ndarray:
    # Convert RGB to pseudo-thermal image using CLAHE + colormap
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    thermal = cv2.applyColorMap(enhanced, cv2.COLORMAP_INFERNO)
    return thermal


def rgb_to_infrared(img: np.ndarray) -> np.ndarray:
    # Simulate near-infrared by boosting red channel and applying HOT colormap
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(np.float32)
    nir_sim = np.clip(gray + img[:, :, 0].astype(np.float32) * 0.5, 0, 255).astype(np.uint8)
    return cv2.applyColorMap(nir_sim, cv2.COLORMAP_HOT)


def transform_to_night_vision(img_rgb: np.ndarray, gamma_min: float = 0.3, gamma_max: float = 0.7) -> np.ndarray:
    # Full pipeline: RGB → luminance → adaptive gamma → night vision image
    luminance = rgb_to_luminance(img_rgb.astype(np.float32))
    gamma = compute_adaptive_gamma(luminance, gamma_min, gamma_max)
    return luminance_to_night_vision(luminance.astype(np.uint8), gamma)


def remove_cloud_artifacts(img: np.ndarray, threshold: int = 220) -> np.ndarray:
    # Mask near-white cloud pixels to reduce false detections in bright regions
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY) if img.ndim == 3 else img
    cloud_mask = gray > threshold
    result = img.copy()
    if img.ndim == 3:
        result[cloud_mask] = 0
    else:
        result[cloud_mask] = 0
    return result


def preprocess_for_detection(img_rgb: np.ndarray, mode: str = "night_vision",
                              gamma_min: float = 0.3, gamma_max: float = 0.7) -> np.ndarray:
    # Apply selected imaging modality transformation for detector input
    cleaned = remove_cloud_artifacts(img_rgb)
    if mode == "night_vision":
        return transform_to_night_vision(cleaned, gamma_min, gamma_max)
    elif mode == "thermal":
        return rgb_to_thermal(cleaned)
    elif mode == "infrared":
        return rgb_to_infrared(cleaned)
    else:
        return cleaned
