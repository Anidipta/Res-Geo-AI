import numpy as np
import cv2
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.applications.xception import preprocess_input
import streamlit as st
from config import APP_CONFIG

class FloodDetectionModel:
    def __init__(self):
        self.model = None
        self.input_size = APP_CONFIG["image_size"]["flood_detection"]
        self.load_model()
    
    @st.cache_resource
    def load_model(_self):
        try:
            _self.model = load_model(APP_CONFIG["models"]["flood_detection_path"])
            return True
        except Exception as e:
            st.warning(f"Could not load flood detection model: {e}")
            return False
    
    def preprocess_image(self, image):
        if isinstance(image, np.ndarray):
            img = cv2.resize(image, self.input_size)
        else:
            img = cv2.resize(np.array(image), self.input_size)
        
        img = img_to_array(img)
        img = np.expand_dims(img, axis=0)
        img = preprocess_input(img)
        return img
    
    def predict(self, image):
        if self.model is None:
            return self.mock_prediction(image)
        
        preprocessed = self.preprocess_image(image)
        prediction = self.model.predict(preprocessed, verbose=0)
        return float(prediction[0][0])
    
    def mock_prediction(self, image):
        img_array = np.array(image) if not isinstance(image, np.ndarray) else image
        
        blue_channel = img_array[:, :, 2] if len(img_array.shape) == 3 else img_array
        water_ratio = np.mean(blue_channel > 120) / 255.0
        
        flood_probability = min(0.9, water_ratio * 1.5 + np.random.normal(0, 0.1))
        return max(0.1, flood_probability)
    
    def get_flood_severity(self, prediction_score):
        if prediction_score < 0.3:
            return "Low Risk", "green"
        elif prediction_score < 0.6:
            return "Medium Risk", "orange"
        else:
            return "High Risk", "red"