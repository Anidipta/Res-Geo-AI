import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import torch
import streamlit as st
import os
import kagglehub
from pathlib import Path
from ultralytics import YOLO

# Global variable to store loaded model
_model = None

def load_yolo_model():
    """Load the YOLO model from Kaggle Hub with proper meta tensor handling"""
    global _model
    
    if _model is None:
        try:
            with st.spinner('Loading YOLO model...'):
                model_path = kagglehub.model_download("anidiptapal/thermo-mob-yolo-model/pyTorch/default")
                model_files = list(Path(model_path).glob("*.pt"))
                if not model_files:
                    st.error("No model file found in downloaded path")
                    return None
                
                model_file = str(model_files[0])
                
                # Method 1: Try direct loading with device specification
                try:
                    device = 'cuda' if torch.cuda.is_available() else 'cpu'
                    _model = YOLO(model_file)
                    _model.to_empty(device) 
                    _model.eval()
                    
                except RuntimeError as e:
                    if "meta tensor" in str(e).lower() or "cannot copy out of meta tensor" in str(e).lower():
                        st.info("Handling meta tensors in model...")
                        
                        # Method 2: Load checkpoint and handle meta tensors manually
                        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
                        
                        # Load the checkpoint
                        checkpoint = torch.load(model_file, map_location='cpu')
                        
                        # Create a new YOLO model instance
                        _model = YOLO()
                        
                        # Get the model state dict
                        if isinstance(checkpoint, dict):
                            if 'model' in checkpoint:
                                model_state = checkpoint['model']
                            elif 'state_dict' in checkpoint:
                                model_state = checkpoint['state_dict']
                            else:
                                model_state = checkpoint
                        else:
                            model_state = checkpoint
                        
                        # Handle meta tensors by moving to target device
                        if hasattr(_model, 'model') and _model.model is not None:
                            # Move model to target device first
                            _model.model = _model.model.to(device)
                            
                            # Load state dict
                            try:
                                _model.model.load_state_dict(model_state, strict=False)
                            except RuntimeError as load_error:
                                if "meta tensor" in str(load_error).lower():
                                    # Alternative: Create model on target device directly
                                    st.info("Using alternative loading method...")
                                    _model = YOLO(model_file, task='detect')
                                    _model = _model.to(device)
                                else:
                                    raise load_error
                        
                        _model.eval()
                    else:
                        raise e
                
        except Exception as e:
            
            # Method 3: Fallback - try loading without explicit device handling
            try:
                model_path = kagglehub.model_download("anidiptapal/thermo-mob-yolo-model/pyTorch/default")
                model_files = list(Path(model_path).glob("*.pt"))
                if model_files:
                    model_file = str(model_files[0])
                    _model = YOLO(model_file, task='detect')
                    # Let YOLO handle device placement automatically
                    _model.eval()
                else:
                    return None
            except Exception as fallback_error:
                st.error(f"All loading methods failed: {fallback_error}")
                return None
    
    return _model

def detect_victims_yolo(thermal_image):
    """Detect all objects in thermal image using YOLO model"""
    try:
        model = load_yolo_model()
        if model is None:
            return None, {'count': 0, 'detections': []}
        
        # Convert PIL image to numpy array
        if isinstance(thermal_image, Image.Image):
            img_array = np.array(thermal_image)
        else:
            img_array = thermal_image
        
        # Ensure image is in correct format
        if len(img_array.shape) == 3 and img_array.shape[2] == 4:  # RGBA
            img_array = img_array[:, :, :3]  # Convert to RGB
        
        with st.spinner('Running AI detection...'):
            # Run inference with error handling
            try:
                results = model(img_array, verbose=False)
            except Exception as inference_error:
                st.error(f"Inference error: {inference_error}")
                return None, {'count': 0, 'detections': []}
        
        detections = []
        detection_results = {
            'count': 0,
            'detections': []
        }
        
        if len(results) > 0:
            result = results[0]
            
            if result.boxes is not None and len(result.boxes) > 0:
                # Get detection data
                boxes = result.boxes.xyxy.cpu().numpy()
                scores = result.boxes.conf.cpu().numpy()
                class_ids = result.boxes.cls.cpu().numpy()
                
                # Get class names
                if hasattr(result, 'names') and result.names:
                    class_names = result.names
                elif hasattr(model, 'names') and model.names:
                    class_names = model.names
                else:
                    class_names = {i: f'class_{i}' for i in range(int(class_ids.max()) + 1)}
                
                for i in range(len(boxes)):
                    class_id = int(class_ids[i])
                    class_name = class_names.get(class_id, f'class_{class_id}')
                    confidence = float(scores[i])
                    box = boxes[i]
                    
                    # Include ALL detections, not just persons
                    detection_info = {
                        'bbox': [float(box[0]), float(box[1]), float(box[2]), float(box[3])],
                        'confidence': confidence,
                        'class': class_name,
                        'class_id': class_id,
                        'center_x': (float(box[0]) + float(box[2])) / 2,
                        'center_y': (float(box[1]) + float(box[3])) / 2
                    }
                    detection_results['detections'].append(detection_info)
                
                detection_results['count'] = len(detection_results['detections'])
        
        annotated_image = annotate_detections(thermal_image, detection_results['detections'])
        return annotated_image, detection_results
        
    except Exception as e:
        st.error(f"Error in detection: {e}")
        return None, {'count': 0, 'detections': []}

