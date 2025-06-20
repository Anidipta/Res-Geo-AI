import numpy as np
import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    R = 6371000  # Earth's radius in meters
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * 
         math.sin(delta_lon/2) * math.sin(delta_lon/2))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance

def calculate_coordinates(pixel_x, pixel_y, center_lat, center_lng, image_size=512, zoom=16):
    """Convert pixel coordinates to lat/lng coordinates"""
    
    # Calculate meters per pixel at given zoom level
    meters_per_pixel = 156543.03392 * math.cos(math.radians(center_lat)) / (2 ** zoom)
    
    # Calculate offset in meters from center
    center_pixel = image_size / 2
    offset_x_meters = (pixel_x - center_pixel) * meters_per_pixel
    offset_y_meters = (center_pixel - pixel_y) * meters_per_pixel  # Y is inverted
    
    # Convert meter offsets to lat/lng offsets
    lat_offset = offset_y_meters / 111320.0  # Approx meters per degree latitude
    lng_offset = offset_x_meters / (111320.0 * math.cos(math.radians(center_lat)))
    
    pixel_lat = center_lat + lat_offset
    pixel_lng = center_lng + lng_offset
    
    return pixel_lat, pixel_lng

def get_bounding_box(center_lat, center_lng, size_meters):
    """Get bounding box coordinates for a given center point and size"""
    
    # Approximate conversions
    lat_offset = size_meters / 111320.0  # meters to degrees lat
    lng_offset = size_meters / (111320.0 * math.cos(math.radians(center_lat)))
    
    return {
        'north': center_lat + lat_offset,
        'south': center_lat - lat_offset,
        'east': center_lng + lng_offset,
        'west': center_lng - lng_offset
    }

def pixel_to_meters(pixel_distance, zoom_level, latitude):
    """Convert pixel distance to meters"""
    meters_per_pixel = 156543.03392 * math.cos(math.radians(latitude)) / (2 ** zoom_level)
    return pixel_distance * meters_per_pixel

def format_coordinates(lat, lng):
    """Format coordinates for display"""
    lat_dir = "N" if lat >= 0 else "S"
    lng_dir = "E" if lng >= 0 else "W"
    
    return f"{abs(lat):.6f}°{lat_dir}, {abs(lng):.6f}°{lng_dir}"