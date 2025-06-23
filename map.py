import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import os
import requests
import numpy as np
from PIL import Image
import io
import math
import time
import shutil
import pandas as pd

@st.cache_data
def load_geodata():
    df = pd.read_csv("src/India_new_political_map/india_map.csv")
    return df

def display_state_map_and_tiles(df, state_name, tiles_number=10):
    state_row = df[df['ST_NAME'].str.lower() == state_name.lower()]

    if state_row.empty:
        return None, None
    
    state_data = state_row.iloc[0]
    
    if 'geometry' in state_data and state_data['geometry']:
        from shapely import wkt
        geometry = wkt.loads(state_data['geometry'])
        minx, miny, maxx, maxy = geometry.bounds
    else:
        return None, None
    
    center_lat = (miny + maxy) / 2
    center_lon = (minx + maxx) / 2
    
    output_dir = f"output/{state_data['ST_NAME'].replace(' ', '_')}"
    os.makedirs(output_dir, exist_ok=True)
    
    tile_size_meters = tiles_number * 50
    
    map_obj = create_state_map(state_data, center_lat, center_lon, geometry)
    
    return map_obj, {
        'state_name': state_data['ST_NAME'],
        'bounds': (minx, miny, maxx, maxy),
        'center': (center_lat, center_lon),
        'tile_size': tile_size_meters,
        'output_dir': output_dir
    }

def create_state_map(state_data, center_lat, center_lon, geometry):
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=7,
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri World Imagery'
    )
    
    folium.GeoJson(
        geometry.__geo_interface__,
        style_function=lambda x: {
            'color': 'red',
            'weight': 3,
            'fillOpacity': 0,
            'fill': False
        },
        popup=f"State: {state_data['ST_NAME']}",
        tooltip=f"State: {state_data['ST_NAME']}"
    ).add_to(m)
    
    folium.Marker(
        [center_lat, center_lon],
        popup=f"Center: ({center_lon:.6f}, {center_lat:.6f})",
        icon=folium.Icon(color='orange', icon='star')
    ).add_to(m)
    
    return m

def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)

def meters_to_degrees_lat(meters):
    return meters / 111320

def meters_to_degrees_lon(lat, meters):
    return meters / (math.cos(math.radians(lat)) * 111320)

