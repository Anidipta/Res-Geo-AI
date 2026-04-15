"""Spatial tessellation and tile filtering from boundary polygons."""

import numpy as np
from typing import List, Tuple, Dict, Any
from shapely.geometry import Polygon, box


def compute_mbr(polygons: List[List[Tuple[float, float]]]) -> Tuple[float, float, float, float]:
    # Compute minimum bounding rectangle from all polygon vertices
    all_x = [x for poly in polygons for (x, y) in poly]
    all_y = [y for poly in polygons for (x, y) in poly]
    return min(all_x), max(all_x), min(all_y), max(all_y)


def tessellate_grid(xmin: float, xmax: float, ymin: float, ymax: float, n: int) -> List[Dict]:
    # Divide MBR into n×n tiles and return tile metadata list
    dx = (xmax - xmin) / n
    dy = (ymax - ymin) / n
    tiles = []
    for i in range(n):
        for j in range(n):
            tile_xmin = xmin + i * dx
            tile_xmax = tile_xmin + dx
            tile_ymin = ymin + j * dy
            tile_ymax = tile_ymin + dy
            tiles.append({
                "id": f"tile_{i}_{j}",
                "xmin": tile_xmin, "xmax": tile_xmax,
                "ymin": tile_ymin, "ymax": tile_ymax,
                "bbox": (tile_xmin, tile_ymin, tile_xmax, tile_ymax)
            })
    return tiles


def filter_valid_tiles(tiles: List[Dict], polygons: List[List[Tuple[float, float]]]) -> List[Dict]:
    # Keep only tiles that spatially intersect with at least one boundary polygon
    region_polys = [Polygon(poly) for poly in polygons]
    valid = []
    for tile in tiles:
        tile_box = box(*tile["bbox"])
        if any(tile_box.intersects(rp) for rp in region_polys):
            valid.append(tile)
    return valid


def get_tile_centroid(tile: Dict) -> Tuple[float, float]:
    # Return geographic centroid of a tile
    cx = (tile["xmin"] + tile["xmax"]) / 2
    cy = (tile["ymin"] + tile["ymax"]) / 2
    return cx, cy


def load_region_polygons(geojson_path: str) -> List[List[Tuple[float, float]]]:
    # Parse GeoJSON file and extract polygon coordinate lists
    import json
    with open(geojson_path, "r") as f:
        data = json.load(f)
    polygons = []
    features = data.get("features", [data]) if "features" in data else [data]
    for feat in features:
        geom = feat.get("geometry", feat)
        if geom["type"] == "Polygon":
            polygons.append([tuple(c) for c in geom["coordinates"][0]])
        elif geom["type"] == "MultiPolygon":
            for part in geom["coordinates"]:
                polygons.append([tuple(c) for c in part[0]])
    return polygons


def build_valid_tileset(geojson_path: str, n: int) -> List[Dict]:
    # End-to-end: load region, compute MBR, tessellate, filter valid tiles
    polygons = load_region_polygons(geojson_path)
    xmin, xmax, ymin, ymax = compute_mbr(polygons)
    tiles = tessellate_grid(xmin, xmax, ymin, ymax, n)
    return filter_valid_tiles(tiles, polygons)
