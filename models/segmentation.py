import numpy as np
import cv2
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
import streamlit as st
from config import APP_CONFIG

class SegmentationModel:
    def __init__(self):
        self.model = None
        self.input_size = APP_CONFIG["image_size"]["segmentation"]
        self.load_model()
    
    @st.cache_resource
    def load_model(_self):
        try:
            _self.model = load_model(APP_CONFIG["models"]["segmentation_path"])
            return True
        except Exception as e:
            st.warning(f"Could not load segmentation model: {e}")
            return False
    
    def preprocess_image(self, image):
        if isinstance(image, np.ndarray):
            img = cv2.resize(image, self.input_size)
        else:
            img = cv2.resize(np.array(image), self.input_size)
        
        img = img_to_array(img)
        img = np.expand_dims(img, axis=0)
        img = img / 255.0
        return img
    
    def predict(self, image):
        if self.model is None:
            return self.mock_prediction(image)
        
        preprocessed = self.preprocess_image(image)
        prediction = self.model.predict(preprocessed, verbose=0)
        return np.argmax(prediction[0], axis=-1)
    
    def mock_prediction(self, image):
        h, w = self.input_size
        mock_mask = np.zeros((h, w), dtype=np.uint8)
        
        water_regions = [
            (slice(50, 150), slice(100, 200)),
            (slice(180, 220), slice(50, 120))
        ]
        
        for region in water_regions:
            mock_mask[region] = 1
        
        return mock_mask
    
    def visualize_segmentation(self, image, mask):
        overlay = image.copy()
        water_mask = (mask == 1)
        overlay[water_mask] = [0, 100, 255]
        
        result = cv2.addWeighted(image, 0.7, overlay, 0.3, 0)
        return result