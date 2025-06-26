import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
from components.thermal import convert_to_thermal_night_vision
from components.detection import detect_victims_yolo

def render_victim_page():
    """
    Main function to render the victim detection page with thermal conversion and YOLO detection
    """
    st.markdown("""
    <div class="page-title gradient-text">🔍 Victim Detection Interface</div>
    <div class="page-subtitle">Upload an image to detect victims using thermal analysis and AI detection</div>
    """, unsafe_allow_html=True)
    
    # Create columns for better layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div class="solution-card">
            <div class="solution-icon">📤</div>
            <h3>Upload Image</h3>
            <p>Upload your image for victim detection analysis. Supported formats: JPG, JPEG, PNG</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="solution-card">
            <div class="solution-icon">⚙️</div>
            <h3>Processing Pipeline</h3>
            <p>AI-Powered Victim Detection with Thermal Night Vision</p>
        </div>
        """, unsafe_allow_html=True)
    
    # File uploader
    uploaded_file = st.file_uploader(
            "Choose an image file", 
            type=['jpg', 'jpeg', 'png'],
            help="Upload an image to detect victims using thermal analysis"
    )
        
    # Processing section
    if uploaded_file is not None:
        # Display original image
        st.markdown('<div class="indian-flag-divider"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="page-title gradient-text">📊 Analysis Results</div>
        """, unsafe_allow_html=True)
        
        # Create columns for results
        result_col1, result_col2, result_col3 = st.columns([1, 1, 1])
        
        with result_col1:
            st.markdown("""
            <div class="feature-card">
                <h3>Original Image</h3>
                <p>The uploaded image for analysis</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Load and display original image
            image = Image.open(uploaded_file)
            st.image(image, caption="Original Image", use_container_width=True)
        
        with result_col2:
            st.markdown("""
            <div class="feature-card">
                <h3>Thermal Night Vision</h3>
                <p>Converted thermal representation</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Convert to thermal night vision
            with st.spinner('Converting to thermal night vision...'):
                thermal_image = convert_to_thermal_night_vision(image)
                if thermal_image is not None:
                    st.image(thermal_image, caption="Thermal Night Vision", use_container_width=True)
                else:
                    st.error("Failed to convert image to thermal format")
        
        with result_col3:
            st.markdown("""
            <div class="feature-card">
                <h3>Victim Detection</h3>
                <p>AI-detected victims with bounding boxes</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Perform victim detection
            if thermal_image is not None:
                with st.spinner('Detecting victims using AI...'):
                    detected_image, detection_results = detect_victims_yolo(thermal_image)
                    if detected_image is not None:
                        st.image(detected_image, caption="Detected Victims", use_container_width=True)
                        
                        # Display detection statistics
                        st.markdown(f"""
                        <div class="stat-card">
                            <div class="stat-number">{detection_results['count']}</div>
                            <div class="stat-label">Victims Detected</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if detection_results['count'] > 0:
                            st.markdown("""
                            <div class="tech-tag" style="display: inline-block; margin: 0.5rem 0;">
                                ✅ Victims Found - Immediate Rescue Required
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div class="tech-tag" style="display: inline-block; margin: 0.5rem 0; background: rgba(128, 128, 128, 0.2);">
                                ❌ No Victims Detected in Current Image
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.error("Failed to perform victim detection")
        
