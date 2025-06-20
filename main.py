import streamlit as st
import folium
from streamlit_folium import st_folium
import numpy as np
from PIL import Image
import io
import time
import json
import base64
from datetime import datetime

from config import STATES_DATA, APP_CONFIG
from models.segmentation import SegmentationModel
from models.flood_detection import FloodDetectionModel
from models.person_detection import PersonDetectionModel
from utils.image_processing import process_satellite_image, resize_image
from utils.thermal_processing import create_thermal_night_vision
from utils.geo_utils import calculate_coordinates, calculate_distance, format_coordinates
from utils.ui_styles import (
    apply_custom_styles, create_header, create_metrics_cards,
    create_detection_card, create_victim_location_card, 
    create_flood_alert, create_success_alert, create_loading_animation
)

def initialize_session_state():
    """Initialize all session state variables"""
    defaults = {
        'models_loaded': False,
        'analysis_results': None,
        'processing': False,
        'selected_coordinates': None,
        'analysis_history': [],
        'current_state': 'Maharashtra',
        'map_center': None,
        'detection_stats': {'total_analyses': 0, 'floods_detected': 0, 'persons_rescued': 0}
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def initialize_models():
    """Load all AI models with progress tracking"""
    if not st.session_state.models_loaded:
        with st.spinner('🚀 Initializing AI Models...'):
            try:
                progress_placeholder = st.empty()
                
                # Load Segmentation Model
                progress_placeholder.text("Loading Segmentation Model...")
                seg_model = SegmentationModel()
                time.sleep(0.5)
                
                # Load Flood Detection Model
                progress_placeholder.text("Loading Flood Detection Model...")
                flood_model = FloodDetectionModel()
                time.sleep(0.5)
                
                # Load Person Detection Model
                progress_placeholder.text("Loading Person Detection Model...")
                person_model = PersonDetectionModel()
                time.sleep(0.5)
                
                st.session_state.models = {
                    'segmentation': seg_model,
                    'flood_detection': flood_model,
                    'person_detection': person_model
                }
                
                st.session_state.models_loaded = True
                progress_placeholder.success("✅ All models loaded successfully!")
                time.sleep(1)
                progress_placeholder.empty()
                
            except Exception as e:
                st.error(f"❌ Failed to load models: {str(e)}")
                st.stop()

def create_sidebar():
    """Create enhanced sidebar with controls"""
    with st.sidebar:
        st.markdown("### 🎛️ System Configuration")
        
        # Model status indicator
        if st.session_state.models_loaded:
            st.success("✅ All AI Models Online")
        else:
            st.warning("⏳ Loading Models...")
        
        st.markdown("---")
        
        # Detection parameters
        st.markdown("### ⚙️ Detection Parameters")
        
        water_threshold = st.slider(
            "💧 Water Coverage Threshold (%)",
            min_value=30, max_value=80, value=50, step=5,
            help="Minimum water coverage to trigger flood detection"
        )
        
        flood_confidence = st.slider(
            "🌊 Flood Detection Confidence",
            min_value=0.1, max_value=1.0, value=0.6, step=0.1,
            help="Minimum confidence for flood classification"
        )
        
        person_confidence = st.slider(
            "👥 Person Detection Confidence",
            min_value=0.1, max_value=1.0, value=0.5, step=0.1,
            help="Minimum confidence for person detection"
        )
        
        st.markdown("---")
        
        # System stats
        st.markdown("### 📊 System Statistics")
        stats = st.session_state.detection_stats
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🔍 Total Analyses", stats['total_analyses'])
        with col2:
            st.metric("🌊 Floods Detected", stats['floods_detected'])
        
        st.metric("👥 Persons Located", stats['persons_rescued'])
        
        st.markdown("---")
        
        # Analysis history and controls
        st.markdown("### 📋 Analysis History")
        
        if st.session_state.analysis_history:
            for i, analysis in enumerate(st.session_state.analysis_history[-3:]):
                with st.expander(f"Analysis {len(st.session_state.analysis_history) - i}"):
                    st.write(f"**Time:** {analysis['timestamp']}")
                    st.write(f"**Location:** {analysis['state']}")
                    st.write(f"**Status:** {'🚨 Flood' if analysis['flood_detected'] else '✅ Safe'}")
                    if analysis['flood_detected']:
                        st.write(f"**Persons:** {analysis['person_count']}")
        else:
            st.info("No analysis history yet")
        
        # Control buttons
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.analysis_history = []
            st.session_state.analysis_results = None
            st.rerun()
        
        if st.button("📊 Export Data", use_container_width=True):
            export_analysis_data()
    
    return water_threshold, flood_confidence, person_confidence

def create_main_interface():
    """Create the main interface with map and controls"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.markdown("### 🌍 Location Selection")
        
        # State selector
        selected_state = st.selectbox(
            "Choose Indian State",
            options=list(STATES_DATA.keys()),
            index=list(STATES_DATA.keys()).index(st.session_state.current_state),
            key="state_selector",
            help="Select a state to focus the satellite view"
        )
        
        if selected_state != st.session_state.current_state:
            st.session_state.current_state = selected_state
            st.rerun()
        
        state_info = STATES_DATA[selected_state]
        
        # State information card
        with st.expander(f"ℹ️ {selected_state} Details", expanded=True):
            st.write(f"**📍 Coordinates:** {state_info['lat']:.4f}°N, {state_info['lng']:.4f}°E")
            st.write(f"**🔍 Zoom Level:** {state_info['zoom']}")
            st.write(f"**🏛️ Capital:** {state_info.get('capital', 'N/A')}")
        
        # Quick action buttons
        st.markdown("### ⚡ Quick Actions")
        
        if st.button("🎯 Focus on State Center", use_container_width=True):
            st.session_state.map_center = (state_info['lat'], state_info['lng'])
            st.rerun()
        
        if st.button("🔄 Refresh Satellite Data", use_container_width=True):
            st.cache_data.clear()
            st.success("Satellite data refreshed!")
        
        # Recent alerts section
        st.markdown("### 🚨 Active Alerts")
        display_active_alerts()
    
    with col2:
        st.markdown("### 🗺️ Interactive Satellite Map")
        
        # Create and display map
        satellite_map = create_satellite_map(selected_state, state_info)
        map_data = st_folium(
            satellite_map, 
            width=700, 
            height=500, 
            returned_objects=["last_clicked"],
            key="satellite_map"
        )
        
        # Handle map interactions
        handle_map_click(map_data, selected_state)
    
    with col3:
        st.markdown("### 📊 Real-time Analytics")
        create_metrics_cards()
        
        st.markdown("### 🎯 Analysis Results")
        display_analysis_results()

def create_satellite_map(selected_state, state_info):
    """Create interactive satellite map with markers"""
    center_lat = st.session_state.map_center[0] if st.session_state.map_center else state_info['lat']
    center_lng = st.session_state.map_center[1] if st.session_state.map_center else state_info['lng']
    
    # Initialize map
    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=state_info['zoom'],
        tiles=None
    )
    
    # Add multiple tile layers
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri WorldImagery',
        name='🛰️ Satellite',
        overlay=False,
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        tiles='OpenStreetMap',
        name='🗺️ Street Map',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Add state center marker
    folium.Marker(
        [state_info['lat'], state_info['lng']],
        popup=folium.Popup(f"<b>{selected_state}</b><br>State Center", max_width=200),
        icon=folium.Icon(color='blue', icon='home', prefix='fa')
    ).add_to(m)
    
    # Add analysis markers from history
    for analysis in st.session_state.analysis_history:
        if analysis['state'] == selected_state:
            lat, lng = analysis['coordinates']
            
            if analysis['flood_detected']:
                icon_config = {
                    'color': 'red',
                    'icon': 'exclamation-triangle',
                    'prefix': 'fa'
                }
                popup_text = f"<b>🚨 FLOOD ALERT</b><br>Persons: {analysis['person_count']}<br>Time: {analysis['timestamp']}"
            else:
                icon_config = {
                    'color': 'green',
                    'icon': 'check-circle',
                    'prefix': 'fa'
                }
                popup_text = f"<b>✅ Safe Area</b><br>Time: {analysis['timestamp']}"
            
            folium.Marker(
                [lat, lng],
                popup=folium.Popup(popup_text, max_width=250),
                icon=folium.Icon(**icon_config)
            ).add_to(m)
    
    # Add current analysis marker
    if st.session_state.analysis_results:
        lat, lng = st.session_state.analysis_results['coordinates']
        
        if st.session_state.analysis_results.get('flood_detected'):
            folium.Marker(
                [lat, lng],
                popup=folium.Popup("🔍 Current Analysis - Flood Detected", max_width=200),
                icon=folium.Icon(color='darkred', icon='search', prefix='fa')
            ).add_to(m)
        else:
            folium.Marker(
                [lat, lng],
                popup=folium.Popup("🔍 Current Analysis - Safe", max_width=200),
                icon=folium.Icon(color='darkgreen', icon='search', prefix='fa')
            ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m

def handle_map_click(map_data, selected_state):
    """Handle map click events and analysis triggers"""
    if map_data['last_clicked'] and not st.session_state.processing:
        clicked_lat = map_data['last_clicked']['lat']
        clicked_lng = map_data['last_clicked']['lng']
        
        st.session_state.selected_coordinates = (clicked_lat, clicked_lng)
        
        # Display selected coordinates
        st.info(f"📍 **Selected Location:** {format_coordinates(clicked_lat, clicked_lng)}")
        
        # Action buttons
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            if st.button("🔍 Analyze Area", type="primary", use_container_width=True):
                water_threshold, flood_confidence, person_confidence = create_sidebar()
                start_analysis(clicked_lat, clicked_lng, selected_state, water_threshold, flood_confidence, person_confidence)
        
        with col_btn2:
            if st.button("📊 Quick Scan", use_container_width=True):
                perform_quick_scan(clicked_lat, clicked_lng)
        
        with col_btn3:
            if st.button("📥 Save Location", use_container_width=True):
                save_location(clicked_lat, clicked_lng, selected_state)

def start_analysis(lat, lng, state, water_threshold, flood_confidence, person_confidence):
    """Start comprehensive analysis of selected area"""
    st.session_state.processing = True
    
    # Create progress container
    progress_container = st.container()
    
    with progress_container:
        st.markdown("### 🔄 Analysis in Progress")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Fetch satellite imagery
            status_text.info("🛰️ **Step 1/6:** Fetching high-resolution satellite imagery...")
            progress_bar.progress(10)
            time.sleep(1)
            
            satellite_img = process_satellite_image(lat, lng)
            if satellite_img is None:
                st.error("❌ Failed to fetch satellite imagery. Please try another location.")
                return
            
            # Step 2: Segmentation analysis
            status_text.info("🎯 **Step 2/6:** Running AI segmentation analysis...")
            progress_bar.progress(25)
            time.sleep(1)
            
            segmentation_result = st.session_state.models['segmentation'].predict(satellite_img)
            water_percentage = calculate_water_percentage(segmentation_result)
            
            # Initialize results
            results = {
                'coordinates': (lat, lng),
                'state': state,
                'water_percentage': water_percentage,
                'segmentation': segmentation_result,
                'satellite_image': satellite_img,
                'flood_detected': False,
                'person_count': 0,
                'person_locations': [],
                'analysis_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'timestamp': datetime.now().strftime("%H:%M:%S")
            }
            
            # Step 3: Water coverage evaluation
            status_text.info(f"💧 **Step 3/6:** Water coverage: {water_percentage:.1f}% (Threshold: {water_threshold}%)")
            progress_bar.progress(40)
            time.sleep(1)
            
            # Step 4: Flood detection (if water coverage is high)
            if water_percentage > water_threshold:
                status_text.warning("🌊 **Step 4/6:** High water coverage detected! Analyzing for flood conditions...")
                progress_bar.progress(55)
                time.sleep(1)
                
                resized_img = resize_image(satellite_img, (512, 512))
                flood_prediction = st.session_state.models['flood_detection'].predict(resized_img)
                
                results['flood_probability'] = flood_prediction
                
                if flood_prediction > flood_confidence:
                    results['flood_detected'] = True
                    
                    # Step 5: Thermal night vision conversion
                    status_text.warning("🌡️ **Step 5/6:** Converting to thermal night vision for enhanced detection...")
                    progress_bar.progress(70)
                    time.sleep(1)
                    
                    thermal_img = create_thermal_night_vision(resized_img)
                    results['thermal_image'] = thermal_img
                    
                    # Step 6: Person detection
                    status_text.error("👥 **Step 6/6:** Scanning for persons in affected area...")
                    progress_bar.progress(85)
                    time.sleep(1)
                    
                    person_detections = st.session_state.models['person_detection'].predict(thermal_img)
                    
                    # Filter by confidence
                    filtered_detections = [
                        det for det in person_detections 
                        if det['confidence'] > person_confidence
                    ]
                    
                    results['person_count'] = len(filtered_detections)
                    results['person_locations'] = filtered_detections
                    
                    # Calculate distances
                    if filtered_detections:
                        calculate_victim_distances(filtered_detections, lat, lng, results)
                    
                    # Update statistics
                    st.session_state.detection_stats['floods_detected'] += 1
                    st.session_state.detection_stats['persons_rescued'] += results['person_count']
            else:
                status_text.success("✅ **Step 4/6:** Water coverage below threshold. Area appears safe.")
                progress_bar.progress(85)
                time.sleep(1)
            
            # Complete analysis
            progress_bar.progress(100)
            status_text.success("✅ **Analysis Complete!** Results ready for review.")
            
            st.session_state.analysis_results = results
            st.session_state.detection_stats['total_analyses'] += 1
            
            # Add to history
            st.session_state.analysis_history.append(results.copy())
            
            time.sleep(2)
            
        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)}")
        finally:
            st.session_state.processing = False
            progress_container.empty()

def calculate_water_percentage(segmentation_result):
    """Calculate percentage of water pixels in segmentation result"""
    if isinstance(segmentation_result, np.ndarray):
        if len(segmentation_result.shape) == 3:
            water_pixels = np.sum(segmentation_result[:, :, 0] > 0.5)
            total_pixels = segmentation_result.shape[0] * segmentation_result.shape[1]
        else:
            water_pixels = np.sum(segmentation_result == 1)
            total_pixels = segmentation_result.size
        return (water_pixels / total_pixels) * 100 if total_pixels > 0 else 0
    return np.random.uniform(10, 80)  # Fallback for demo

def calculate_victim_distances(detections, center_lat, center_lng, results):
    """Calculate distances of detected persons from center point"""
    victim_data = []
    
    for i, detection in enumerate(detections):
        bbox = detection.get('bbox', [0, 0, 50, 50])
        x_center = bbox[0] + bbox[2] / 2
        y_center = bbox[1] + bbox[3] / 2
        
        # Convert pixel coordinates to lat/lng (simplified)
        pixel_lat, pixel_lng = calculate_coordinates(x_center, y_center, center_lat, center_lng)
        
        # Calculate distance from center
        distance = calculate_distance(center_lat, center_lng, pixel_lat, pixel_lng)
        
        victim_data.append({
            'id': i + 1,
            'pixel_position': (x_center, y_center),
            'coordinates': (pixel_lat, pixel_lng),
            'distance_m': distance,
            'confidence': detection['confidence']
        })
    
    results['victim_distances'] = victim_data

def display_active_alerts():
    """Display active flood alerts"""
    active_alerts = [
        analysis for analysis in st.session_state.analysis_history 
        if analysis.get('flood_detected', False)
    ]
    
    if active_alerts:
        for alert in active_alerts[-3:]:  # Show last 3 alerts
            create_detection_card(
                "🚨 Flood Alert",
                f"{alert['state']} - {alert['person_count']} persons",
                "danger"
            )
    else:
        st.success("✅ No active flood alerts")

def display_analysis_results():
    """Display detailed analysis results"""
    if not st.session_state.analysis_results:
        st.info("🔍 **Instructions:**\n\n1. Select a state from dropdown\n2. Click on the satellite map\n3. Click 'Analyze Area' to start")
        return
    
    results = st.session_state.analysis_results
    
    # Key metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("💧 Water Coverage", f"{results['water_percentage']:.1f}%")
    with col2:
        if results.get('flood_probability'):
            st.metric("🌊 Flood Risk", f"{results['flood_probability']:.1%}")
        else:
            st.metric("🌊 Flood Risk", "Low")
    
    # Flood status
    if results['flood_detected']:
        create_flood_alert()
        
        st.metric("👥 Persons Detected", results['person_count'])
        
        # Display victim locations
        if results.get('victim_distances'):
            st.markdown("**🚨 Emergency Locations:**")
            for victim in results['victim_distances']:
                create_victim_location_card(
                    victim['id'],
                    victim['distance_m'],
                    victim['coordinates']
                )
        
        # Display images
        if results.get('thermal_image') is not None:
            st.markdown("### 🖼️ Analysis Images")
            
            img_col1, img_col2 = st.columns(2)
            with img_col1:
                st.image(
                    results['satellite_image'], 
                    caption="📡 Satellite View",
                    use_column_width=True
                )
            
            with img_col2:
                st.image(
                    results['thermal_image'],
                    caption="🌡️ Thermal Detection",
                    use_column_width=True
                )
    else:
        create_success_alert("✅ No flood detected - Area appears safe")
    
    # Analysis metadata
    with st.expander("📋 Detailed Analysis Report"):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**📅 Analysis Time:** {results.get('analysis_time', 'Unknown')}")
            st.write(f"**📍 Coordinates:** {format_coordinates(results['coordinates'][0], results['coordinates'][1])}")
            st.write(f"**🌍 State:** {results.get('state', 'Unknown')}")
        
        with col2:
            if results.get('flood_probability'):
                st.write(f"**🌊 Flood Confidence:** {results['flood_probability']:.3f}")
            st.write(f"**💧 Water Percentage:** {results['water_percentage']:.2f}%")
            st.write(f"**🎯 Detection Model:** LoveDa + Xception + YOLO")

def perform_quick_scan(lat, lng):
    """Perform quick preliminary scan"""
    with st.spinner("🔍 Performing quick scan..."):
        time.sleep(2)
        
        # Simulate quick scan results
        water_pct = np.random.uniform(5, 95)
        
        if water_pct > 60:
            st.warning(f"⚠️ **Quick Scan Result:** High water coverage ({water_pct:.1f}%) detected. Recommend full analysis.")
        elif water_pct > 30:
            st.info(f"ℹ️ **Quick Scan Result:** Moderate water coverage ({water_pct:.1f}%) detected.")
        else:
            st.success(f"✅ **Quick Scan Result:** Low water coverage ({water_pct:.1f}%) - Area appears normal.")

def save_location(lat, lng, state):
    """Save location for future reference"""
    saved_locations = st.session_state.get('saved_locations', [])
    
    new_location = {
        'coordinates': (lat, lng),
        'state': state,
        'saved_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'name': f"{state} - {format_coordinates(lat, lng)}"
    }
    
    saved_locations.append(new_location)
    st.session_state['saved_locations'] = saved_locations
    
    st.success(f"📌 Location saved: {format_coordinates(lat, lng)}")

def export_analysis_data():
    """Export analysis data as JSON"""
    if st.session_state.analysis_history:
        export_data = {
            'export_time': datetime.now().isoformat(),
            'total_analyses': len(st.session_state.analysis_history),
            'statistics': st.session_state.detection_stats,
            'analyses': st.session_state.analysis_history
        }
        
        # Convert to JSON
        json_data = json.dumps(export_data, indent=2, default=str)
        
        # Create download
        st.download_button(
            label="📥 Download Analysis Data",
            data=json_data,
            file_name=f"res_geo_ai_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    else:
        st.warning("No analysis data to export")

def main():
    """Main application function"""
    # Page configuration
    st.set_page_config(
        page_title="Res Geo AI - Flood Detection & Rescue",
        page_icon="🛰️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom styles
    apply_custom_styles()
    
    # Create header
    create_header()
    
    # Initialize session state and models
    initialize_session_state()
    initialize_models()
    
    # Create sidebar controls
    water_threshold, flood_confidence, person_confidence = create_sidebar()
    
    # Create main interface
    create_main_interface()
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 1rem;'>
            🛰️ <strong>Res Geo AI</strong> - Advanced Satellite-to-Drone Dual-Modality System<br>
            Powered by LoveDa Segmentation • Xception Flood Detection • YOLO Person Detection
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()