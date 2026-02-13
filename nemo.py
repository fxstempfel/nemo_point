import logging

import folium
import folium.vector_layers
import numpy as np
import pandas as pd
import pyproj
from scipy import spatial
from shapely import ops, prepared, wkt
from shapely import MultiPolygon, Point, Polygon

import util

logging.basicConfig(
     level=logging.INFO, 
     format= '%(asctime)s {%(pathname)s:%(lineno)d} [%(levelname)s] %(message)s',
 )


def load_points():
    """Read a MultiPoint with coordinates as (lon, lat)."""
    return wkt.loads(util.OSM_POINTS_PATH.read_text())


def load_region():
    """Read a (Multi)Polygon with coordinates as (lon, lat)."""
    return wkt.loads(util.OSM_REGION_PATH.read_text())


def project(obj, transform):
    """Project `obj` to the transformation defined by `transform`."""
    return ops.transform(transform, obj)


def project_region_and_points(region, points):
    transformer = pyproj.Transformer.from_crs(
        "EPSG:4326",  # WGS84 (lon, lat)
        "EPSG:2154",  # Lambert-93
        always_xy=True, # ensures (lon, lat) order
    )

    region = ops.transform(transformer.transform, region)
    points = ops.transform(transformer.transform, points)

    return region, points


def get_region_border(region: MultiPolygon | Polygon) -> list[Polygon]:
    """Make a list of folium Polygons out of a shapely (Multi)Polygon."""
    if isinstance(region, MultiPolygon):
        boundaries = list(region.boundary.geoms)
    else:
        boundaries = [region.boundary]
    
    result = []
    for b in boundaries:
        border = zip(list(b.xy[1]), list(b.xy[0]))
        polygon = folium.vector_layers.Polygon(
            border,
            tooltip=util.CONFIG["osm_region_name"],
            color="red",
        )
        result.append(polygon)

    logging.info(f"Generated {len(result)} polygons")
    return result


def compute_min_distances(voronoi, points, region):
    # Convert points to numpy array
    coords = np.array([(p.x, p.y) for p in points])

    # Prepare region for .contains calls
    region = prepared.prep(region)

    # Build KDTree
    tree = spatial.cKDTree(coords)

    vertices = voronoi.vertices
    results = []
    for i, vertex in enumerate(vertices):
        if i % 1000 == 0:
            logging.info(f"Processing vertex #{i + 1}/{len(vertices)}")

        pt_vertex = Point(vertex)
        if not region.contains(pt_vertex):
            continue

        # Query nearest neighbor (O(log n))
        dist, idx = tree.query(vertex)
        results.append((dist, points[idx], pt_vertex))

    return pd.DataFrame(results, columns=["dist", "point", "vertice"])         


def create_map(region, nemos: pd.DataFrame):
    # project everything back to WGS84
    transformer = pyproj.Transformer.from_crs(
        "EPSG:2154",
        "EPSG:4326",
        always_xy=True,
    )
    region = ops.transform(transformer.transform, region)
    nemos["vertice"] = nemos["vertice"].apply(lambda x: ops.transform(transformer.transform, x))
    nemos["point"] = nemos["point"].apply(lambda x: ops.transform(transformer.transform, x))

    # create map with region outline
    centre = region.centroid
    map = folium.Map(location=(centre.y, centre.x), zoom_start=util.CONFIG.get("map_zoom_start_level", 6))
    border_polygons = get_region_border(region)
    for p in border_polygons:
        p.add_to(map)

    def make_markers(row, is_nemo=False):
        nemo = folium.Marker(
            location=(row["vertice"].y, row["vertice"].x),
            icon=folium.Icon(color="black" if is_nemo else "blue"),
            tooltip=f'{row["vertice"]} is {row["dist"] / 1000:.01f} km to {row["point"]}',
        )
        point = folium.Marker(
            location=(row["point"].y, row["point"].x),
            icon=folium.Icon(color="orange" if is_nemo else "green"),
            tooltip=f'{row["point"]}',
        )
        nemo.add_to(map)
        point.add_to(map)
    
    # add Nemo point to map
    make_markers(nemos.iloc[0], is_nemo=True)

    # add next closest Nemo candidates to map
    nemos.iloc[1:].apply(make_markers, axis=1)

    return map


if __name__ == "__main__":
    pts = load_points()
    region = load_region()
    region, pts = project_region_and_points(region, pts)

    pts = list(pts.geoms)
    voronoi = spatial.Voronoi([(x.x, x.y) for x in pts])
    df = compute_min_distances(voronoi, points=pts, region=region)
    
    # the Nemo point corresponds to the maximum distance. Keep the first 10 Nemo points
    df = df.sort_values("dist", ascending=False).head(10)
    nemo = df.iloc[0]
    print(f"Nemo point is {nemo.vertice}, with a distance of {nemo.dist} meters")

    map = create_map(region=region, nemos=df)
    map.save(util.MAP_OUTPUT_PATH)
    