import numpy as np
import cv2
import torch
import streamlit as st
from config import APP_CONFIG

class PersonDetectionModel:
    def __init__(self):
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.confidence_threshold = APP_CONFIG["thresholds"]["person_confidence"]
        self.load_model()
    
    @st.cache_resource
    def load_model(_self):
        try:
            _self.model = torch.hub.load('ultralytics/yolov5', 'custom', 
                                        path=APP_CONFIG["models"]["person_detection_path"],
                                        force_reload=True)
            _self.model.to(_self.device)
            return True
        except Exception as e:
            st.warning(f"Could not load person detection model: {e}")
            return False
    
    def predict(self, image):
        if self.model is None:
            return self.mock_prediction(image)
        
        results = self.model(image)
        detections = []
        
        for *box, conf, cls in results.xyxy[0].cpu().numpy():
            if int(cls) == 0 and conf > self.confidence_threshold:  # Person class
                x1, y1, x2, y2 = map(int, box)
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                
                detections.append({
                    'bbox': [x1, y1, x2, y2],
                    'center': [center_x, center_y],
                    'confidence': float(conf)
                })
        
        return detections
    
    def mock_prediction(self, image):
        h, w = image.shape[:2]
        num_persons = np.random.randint(0, 4)
        detections = []
        
        for i in range(num_persons):
            x1 = np.random.randint(0, w - 50)
            y1 = np.random.randint(0, h - 50)
            x2 = x1 + np.random.randint(30, 80)
            y2 = y1 + np.random.randint(40, 100)
            
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            
            detections.append({
                'bbox': [x1, y1, x2, y2],
                'center': [center_x, center_y],
                'confidence': np.random.uniform(0.6, 0.9)
            })
        
        return detections
    
    def draw_detections(self, image, detections):
        result_img = image.copy()
        
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            conf = detection['confidence']
            
            cv2.rectangle(result_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(result_img, f'Person {conf:.2f}', 
                       (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            center_x, center_y = detection['center']
            cv2.circle(result_img, (center_x, center_y), 5, (255, 0, 0), -1)
        
        return result_img