def download_tile(x, y, z, tile_path):
    try:
        url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        with open(tile_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        return False

def capture_satellite_tiles(minx, miny, maxx, maxy, tile_size_meters, output_dir, state_name, progress_callback=None):
    center_lat = (miny + maxy) / 2
    lat_step = meters_to_degrees_lat(tile_size_meters)
    lon_step = meters_to_degrees_lon(center_lat, tile_size_meters)
    
    lat_tiles = math.ceil((maxy - miny) / lat_step)
    lon_tiles = math.ceil((maxx - minx) / lon_step)
    total_tiles = lat_tiles * lon_tiles
    
    if tile_size_meters <= 100*50:
        zoom = 17
    elif tile_size_meters <= 150*50:
        zoom = 16
    else:
        zoom = 15
    
    tile_count = 0
    successful_tiles = 0
    
    for i in range(lat_tiles):
        for j in range(lon_tiles):
            tile_miny = miny + i * lat_step
            tile_maxy = min(miny + (i + 1) * lat_step, maxy)
            tile_minx = minx + j * lon_step
            tile_maxx = min(minx + (j + 1) * lon_step, maxx)
            
            tile_center_lat = (tile_miny + tile_maxy) / 2
            tile_center_lon = (tile_minx + tile_maxx) / 2
            
            x_tile, y_tile = deg2num(tile_center_lat, tile_center_lon, zoom)
            
            tile_filename = f"tile_{i}_{j}_z{zoom}_x{x_tile}_y{y_tile}.png"
            tile_path = os.path.join(output_dir, tile_filename)
            
            success = download_tile(x_tile, y_tile, zoom, tile_path)
            
            if success:
                successful_tiles += 1
            
            tile_count += 1
            
            if progress_callback:
                progress = tile_count / total_tiles
                progress_callback(progress)
    
    return successful_tiles, tile_count

def get_tile_images(output_dir):
    if not os.path.exists(output_dir):
        return []
    
    tile_files = [f for f in os.listdir(output_dir) if f.endswith('.png')]
    return sorted(tile_files)

def render_map_page():
    st.markdown('<div class="page-header" style="text-align: center; padding: 20px; background-color: #667eea; border-radius: 10px; margin-bottom: 20px; color: white; font-family: Arial, sans-serif; font-size: 2rem; font-weight: bold; text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);"><h1>🗺️ Interactive State Analysis</h1></div>', unsafe_allow_html=True)
    
    df = load_geodata()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        
        state_names = sorted(df['ST_NAME'].unique().tolist())
        selected_state = st.selectbox(
            "Select State",
            state_names,
            key="state_selector"
        )
        
        if selected_state:
            tiles_range = st.slider(
                "Tile Range",
                min_value=10,
                max_value=2000,
                value=10,
                step=10,
                key="tiles_slider"
            )
            
            st.markdown("---")
            
            if st.button("🔍 Analysis", key="analysis_btn", use_container_width=True):
                st.session_state.analysis_started = True
                st.session_state.selected_state = selected_state
                st.session_state.tiles_range = tiles_range
            
            if 'analysis_started' in st.session_state and st.session_state.analysis_started:
                progress_container = st.container()
                
                map_obj, state_info = display_state_map_and_tiles(df, selected_state, tiles_range)
                
                if state_info:
                    with progress_container:
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        def update_progress(progress):
                            progress_bar.progress(progress)
                            status_text.text(f"Processing: {progress * 100:.1f}%")
                        
                        minx, miny, maxx, maxy = state_info['bounds']
                        successful_tiles, total_tiles = capture_satellite_tiles(
                            minx, miny, maxx, maxy,
                            state_info['tile_size'],
                            state_info['output_dir'],
                            state_info['state_name'],
                            progress_callback=update_progress
                        )
                        
                        status_text.text(f"✅ Complete: {successful_tiles}/{total_tiles} tiles extracted")
                        st.session_state.analysis_complete = True
                        st.session_state.current_output_dir = state_info['output_dir']
            
            if 'analysis_complete' in st.session_state and st.session_state.analysis_complete:
                st.markdown("---")
                
                if st.button("📁 View Extracted Tiles", key="view_tiles_btn"):
                    st.session_state.show_tiles = not st.session_state.get('show_tiles', False)
                
                if st.session_state.get('show_tiles', False):
                    tile_images = get_tile_images(st.session_state.current_output_dir)
                    
                    if tile_images:
                        st.write(f"**{len(tile_images)} tiles extracted:**")
                        
                        cols = st.columns(3)
                        for idx, tile_name in enumerate(tile_images[:12]):
                            with cols[idx % 3]:
                                tile_path = os.path.join(st.session_state.current_output_dir, tile_name)
                                if os.path.exists(tile_path):
                                    image = Image.open(tile_path)
                                    st.image(image, caption=tile_name, use_container_width=True)
                        
                        if len(tile_images) > 12:
                            st.write(f"... and {len(tile_images) - 12} more tiles")
                    else:
                        st.write("No tiles found")
                
                st.markdown("---")
                
                col_reset, col_predict = st.columns(2)
                
                with col_reset:
                    if st.button("🗑️ Reset", key="reset_btn", use_container_width=True):
                        if os.path.exists(st.session_state.current_output_dir):
                            shutil.rmtree("output")
                        
                        for key in ['analysis_started', 'analysis_complete', 'show_tiles', 'current_output_dir']:
                            if key in st.session_state:
                                del st.session_state[key]
                        
                        st.rerun()
                
                with col_predict:
                    if st.button("🤖 Prediction", key="predict_btn", use_container_width=True):
                        pass
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        if selected_state:
            map_obj, _ = display_state_map_and_tiles(df, selected_state, 10)
            if map_obj:
                st_folium(map_obj, width=700, height=700)
        else:
            st.info("Please select a state to view the map")
    
    if st.button("← Back to Home", key="back_btn"):
        st.session_state.current_page = 'home'
        st.rerun()