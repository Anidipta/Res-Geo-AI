import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import requests
import os
import tempfile
from ultralytics import YOLO
import io

# Global variable to store the model
_model = None

def load_yolo_model():
    """
    Load the YOLO model from HuggingFace
    
    Returns:
        YOLO: Loaded YOLO model or None if failed
    """
    global _model
    
    if _model is not None:
        return _model
    
    try:
        # HuggingFace model URL
        model_url = "https://huggingface.co/ANI00/Victim-Localisation/resolve/main/best.pt"
        
        # Create a temporary file to store the model
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pt') as tmp_file:
            model_path = tmp_file.name
        
        # Download the model with progress
        with st.spinner('Downloading victim detection model... This may take a few moments.'):
            response = requests.get(model_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(model_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
        
        # Load the YOLO model
        _model = YOLO(model_path)
        
        # Clean up the temporary file
        try:
            os.unlink(model_path)
        except:
            pass  # Ignore cleanup errors
        
        st.success("Model loaded successfully!")
        return _model
        
    except Exception as e:
        st.error(f"Error loading YOLO model: {e}")
        return None

def detect_victims_yolo(thermal_image):
    """
    Detect victims in thermal image using YOLO model
    
    Args:
        thermal_image (PIL.Image): Input thermal image
    
    Returns:
        tuple: (detected_image_pil, detection_results)
    """
    try:
        # Load the YOLO model
        model = load_yolo_model()
        if model is None:
            return None, {"count": 0, "boxes": [], "confidences": []}
        
        # Convert PIL to numpy array
        img_array = np.array(thermal_image)
        
        # Run YOLO detection
        with st.spinner('Detecting victims...'):
            results = model(img_array, conf=0.3, iou=0.5)
        
        # Process detection results
        detection_results = {
            "count": 0,
            "boxes": [],
            "confidences": [],
            "class_names": []
        }
        
        detected_image = img_array.copy()
        
        if results and len(results) > 0:
            # Get the first result (single image)
            result = results[0]
            
            if result.boxes is not None and len(result.boxes) > 0:
                boxes = result.boxes.xyxy.cpu().numpy()  # x1, y1, x2, y2
                confidences = result.boxes.conf.cpu().numpy()
                class_ids = result.boxes.cls.cpu().numpy()
                
                detection_results["count"] = len(boxes)
                detection_results["boxes"] = boxes.tolist()
                detection_results["confidences"] = confidences.tolist()
                
                # Draw bounding boxes on the image
                detected_image = draw_detection_boxes(
                    detected_image, 
                    boxes, 
                    confidences, 
                    class_ids,
                    model.names if hasattr(model, 'names') else {0: 'victim'}
                )
                
                # Store class names
                detection_results["class_names"] = [
                    model.names.get(int(cls_id), 'victim') if hasattr(model, 'names') 
                    else 'victim' for cls_id in class_ids
                ]
        
        # Convert back to PIL Image
        detected_image_pil = Image.fromarray(detected_image)
        
        return detected_image_pil, detection_results
        
    except Exception as e:
        st.error(f"Error in victim detection: {e}")
        return None, {"count": 0, "boxes": [], "confidences": []}

def draw_detection_boxes(image, boxes, confidences, class_ids, class_names):
    """
    Draw bounding boxes and labels on the image
    
    Args:
        image (numpy.ndarray): Input image
        boxes (numpy.ndarray): Bounding boxes
        confidences (numpy.ndarray): Confidence scores
        class_ids (numpy.ndarray): Class IDs
        class_names (dict): Class ID to name mapping
    
    Returns:
        numpy.ndarray: Image with drawn boxes
    """
    try:
        # Convert to PIL for better text rendering
        pil_image = Image.fromarray(image)
        draw = ImageDraw.Draw(pil_image)
        
        # Define colors for different detection confidence levels
        colors = [
            (255, 0, 0),    # Red for high confidence
            (255, 165, 0),  # Orange for medium confidence
            (255, 255, 0),  # Yellow for lower confidence
        ]
        
        for i, (box, conf, cls_id) in enumerate(zip(boxes, confidences, class_ids)):
            x1, y1, x2, y2 = map(int, box)
            
            # Choose color based on confidence
            if conf > 0.7:
                color = colors[0]  # Red
            elif conf > 0.5:
                color = colors[1]  # Orange
            else:
                color = colors[2]  # Yellow
            
            # Draw bounding box
            draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
            
            # Prepare label text
            class_name = class_names.get(int(cls_id), 'victim')
            label = f"{class_name}: {conf:.2f}"
            
            # Calculate text size and draw background
            try:
                # Try to use a better font if available
                font = ImageFont.truetype("arial.ttf", 16)
            except:
                # Fallback to default font
                font = ImageFont.load_default()
            
            # Get text bounding box
            bbox = draw.textbbox((0, 0), label, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Draw text background
            draw.rectangle([x1, y1 - text_height - 4, x1 + text_width + 4, y1], 
                         fill=color, outline=color)
            
            # Draw text
            draw.text((x1 + 2, y1 - text_height - 2), label, fill=(255, 255, 255), font=font)
            
            # Add victim number
            victim_number = f"V{i+1}"
            number_bbox = draw.textbbox((0, 0), victim_number, font=font)
            number_width = number_bbox[2] - number_bbox[0]
            number_height = number_bbox[3] - number_bbox[1]
            
            # Draw victim number in bottom-right of box
            draw.rectangle([x2 - number_width - 4, y2 - number_height - 4, x2, y2], 
                         fill=color, outline=color)
            draw.text((x2 - number_width - 2, y2 - number_height - 2), 
                     victim_number, fill=(255, 255, 255), font=font)
        
        # Convert back to numpy array
        return np.array(pil_image)
        
    except Exception as e:
        print(f"Error drawing detection boxes: {e}")
        # Fallback to OpenCV drawing if PIL fails
        return draw_boxes_opencv(image, boxes, confidences, class_ids, class_names)

def draw_boxes_opencv(image, boxes, confidences, class_ids, class_names):
    """
    Fallback function to draw boxes using OpenCV
    
    Args:
        image (numpy.ndarray): Input image
        boxes (numpy.ndarray): Bounding boxes
        confidences (numpy.ndarray): Confidence scores
        class_ids (numpy.ndarray): Class IDs
        class_names (dict): Class ID to name mapping
    
    Returns:
        numpy.ndarray: Image with drawn boxes
    """
    try:
        result_image = image.copy()
        
        # Define colors
        colors = [(255, 0, 0), (255, 165, 0), (255, 255, 0)]
        
        for i, (box, conf, cls_id) in enumerate(zip(boxes, confidences, class_ids)):
            x1, y1, x2, y2 = map(int, box)
            
            # Choose color based on confidence
            if conf > 0.7:
                color = colors[0]
            elif conf > 0.5:
                color = colors[1]
            else:
                color = colors[2]
            
            # Draw bounding box
            cv2.rectangle(result_image, (x1, y1), (x2, y2), color, 2)
            
            # Prepare label
            class_name = class_names.get(int(cls_id), 'victim')
            label = f"{class_name}: {conf:.2f}"
            
            # Draw label background
            (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(result_image, (x1, y1 - text_height - 10), 
                         (x1 + text_width, y1), color, -1)
            
            # Draw label text
            cv2.putText(result_image, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Draw victim number
            victim_number = f"V{i+1}"
            cv2.putText(result_image, victim_number, 
                       (x2 - 30, y2 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        return result_image
    except Exception as e:
        print(f"Error in OpenCV drawing: {e}")
        return image
    