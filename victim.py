import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
from components.thermal import convert_to_thermal_night_vision
from components.detection import detect_victims_yolo, display_detection_results, get_detection_statistics

def annotate_original_image(original_image, detection_results):
    """Annotate the original RGB image with all detection results"""
    try:
        from PIL import ImageDraw, ImageFont
        
        annotated_img = original_image.copy()
        draw = ImageDraw.Draw(annotated_img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        for detection in detection_results['detections']:
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
            text_bbox = draw.textbbox((x1, y1-25), label, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            
            # Text background and text
            draw.rectangle([x1, y1-25, x1+text_width+4, y1], fill='#FFFFFF')
            draw.text((x1+2, y1-23), label, fill='#000000', font=font)
            
            # Center point
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            draw.ellipse([center_x-3, center_y-3, center_x+3, center_y+3], fill=color)
        
        return annotated_img
        
    except Exception as e:
        st.error(f"Error annotating original image: {e}")
        return original_image

def display_detection_results_with_original(detection_results, original_image):
    """Display detection results using the original RGB image"""
    try:
        if detection_results['count'] > 0:
            # Separate persons and other objects
            persons = [d for d in detection_results['detections'] if d['class'].lower() == 'person']
            others = [d for d in detection_results['detections'] if d['class'].lower() != 'person']
            
            with st.expander(f"🔍 Detection Results ({detection_results['count']} objects found)", expanded=True):
                
                # Show persons if any
                if persons:
                    st.markdown(f"**🚨 {len(persons)} Person(s) Detected - RESCUE REQUIRED**")
                    cols = st.columns(min(len(persons), 4))
                    
                    for i, detection in enumerate(persons):
                        with cols[i % 4]:
                            bbox = detection['bbox']
                            x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
                            
                            padding = 10
                            img_width, img_height = original_image.size
                            x1 = max(0, x1 - padding)
                            y1 = max(0, y1 - padding)
                            x2 = min(img_width, x2 + padding)
                            y2 = min(img_height, y2 + padding)
                            
                            cropped = original_image.crop((x1, y1, x2, y2))
                            st.image(cropped, caption=f"Person {i+1}", use_container_width=True)
                            st.text(f"Position: ({detection['center_x']:.0f}, {detection['center_y']:.0f})")
                
                # Summary statistics
                st.markdown("---")
                stats = get_detection_statistics(detection_results)
                st.markdown(f"""
                **Detection Summary:**
                - Total Objects: **{detection_results['count']}**
                - Persons: **{stats.get('person_count', 0)}**
                - Other Objects: **{stats.get('other_count', 0)}**
                - Average Confidence: **{stats.get('average_confidence', 0):.1%}**
                """)
        
        else:
            with st.expander("🔍 Detection Results", expanded=False):
                st.markdown("❌ No objects detected in the image.")
    
    except Exception as e:
        st.error(f"Error displaying detection results: {e}")

def render_victim_page():
    """Main function to render the victim detection page"""
    st.markdown("""
    <div class="page-title gradient-text">Victim Localisation</div>
    <div class="page-subtitle">Upload an image to detect all objects using thermal analysis and AI detection</div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div class="solution-card">
            <div class="solution-icon">📤</div>
            <h3>Upload Image</h3>
            <p>Upload your image for detection analysis. Supported formats: JPG, JPEG, PNG</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="solution-card">
            <div class="solution-icon">⚙️</div>
            <h3>Processing Pipeline</h3>
            <p>AI-Powered Object Detection with Thermal Night Vision</p>
        </div>
        """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
            "Choose an image file", 
            type=['jpg', 'jpeg', 'png'],
            help="Upload an image to detect objects using thermal analysis"
    )
        
    if uploaded_file is not None:
        st.markdown('<div class="indian-flag-divider"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="page-title gradient-text">📊 Analysis Results</div>
        """, unsafe_allow_html=True)
        
        original_image = Image.open(uploaded_file)
        
        result_col1, result_col2, result_col3 = st.columns([1, 1, 1])
        
        with result_col1:
            st.markdown("""
            <div class="feature-card">
                <h3>Original Image</h3>
                <p>The uploaded image for analysis</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.image(original_image, caption="Original Image", use_container_width=True)
        
        with result_col2:
            st.markdown("""
            <div class="feature-card">
                <h3>Night Vision</h3>
                <p>Converted thermal representation</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.spinner('Converting to thermal night vision...'):
                thermal_image = convert_to_thermal_night_vision(original_image)
                if thermal_image is not None:
                    st.image(thermal_image, caption="Thermal Night Vision", use_container_width=True)
                else:
                    st.error("Failed to convert image to thermal format")
        
        with result_col3:
            st.markdown("""
            <div class="feature-card">
                <h3>Object Detection</h3>
                <p>AI-detected objects on original image</p>
            </div>
            """, unsafe_allow_html=True)
            
            if thermal_image is not None:
                with st.spinner('Detecting objects using AI...'):
                    _, detection_results = detect_victims_yolo(thermal_image)
                    
                    if detection_results is not None:
                        annotated_original = annotate_original_image(original_image, detection_results)
                        st.image(annotated_original, caption="Detected Objects", use_container_width=True)
                        
                        stats = get_detection_statistics(detection_results)
                        
                        # Show person count prominently
                        person_count = stats.get('person_count', 0)
                        if person_count > 0:
                            st.markdown(f"**🚨 {person_count} Person(s) Detected - RESCUE REQUIRED**")
                    else:
                        st.error("Failed to perform object detection")
        
        # Detailed detection results
        if 'thermal_image' in locals() and thermal_image is not None:
            if 'detection_results' in locals() and detection_results is not None:
                st.markdown('<div class="indian-flag-divider"></div>', unsafe_allow_html=True)
                display_detection_results_with_original(detection_results, original_image)
                
                # Download options
                if detection_results['count'] > 0:
                    st.markdown("---")
                    st.markdown("### 📥 Download Results")
                    
                    col0, col1, col11, col2, col22 = st.columns([1, 1, 1, 1, 1])
                    
                    with col1:
                        annotated_original = annotate_original_image(original_image, detection_results)
                        img_bytes = io.BytesIO()
                        annotated_original.save(img_bytes, format='PNG')
                        img_bytes = img_bytes.getvalue()
                        
                        st.download_button(
                            label="📥 Download Annotated Image",
                            data=img_bytes,
                            file_name="detection_results.png",
                            mime="image/png"
                        )
                    
                    with col2:
                        thermal_bytes = io.BytesIO()
                        thermal_image.save(thermal_bytes, format='PNG')
                        thermal_bytes = thermal_bytes.getvalue()
                        
                        st.download_button(
                            label="📥 Download Thermal Image",
                            data=thermal_bytes,
                            file_name="thermal_image.png",
                            mime="image/png"
                        )