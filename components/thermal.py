import cv2
import numpy as np
from PIL import Image
from scipy import ndimage
from sklearn.cluster import KMeans
import io

def convert_to_thermal_night_vision(pil_image):
    """
    Convert PIL image to thermal night vision format
    
    Args:
        pil_image (PIL.Image): Input PIL image
    
    Returns:
        PIL.Image: Thermal night vision converted image
    """
    try:
        # Convert PIL to OpenCV format
        img_array = np.array(pil_image)
        
        # Handle different image formats
        if len(img_array.shape) == 3:
            if img_array.shape[2] == 4:  # RGBA
                img_rgb = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
            else:  # RGB
                img_rgb = img_array
            img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        else:  # Already grayscale
            img_gray = img_array
            img_rgb = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2RGB)
        
        # Create thermal base representation
        thermal_base = create_thermal_base(img_rgb, img_gray)
        
        # Convert to thermal night vision
        thermal_night_vision = create_thermal_night_vision(thermal_base, img_rgb)
        
        # Convert back to PIL Image
        thermal_pil = Image.fromarray(thermal_night_vision)
        
        return thermal_pil
        
    except Exception as e:
        print(f"Error in thermal conversion: {e}")
        return None

def create_thermal_base(img_rgb, img_gray):
    """
    Create base thermal representation using multiple features
    
    Args:
        img_rgb (numpy.ndarray): RGB image array
        img_gray (numpy.ndarray): Grayscale image array
    
    Returns:
        numpy.ndarray: Base thermal representation
    """
    try:
        # 1. Luminance-based temperature mapping
        luminance = 0.299 * img_rgb[:,:,0] + 0.587 * img_rgb[:,:,1] + 0.114 * img_rgb[:,:,2]
        
        # 2. Edge detection for material boundaries
        edges = cv2.Canny(img_gray, 50, 150)
        edges_dilated = cv2.dilate(edges, np.ones((3,3), np.uint8), iterations=1)
        
        # 3. Texture analysis using local variance
        texture = local_variance(img_gray)
        
        # 4. Color-based material classification
        pixels = img_rgb.reshape(-1, 3)
        
        # Use K-means to identify material groups
        kmeans = KMeans(n_clusters=8, random_state=42, n_init=10)
        material_labels = kmeans.fit_predict(pixels)
        material_map = material_labels.reshape(img_rgb.shape[:2])
        
        # Assign thermal properties to each material cluster
        thermal_properties = np.array([0.2, 0.4, 0.6, 0.8, 0.3, 0.7, 0.9, 0.5])
        material_thermal = thermal_properties[material_map]
        
        # 5. Combine all features with weights
        thermal_base = (
            0.3 * (luminance / 255.0) +
            0.2 * (texture / np.max(texture) if np.max(texture) > 0 else texture) +
            0.3 * material_thermal +
            0.2 * (edges_dilated / 255.0)
        )
        
        # Apply Gaussian blur to simulate thermal diffusion
        thermal_base = ndimage.gaussian_filter(thermal_base, sigma=2.0)
        
        # Normalize to 0-1 range
        thermal_base = (thermal_base - np.min(thermal_base)) / (np.max(thermal_base) - np.min(thermal_base))
        
        return thermal_base
        
    except Exception as e:
        print(f"Error creating thermal base: {e}")
        # Return a basic luminance-based thermal if advanced processing fails
        luminance = 0.299 * img_rgb[:,:,0] + 0.587 * img_rgb[:,:,1] + 0.114 * img_rgb[:,:,2]
        return luminance / 255.0

def local_variance(img, window_size=5):
    """
    Calculate local variance for texture analysis
    
    Args:
        img (numpy.ndarray): Input grayscale image
        window_size (int): Size of the local window
    
    Returns:
        numpy.ndarray: Local variance map
    """
    try:
        kernel = np.ones((window_size, window_size), np.float32) / (window_size * window_size)
        mean = cv2.filter2D(img.astype(np.float32), -1, kernel)
        sqr_mean = cv2.filter2D((img.astype(np.float32))**2, -1, kernel)
        return sqr_mean - mean**2
    except Exception as e:
        print(f"Error calculating local variance: {e}")
        return np.zeros_like(img, dtype=np.float32)

def create_thermal_night_vision(thermal_base, img_rgb):
    """
    Create thermal night vision with black, gray, white monochrome
    
    Args:
        thermal_base (numpy.ndarray): Base thermal representation
        img_rgb (numpy.ndarray): Original RGB image
    
    Returns:
        numpy.ndarray: Thermal night vision image
    """
    try:
        # Enhance low-light details
        gamma = 0.5  # Gamma correction for night vision effect
        thermal_gamma = np.power(thermal_base, gamma)
        
        # Add noise reduction
        thermal_denoised = cv2.bilateralFilter(
            (thermal_gamma * 255).astype(np.uint8), 9, 75, 75
        ).astype(np.float32) / 255.0
        
        # Create monochrome night vision (black, gray, white)
        night_vision = np.zeros((img_rgb.shape[0], img_rgb.shape[1], 3), dtype=np.uint8)
        
        # Convert to grayscale values (0-255)
        gray_channel = (thermal_denoised * 255).astype(np.uint8)
        
        # Enhance contrast for better black/gray/white definition
        gray_channel = cv2.equalizeHist(gray_channel)
        
        # Apply the same grayscale value to all RGB channels for true monochrome
        night_vision[:,:,0] = gray_channel  # Red channel
        night_vision[:,:,1] = gray_channel  # Green channel  
        night_vision[:,:,2] = gray_channel  # Blue channel
        
        # Add subtle scanline effect for authenticity
        for i in range(0, night_vision.shape[0], 4):
            if i < night_vision.shape[0]:
                night_vision[i:i+1, :, :] = (night_vision[i:i+1, :, :] * 0.9).astype(np.uint8)
        
        return night_vision
        
    except Exception as e:
        print(f"Error creating thermal night vision: {e}")
        # Return a basic grayscale conversion if advanced processing fails
        gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)

def save_thermal_image(thermal_image, output_path):
    """
    Save thermal image to file
    
    Args:
        thermal_image (PIL.Image): Thermal image to save
        output_path (str): Output file path
    
    Returns:
        bool: Success status
    """
    try:
        thermal_image.save(output_path)
        return True
    except Exception as e:
        print(f"Error saving thermal image: {e}")
        return False

def get_thermal_image_bytes(thermal_image):
    """
    Convert thermal image to bytes for download
    
    Args:
        thermal_image (PIL.Image): Thermal image
    
    Returns:
        bytes: Image bytes
    """
    try:
        img_byte_arr = io.BytesIO()
        thermal_image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        return img_byte_arr
    except Exception as e:
        print(f"Error converting image to bytes: {e}")
        return None