def annotate_detections(image, detections):
    """Annotate image with detection bounding boxes - Red for Person, Purple for others"""
    try:
        # Ensure we're working with a PIL Image
        if isinstance(image, np.ndarray):
            annotated_img = Image.fromarray(image).copy()
        else:
            annotated_img = image.copy()
            
        draw = ImageDraw.Draw(annotated_img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            try:
                font = ImageFont.load_default()
            except:
                font = None
        
        for detection in detections:
            bbox = detection['bbox']
            x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
            confidence = detection['confidence']
            class_name = detection['class']
            
            # Color coding: Red for Person, Purple for others
            if class_name.lower() == 'person':
                color = '#FF0000'  # Red
            else:
                color = '#800080'  # Purple
            
            # Draw bounding box
            draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
            
            # Label
            label = f"{class_name}: {confidence:.2f}"
            
            if font:
                try:
                    text_bbox = draw.textbbox((x1, y1-25), label, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_height = text_bbox[3] - text_bbox[1]
                except:
                    text_width, text_height = len(label) * 8, 15
            else:
                text_width, text_height = len(label) * 8, 15
            
            # Text background and text
            draw.rectangle([x1, y1-25, x1+text_width+4, y1], fill='#FFFFFF')
            if font:
                draw.text((x1+2, y1-23), label, fill='#000000', font=font)
            else:
                draw.text((x1+2, y1-15), label, fill='#000000')
            
            # Center point
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            draw.ellipse([center_x-3, center_y-3, center_x+3, center_y+3], fill=color)
        
        return annotated_img
        
    except Exception as e:
        st.error(f"Error annotating image: {e}")
        return image

def display_detection_results(detection_results, thermal_image):
    """Display simplified detection results"""
    try:
        if detection_results['count'] > 0:
            # Separate persons and other objects
            persons = [d for d in detection_results['detections'] if d['class'].lower() == 'person']
            others = [d for d in detection_results['detections'] if d['class'].lower() != 'person']
            
            with st.expander(f"🔍 Detection Results ({detection_results['count']} objects found)", expanded=True):
                
                # Show persons if any
                if persons:
                    st.markdown(f"**🚨 {len(persons)} Person(s) Detected**")
                    cols = st.columns(min(len(persons), 4))
                    
                    for i, detection in enumerate(persons):
                        with cols[i % 4]:
                            bbox = detection['bbox']
                            x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
                            
                            padding = 10
                            img_width, img_height = thermal_image.size
                            x1 = max(0, x1 - padding)
                            y1 = max(0, y1 - padding)
                            x2 = min(img_width, x2 + padding)
                            y2 = min(img_height, y2 + padding)
                            
                            cropped = thermal_image.crop((x1, y1, x2, y2))
                            st.image(cropped, caption=f"Person {i+1}", use_container_width=True)
                            st.text(f"Confidence: {detection['confidence']:.2f}")
                            st.text(f"Position: ({detection['center_x']:.0f}, {detection['center_y']:.0f})")
                
                # Show other objects if any
                if others:
                    st.markdown(f"**📦 {len(others)} Other Object(s) Detected**")
                    for i, detection in enumerate(others):
                        st.text(f"• {detection['class']}: {detection['confidence']:.2f} confidence")
                
        else:
            with st.expander("🔍 Detection Results", expanded=False):
                st.markdown("❌ No objects detected in the image.")
    
    except Exception as e:
        st.error(f"Error displaying results: {e}")

def get_detection_statistics(detection_results):
    """Get detection statistics"""
    try:
        if detection_results['count'] == 0:
            return {'total_detections': 0, 'average_confidence': 0}
        
        confidences = [d['confidence'] for d in detection_results['detections']]
        persons = [d for d in detection_results['detections'] if d['class'].lower() == 'person']
        
        stats = {
            'total_detections': detection_results['count'],
            'person_count': len(persons),
            'other_count': detection_results['count'] - len(persons),
            'average_confidence': np.mean(confidences),
            'max_confidence': np.max(confidences),
            'min_confidence': np.min(confidences)
        }
        
        return stats
        
    except Exception as e:
        st.error(f"Error calculating statistics: {e}")
        return {}