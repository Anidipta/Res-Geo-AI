import streamlit as st
from streamlit_folium import st_folium
import os
import shutil
from PIL import Image

# Import our components
from components.geo_map import (
    load_geodata, 
    display_state_map_and_tiles, 
    capture_satellite_tiles, 
    get_limited_tile_images
)
from components.flood import (
    process_flood_prediction,
    get_flooded_images,
    cleanup_prediction_data,
    get_prediction_summary
)

# Add custom CSS to prevent unnecessary reruns
st.markdown("""
<style>
    /* Stable container sizes */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: none;
    }
    
    /* Prevent map container from triggering reruns */
    .folium-map {
        position: relative !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def cached_load_geodata():
    """Cached version of geodata loading"""
    return load_geodata()

def display_tile_images(tile_images, output_dir, columns=5, max_display=10):
    """Display tile images in a grid layout"""
    if not tile_images:
        st.write("No tiles found")
        return
    
    # Limit to max_display images
    display_images = tile_images[:max_display]
    st.write(f"**Showing {len(display_images)} of {len(tile_images)} tiles:**")
    
    # Create 2x5 grid (2 rows of 5 columns each)
    for row in range(0, len(display_images), columns):
        cols = st.columns(columns)
        for col_idx, tile_idx in enumerate(range(row, min(row + columns, len(display_images)))):
            with cols[col_idx]:
                tile_name = display_images[tile_idx]
                tile_path = os.path.join(output_dir, tile_name)
                if os.path.exists(tile_path):
                    try:
                        image = Image.open(tile_path)
                        st.image(image, caption=tile_name.split('_')[1], use_container_width=True)
                    except Exception as e:
                        st.error(f"Error loading {tile_name}: {e}")
    
    if len(tile_images) > max_display:
        st.info(f"... and {len(tile_images) - max_display} more tiles")

def display_flooded_images_section(state_name):
    """Display section for flooded images"""
    flooded_images = get_flooded_images(f"output/flooded/{state_name.replace(' ', '_')}")
    
    if not flooded_images:
        st.warning("No flooded areas detected")
        return
    
    st.success(f"🌊 Found {len(flooded_images)} images with significant flooding!")
    
    # Display flooded images in grid format
    for row_start in range(0, len(flooded_images), 5):
        row_images = flooded_images[row_start:row_start + 5]
        
        # Original images row
        st.write("**Original Satellite Images:**")
        cols = st.columns(5)
        for idx, img_info in enumerate(row_images):
            with cols[idx]:
                if os.path.exists(img_info['original_path']):
                    original_img = Image.open(img_info['original_path'])
                    st.image(original_img, caption=f"Area {row_start + idx + 1}", use_container_width=True)
        
        # Prediction images row
        st.write("**Flood Predictions:**")
        cols = st.columns(5)
        for idx, img_info in enumerate(row_images):
            with cols[idx]:
                if os.path.exists(img_info['prediction_path']):
                    pred_img = Image.open(img_info['prediction_path'])
                    st.image(pred_img, caption="Flood Zones", use_container_width=True)
        
        if row_start + 5 < len(flooded_images):
            st.markdown("---")

def reset_analysis_state():
    """Reset all analysis-related session state"""
    keys_to_remove = [
        'analysis_started', 'analysis_complete', 'show_tiles',
        'current_output_dir', 'prediction_complete', 'show_predictions'
    ]
    
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]

def render_map_page():
    """Main function to render the map analysis page"""
        
    st.markdown('<div class="hero-title"><h2>Interactive State Analysis</h2></div>', unsafe_allow_html=True)
    
    # Load geographic data
    df = cached_load_geodata()
    
    # Top controls section
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        # State selection
        state_names = sorted(df['ST_NAME'].unique().tolist())
        selected_state = st.selectbox(
            "Select State",
            state_names,
            key="state_selector"
        )
    
    with col2:
        if selected_state:
            # Tile range selector
            tiles_range = st.slider(
                "Tile Range",
                min_value=10,
                max_value=2000,
                value=10,
                step=10,
                key="tiles_slider"
            )
    
    with col3:
        if selected_state:
            # Analysis button
            if st.button("🔍 Start Analysis", key="analysis_btn", use_container_width=True):
                st.session_state.analysis_started = True
                st.session_state.selected_state = selected_state
                st.session_state.tiles_range = tiles_range
                # Clear previous states
                for key in ['analysis_complete', 'show_tiles', 'prediction_complete', 'show_predictions']:
                    if key in st.session_state:
                        del st.session_state[key]
    
    # Map display section
    if selected_state:
        st.markdown("### State Map View")
        map_obj, _ = display_state_map_and_tiles(df, selected_state, 10)
        if map_obj:
            # Reduce map height and center it
            col_map1, col_map2, col_map3 = st.columns([0.1, 0.8, 0.1])
            with col_map2:
                st_folium(map_obj, width=None, height=700)
    else:
        st.info("Please select a state to view the map")
    
    # Analysis progress section
    if st.session_state.get('analysis_started', False):
        st.markdown("---")
        st.markdown("### Analysis Progress")
        
        progress_container = st.container()
        
        map_obj, state_info = display_state_map_and_tiles(
            df, 
            st.session_state.selected_state, 
            st.session_state.tiles_range
        )
        
        if state_info:
            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def update_progress(progress):
                    progress_bar.progress(progress)
                    status_text.text(f"Processing: {progress * 100:.1f}%")
                
                # Capture satellite tiles
                successful_tiles, total_tiles = capture_satellite_tiles(
                    state_info['bounds'],
                    state_info['tile_params'],
                    state_info['output_dir'],
                    state_info['state_name'],
                    progress_callback=update_progress
                )
                
                status_text.text(f"✅ Complete: {successful_tiles}/{total_tiles} tiles extracted")
                st.session_state.analysis_complete = True
                st.session_state.current_output_dir = state_info['output_dir']
                st.session_state.current_state_name = state_info['state_name']
    
    # Post-analysis controls
    if st.session_state.get('analysis_complete', False):
        st.markdown("---")
        st.markdown("### 🛠️ Analysis Tools")
        
        # Action buttons in columns
        col_tiles, col_predict, col_reset = st.columns(3)
        
        with col_tiles:
            view_tiles_btn = st.button("📁 View Extracted Tiles", key="view_tiles_btn", use_container_width=True)
        
        with col_predict:
            predict_btn = st.button("🤖 Flood Prediction", key="predict_btn", use_container_width=True)
        
        with col_reset:
            if st.button("🗑️ Reset Analysis", key="reset_btn", use_container_width=True):
                if os.path.exists("output"):
                    shutil.rmtree("output")
                reset_analysis_state()
                st.rerun()
        
        # Handle button clicks
        if view_tiles_btn:
            st.session_state.show_tiles = not st.session_state.get('show_tiles', False)
        
        if predict_btn:
            st.session_state.prediction_started = True
    
    # Extracted tiles section with expander
    if st.session_state.get('show_tiles', False) and st.session_state.get('analysis_complete', False):
        tile_images = get_limited_tile_images(st.session_state.current_output_dir)
        
        with st.expander("Extracted Satellite Tiles", expanded=True):
            display_tile_images(tile_images, st.session_state.current_output_dir)
    
    # Prediction progress section
    if st.session_state.get('prediction_started', False):
        st.markdown("---")
        st.markdown("### 🌊 Flood Prediction Analysis")
        
        progress_container = st.container()
        
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_prediction_progress(progress):
                progress_bar.progress(progress)
                status_text.text(f"Analyzing images: {progress * 100:.1f}%")
            
            # Process flood prediction
            prediction_result = process_flood_prediction(
                st.session_state.current_output_dir,
                st.session_state.current_state_name,
                progress_callback=update_prediction_progress
            )
            
            if 'error' in prediction_result:
                st.error(f"Prediction failed: {prediction_result['error']}")
            else:
                total_images = prediction_result['total_images']
                total_flooded = prediction_result['total_flooded']
                flooded_percentage = prediction_result['flooded_percentage']
                
                status_text.text(f"✅ Analysis Complete!")
                
                # Display summary
                col_summary1, col_summary2, col_summary3 = st.columns(3)
                
                with col_summary1:
                    st.metric("Total Images", total_images)
                
                with col_summary2:
                    st.metric("Flooded Areas", total_flooded)
                
                with col_summary3:
                    st.metric("Flood Percentage", f"{flooded_percentage:.1f}%")
                
                st.session_state.prediction_complete = True
                st.session_state.prediction_started = False
                
                # Auto-show predictions if flooded areas found
                if total_flooded > 0:
                    st.session_state.show_predictions = True
    
    # Flood predictions section with expander
    if st.session_state.get('prediction_complete', False):
        
        # Show predictions button
        view_pred_btn = st.button("🌊 View Flood Predictions", key="view_predictions_btn", use_container_width=True)
        if view_pred_btn:
            st.session_state.show_predictions = not st.session_state.get('show_predictions', False)
        
        # Expandable section for predicted images
        if st.session_state.get('show_predictions', False):
            with st.expander("🌊 Flooded Areas Detection", expanded=True):
                display_flooded_images_section(st.session_state.current_state_name)