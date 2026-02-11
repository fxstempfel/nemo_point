import pathlib

import geopandas as gpd
from OSMPythonTools.overpass import Overpass
from shapely.geometry import box, shape
from shapely.ops import unary_union


OSM_REGION_NAME = "France métropolitaine"
PATH_LAND_POLYGON = r"D:\Documents\osm_land_poolygon_split_4326\land-polygons-split-4326\land_polygons.shp"

# Load land polygons
print("Loading global land polygons...")
land_gdf = gpd.read_file(PATH_LAND_POLYGON)
print(f"Loaded {len(land_gdf)} land polygons")


def get_region_geometry(name: str, admin_level: str | None = None):
    """Query a region by name from OSM and return its Shapely geometry (WGS84)."""
    overpass = Overpass()
    query = f"""
    relation
      ["boundary"="administrative"]
      ["name"="{name}"]
      {f'["admin_level"="{admin_level}"]' if admin_level else ""};
    out geom;
    """
    result = overpass.query(query)
    relations = result.relations()
    if not relations:
        raise ValueError(f"No relation found for {name}")

    region = shape(relations[0].geometry())
    return region


def clip_region_to_land(region_geom):
    """Clip a Shapely region geometry to land territory only.
    
    Both are assumed to be in EPSG:4326.
    """
    # Use region bbox to pre-filter land polygons (important for performance)
    minx, miny, maxx, maxy = region_geom.bounds
    bbox = box(minx, miny, maxx, maxy)

    # Spatial prefilter using GeoPandas
    land_subset = land_gdf[land_gdf.intersects(bbox)]

    # Merge only relevant land pieces
    land_union = unary_union(land_subset.geometry)

    # Intersect region with land
    land_region = region_geom.intersection(land_union)

    return land_region


if __name__ == "__main__":
    print("Querying region from OSM...")
    region = get_region_geometry(OSM_REGION_NAME)

    print("Clipping to land...")
    land_region = clip_region_to_land(region)

    pathlib.Path(f"region_{OSM_REGION_NAME.lower()}.wkt").write_text(land_region.wkt)
