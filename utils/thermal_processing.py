import cv2
import numpy as np
from scipy import ndimage
from sklearn.cluster import KMeans

def create_thermal_night_vision(image):
    if isinstance(image, list):
        image = np.array(image)
    
    if len(image.shape) == 3:
        img_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        img_rgb = image
    else:
        img_gray = image
        img_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    
    thermal_base = create_thermal_base(img_rgb, img_gray)
    night_vision = create_night_vision_from_thermal(thermal_base, img_rgb)
    
    return night_vision

def create_thermal_base(img_rgb, img_gray):
    luminance = 0.299 * img_rgb[:,:,0] + 0.587 * img_rgb[:,:,1] + 0.114 * img_rgb[:,:,2]
    
    edges = cv2.Canny(img_gray, 50, 150)
    edges_dilated = cv2.dilate(edges, np.ones((3,3), np.uint8), iterations=1)
    
    texture = local_variance(img_gray)
    
    pixels = img_rgb.reshape(-1, 3)
    kmeans = KMeans(n_clusters=8, random_state=42, n_init=10)
    material_labels = kmeans.fit_predict(pixels)
    material_map = material_labels.reshape(img_rgb.shape[:2])
    
    thermal_properties = np.array([0.2, 0.4, 0.6, 0.8, 0.3, 0.7, 0.9, 0.5])
    material_thermal = thermal_properties[material_map]
    
    thermal_base = (
        0.3 * (luminance / 255.0) +
        0.2 * (texture / np.max(texture)) +
        0.3 * material_thermal +
        0.2 * (edges_dilated / 255.0)
    )
    
    thermal_base = ndimage.gaussian_filter(thermal_base, sigma=2.0)
    thermal_base = (thermal_base - np.min(thermal_base)) / (np.max(thermal_base) - np.min(thermal_base))
    
    return thermal_base

def local_variance(img, window_size=5):
    kernel = np.ones((window_size, window_size), np.float32) / (window_size * window_size)
    mean = cv2.filter2D(img.astype(np.float32), -1, kernel)
    sqr_mean = cv2.filter2D((img.astype(np.float32))**2, -1, kernel)
    return sqr_mean - mean**2

def create_night_vision_from_thermal(thermal_base, img_rgb):
    gamma = 0.5
    thermal_gamma = np.power(thermal_base, gamma)
    
    thermal_denoised = cv2.bilateralFilter(
        (thermal_gamma * 255).astype(np.uint8), 9, 75, 75
    ).astype(np.float32) / 255.0
    
    night_vision = np.zeros((img_rgb.shape[0], img_rgb.shape[1], 3), dtype=np.uint8)
    
    gray_channel = (thermal_denoised * 255).astype(np.uint8)
    gray_channel = cv2.equalizeHist(gray_channel)
    
    night_vision[:,:,0] = gray_channel
    night_vision[:,:,1] = gray_channel
    night_vision[:,:,2] = gray_channel
    
    for i in range(0, night_vision.shape[0], 4):
        night_vision[i:i+1, :, :] = (night_vision[i:i+1, :, :] * 0.9).astype(np.uint8)
    
    return night_vision