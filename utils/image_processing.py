import numpy as np
import cv2
import requests
from PIL import Image
import io
import streamlit as st

def process_satellite_image(lat, lng, zoom=16, size=512):
    try:
        satellite_img = fetch_satellite_image(lat, lng, zoom, size)
        if satellite_img is not None:
            return preprocess_image(satellite_img)
        else:
            return generate_mock_satellite_image(size)
    except Exception as e:
        st.warning(f"Error processing satellite image: {e}")
        return generate_mock_satellite_image(size)

def fetch_satellite_image(lat, lng, zoom, size):
    try:
        url = f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/{lng},{lat},{zoom}/{size}x{size}@2x?access_token=YOUR_MAPBOX_TOKEN"
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            image = Image.open(io.BytesIO(response.content))
            return np.array(image)
        else:
            return None
    except Exception as e:
        print(f"Error fetching satellite image: {e}")
        return None

def generate_mock_satellite_image(size=512):
    """Generate a mock satellite image for testing"""
    img = np.random.randint(50, 200, (size, size, 3), dtype=np.uint8)
    
    # Add some water-like regions (blue areas)
    water_regions = [
        (slice(100, 200), slice(150, 300)),
        (slice(300, 400), slice(100, 250))
    ]
    
    for region in water_regions:
        img[region] = [30, 100, 180]  # Blue-ish color for water
    
    # Add some land features
    img = cv2.GaussianBlur(img, (5, 5), 0)
    
    return img

def preprocess_image(image):
    """Preprocess image for model input"""
    if len(image.shape) == 3 and image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
    
    # Normalize pixel values
    image = image.astype(np.float32) / 255.0
    image = (image * 255).astype(np.uint8)
    
    return image

def resize_image(image, target_size):
    """Resize image to target size"""
    if isinstance(image, np.ndarray):
        return cv2.resize(image, target_size)
    else:
        return np.array(Image.fromarray(image).resize(target_size))

def enhance_contrast(image):
    """Enhance image contrast"""
    lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    l = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)).apply(l)
    enhanced = cv2.merge([l, a, b])
    return cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)