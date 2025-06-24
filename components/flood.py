import os
import torch
import numpy as np
from PIL import Image
from transformers import AutoImageProcessor, SegformerForSemanticSegmentation
import shutil

# Initialize model and processor
def initialize_flood_model():
    """Initialize the Segformer model for flood prediction"""
    try:
        processor = AutoImageProcessor.from_pretrained("wu-pr-gw/segformer-b2-finetuned-with-LoveDA")
        model = SegformerForSemanticSegmentation.from_pretrained("wu-pr-gw/segformer-b2-finetuned-with-LoveDA")
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        model.eval()
        
        return processor, model, device
    except Exception as e:
        print(f"Error initializing model: {e}")
        return None, None, None

# LoveDA dataset classes (8 classes)
CLASS_NAMES = ['No Data', 'Background', 'Building', 'Road', 'Water', 'Barren', 'Forest', 'Agricultural']
NUM_CLASSES = 8

# Color mapping for visualization
COLORS = np.array([
    [0, 0, 0],         # 0: no data
    [255, 255, 255],   # 1: background
    [255, 0, 0],       # 2: building
    [255, 255, 0],     # 3: road
    [0, 26, 255],      # 4: water
    [77, 86, 99],      # 5: barren
    [4, 107, 0],       # 6: forest
    [255, 123, 0]      # 7: agricultural
])

def predict_single_image(image_path, processor, model, device):
    """Predict segmentation for a single image"""
    try:
        # Load and preprocess image
        image = Image.open(image_path).convert('RGB')
        inputs = processor(images=image, return_tensors="pt")
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Make prediction
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            
            # Resize logits to match input image size
            upsampled_logits = torch.nn.functional.interpolate(
                logits,
                size=image.size[::-1],  # PIL size is (width, height), we need (height, width)
                mode="bilinear",
                align_corners=False,
            )
            
            # Get predicted segmentation
            predicted = upsampled_logits.argmax(dim=1).squeeze().cpu().numpy()
            
        return predicted, image
    
    except Exception as e:
        print(f"Error predicting image {image_path}: {e}")
        return None, None

def calculate_water_percentage(prediction):
    """Calculate the percentage of water pixels in the prediction"""
    if prediction is None:
        return 0.0
    
    total_pixels = prediction.size
    water_pixels = np.sum(prediction == 4)  # Water class is index 4
    water_percentage = (water_pixels / total_pixels) * 100
    
    return water_percentage

def create_prediction_visualization(prediction):
    """Create a colored visualization of the prediction"""
    if prediction is None:
        return None
    
    # Create colored prediction
    colored_prediction = COLORS[prediction]
    prediction_image = Image.fromarray(colored_prediction.astype(np.uint8))
    
    return prediction_image

def process_flood_prediction(input_dir, state_name, progress_callback=None):
    """Process all images in the input directory for flood prediction"""
    
    # Initialize model
    processor, model, device = initialize_flood_model()
    if not processor or not model:
        return {"error": "Failed to initialize model", "flooded_images": [], "all_predictions": []}
    
    # Create flooded images directory
    flooded_dir = f"output/flooded/{state_name.replace(' ', '_')}"
    os.makedirs(flooded_dir, exist_ok=True)
    
    # Get all image files
    image_files = [f for f in os.listdir(input_dir) if f.endswith('.png')]
    total_images = len(image_files)
    
    if total_images == 0:
        return {"error": "No images found", "flooded_images": [], "all_predictions": []}
    
    flooded_images = []
    all_predictions = []
    processed_count = 0
    
    for idx, image_file in enumerate(image_files):
        image_path = os.path.join(input_dir, image_file)
        
        # Make prediction
        prediction, original_image = predict_single_image(image_path, processor, model, device)
        
        if prediction is not None:
            # Calculate water percentage
            water_percentage = calculate_water_percentage(prediction)
            
            # Create prediction visualization
            prediction_viz = create_prediction_visualization(prediction)
            
            # Store prediction info
            prediction_info = {
                'image_name': image_file,
                'water_percentage': water_percentage,
                'prediction': prediction,
                'original_image': original_image,
                'prediction_viz': prediction_viz
            }
            
            all_predictions.append(prediction_info)
            
            # If water percentage > 50%, save to flooded directory
            if water_percentage > 50.0:
                # Save original image
                original_path = os.path.join(flooded_dir, f"original_{image_file}")
                original_image.save(original_path)
                
                # Save prediction visualization
                pred_path = os.path.join(flooded_dir, f"prediction_{image_file}")
                prediction_viz.save(pred_path)
                
                flooded_images.append({
                    'image_name': image_file,
                    'water_percentage': water_percentage,
                    'original_path': original_path,
                    'prediction_path': pred_path
                })
        
        processed_count += 1
        
        # Update progress
        if progress_callback:
            progress = processed_count / total_images
            progress_callback(progress)
    
    # Summary
    total_flooded = len(flooded_images)
    
    result = {
        'total_images': total_images,
        'total_flooded': total_flooded,
        'flooded_percentage': (total_flooded / total_images * 100) if total_images > 0 else 0,
        'flooded_images': flooded_images[:10],  # Limit to first 10 for display
        'all_predictions': all_predictions,
        'flooded_dir': flooded_dir
    }
    
    return result

def get_flooded_images(flooded_dir, limit=10):
    """Get list of flooded images from directory"""
    if not os.path.exists(flooded_dir):
        return []
    
    # Get original images (not prediction visualizations)
    original_files = [f for f in os.listdir(flooded_dir) if f.startswith('original_')]
    
    flooded_images = []
    for original_file in original_files[:limit]:
        pred_file = original_file.replace('original_', 'prediction_')
        
        original_path = os.path.join(flooded_dir, original_file)
        pred_path = os.path.join(flooded_dir, pred_file)
        
        if os.path.exists(original_path) and os.path.exists(pred_path):
            flooded_images.append({
                'image_name': original_file.replace('original_', ''),
                'original_path': original_path,
                'prediction_path': pred_path
            })
    
    return flooded_images

def cleanup_prediction_data(state_name):
    """Clean up prediction data for a state"""
    flooded_dir = f"output/flooded/{state_name.replace(' ', '_')}"
    if os.path.exists(flooded_dir):
        shutil.rmtree(flooded_dir)

def get_prediction_summary(state_name):
    """Get summary of prediction results"""
    flooded_dir = f"output/flooded/{state_name.replace(' ', '_')}"
    
    if not os.path.exists(flooded_dir):
        return {"total_flooded": 0, "flooded_images": []}
    
    original_files = [f for f in os.listdir(flooded_dir) if f.startswith('original_')]
    flooded_images = get_flooded_images(flooded_dir, limit=10)
    
    return {
        "total_flooded": len(original_files),
        "flooded_images": flooded_images
    }