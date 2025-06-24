import geopandas as gpd
import folium
import os
import requests
import numpy as np
from PIL import Image
import math
import pandas as pd
from shapely import wkt

def load_geodata():
    """Load geographic data from CSV file"""
    df = pd.read_csv("src/India_new_political_map/india_map.csv")
    return df

def get_state_geometry_and_bounds(df, state_name):
    """Extract state geometry and calculate bounds"""
    state_row = df[df['ST_NAME'].str.lower() == state_name.lower()]
    
    if state_row.empty:
        return None, None, None
    
    state_data = state_row.iloc[0]
    
    if 'geometry' in state_data and state_data['geometry']:
        geometry = wkt.loads(state_data['geometry'])
        minx, miny, maxx, maxy = geometry.bounds
        return state_data, geometry, (minx, miny, maxx, maxy)
    
    return None, None, None

def calculate_tile_parameters(bounds, tiles_number):
    """Calculate tile parameters for satellite image capture"""
    minx, miny, maxx, maxy = bounds
    center_lat = (miny + maxy) / 2
    center_lon = (minx + maxx) / 2
    
    tile_size_meters = tiles_number * 50
    
    # Calculate lat/lon steps
    lat_step = meters_to_degrees_lat(tile_size_meters)
    lon_step = meters_to_degrees_lon(center_lat, tile_size_meters)
    
    # Calculate number of tiles needed
    lat_tiles = math.ceil((maxy - miny) / lat_step)
    lon_tiles = math.ceil((maxx - minx) / lon_step)
    total_tiles = lat_tiles * lon_tiles
    
    # Determine zoom level based on tile size
    if tile_size_meters <= 250 * 50:
        zoom = 17
    elif tile_size_meters <= 1000 * 50:
        zoom = 16
    else:
        zoom = 15
    
    return {
        'center': (center_lat, center_lon),
        'tile_size_meters': tile_size_meters,
        'lat_step': lat_step,
        'lon_step': lon_step,
        'lat_tiles': lat_tiles,
        'lon_tiles': lon_tiles,
        'total_tiles': total_tiles,
        'zoom': zoom
    }

def create_state_folium_map(state_data, geometry, center_lat, center_lon):
    """Create a Folium map for the state"""
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=7,
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri World Imagery'
    )
    
    # Add state boundary
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
    
    # Add center marker
    folium.Marker(
        [center_lat, center_lon],
        popup=f"Center: ({center_lon:.6f}, {center_lat:.6f})",
        icon=folium.Icon(color='orange', icon='star')
    ).add_to(m)
    
    return m

def display_state_map_and_tiles(df, state_name, tiles_number=10):
    """Main function to display state map and prepare tile information"""
    state_data, geometry, bounds = get_state_geometry_and_bounds(df, state_name)
    
    if state_data is None or geometry is None or bounds is None:
        return None, None
    
    # Calculate tile parameters
    tile_params = calculate_tile_parameters(bounds, tiles_number)
    
    # Create output directory
    output_dir = f"output/{state_data['ST_NAME'].replace(' ', '_')}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create map
    center_lat, center_lon = tile_params['center']
    map_obj = create_state_folium_map(state_data, geometry, center_lat, center_lon)
    
    # Prepare state info
    state_info = {
        'state_name': state_data['ST_NAME'],
        'bounds': bounds,
        'center': tile_params['center'],
        'tile_size': tile_params['tile_size_meters'],
        'output_dir': output_dir,
        'tile_params': tile_params
    }
    
    return map_obj, state_info

def meters_to_degrees_lat(meters):
    """Convert meters to degrees latitude"""
    return meters / 111320

def meters_to_degrees_lon(lat, meters):
    """Convert meters to degrees longitude"""
    return meters / (math.cos(math.radians(lat)) * 111320)

def deg2num(lat_deg, lon_deg, zoom):
    """Convert lat/lon to tile coordinates"""
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)

def download_single_tile(x, y, z, tile_path):
    """Download a single satellite tile"""
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
        print(f"Error downloading tile {x},{y},{z}: {e}")
        return False

def capture_satellite_tiles(bounds, tile_params, output_dir, state_name, progress_callback=None):
    """Capture satellite tiles for the given bounds"""
    minx, miny, maxx, maxy = bounds
    
    lat_step = tile_params['lat_step']
    lon_step = tile_params['lon_step']
    lat_tiles = tile_params['lat_tiles']
    lon_tiles = tile_params['lon_tiles']
    total_tiles = tile_params['total_tiles']
    zoom = tile_params['zoom']
    
    tile_count = 0
    successful_tiles = 0
    
    for i in range(lat_tiles):
        for j in range(lon_tiles):
            # Calculate tile bounds
            tile_miny = miny + i * lat_step
            tile_maxy = min(miny + (i + 1) * lat_step, maxy)
            tile_minx = minx + j * lon_step
            tile_maxx = min(minx + (j + 1) * lon_step, maxx)
            
            # Calculate tile center
            tile_center_lat = (tile_miny + tile_maxy) / 2
            tile_center_lon = (tile_minx + tile_maxx) / 2
            
            # Convert to tile coordinates
            x_tile, y_tile = deg2num(tile_center_lat, tile_center_lon, zoom)
            
            # Create tile filename
            tile_filename = f"tile_{i}_{j}_z{zoom}_x{x_tile}_y{y_tile}.png"
            tile_path = os.path.join(output_dir, tile_filename)
            
            # Download tile
            success = download_single_tile(x_tile, y_tile, zoom, tile_path)
            
            if success:
                successful_tiles += 1
            
            tile_count += 1
            
            # Update progress
            if progress_callback:
                progress = tile_count / total_tiles
                progress_callback(progress)
    
    return successful_tiles, tile_count

def get_tile_images(output_dir):
    """Get list of tile images from output directory"""
    if not os.path.exists(output_dir):
        return []
    
    tile_files = [f for f in os.listdir(output_dir) if f.endswith('.png')]
    return sorted(tile_files)

def get_limited_tile_images(output_dir, limit=10):
    """Get limited number of tile images for display"""
    tile_files = get_tile_images(output_dir)
    return tile_files[:limit] if len(tile_files) > limit else tile_files