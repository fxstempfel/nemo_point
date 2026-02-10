import logging
import pathlib

import folium
import folium.vector_layers
import pandas as pd
from geopy.distance import distance
from scipy import spatial
from shapely import wkt
from shapely import MultiPoint, Point


logging.basicConfig(
     level=logging.INFO, 
     format= '%(asctime)s {%(pathname)s:%(lineno)d} [%(levelname)s] %(message)s',
 )

REGION = "Yonne"


def load_points():
    """Read a MultiPoint with coordinates as (lon, lat)."""
    return wkt.loads(pathlib.Path("points.wkt").read_text())


def load_region():
    """Read a (Multi)Polygon with coordinates as (lon, lat)."""
    return wkt.loads(pathlib.Path(f"region_{REGION.lower()}.wkt").read_text())


def filter_points(points: MultiPoint) -> MultiPoint:
    """Filter points by removing points that are close to each other"""
    # TODO


def compute_min_distances(
        voronoi: spatial.Voronoi,
        points: list[Point],
        region,
    ) -> pd.DataFrame:
    """For all Voronoi vertices, compute minimal distance to points."""
    points = pd.Series(points)
    logging.info(f"Computing minimum distance to {len(points)} points")

    min_distances = []
    min_points = []
    min_vertice = []

    vertices = voronoi.vertices
    logging.info(f"{len(vertices)} to process...")
    for i, vertice in enumerate(vertices):
        if i % 10 == 0:
            logging.info(f"Processing vertice #{i + 1}/{len(vertices)}")
        pt_vertice = Point(vertice)
        if not region.contains(pt_vertice):
            continue

        # compute distances from all points to this vertice
        distances = points.apply(lambda x: distance(vertice, (x.x, x.y)))

        # only keep the point that has the minimal distance to this vertice
        arg_min = distances.argmin()
        min_distances.append(distances[arg_min])
        min_points.append(points[arg_min])
        min_vertice.append(pt_vertice)
    
    return pd.DataFrame({"dist": min_distances, "point": min_points, "vertice": min_vertice})


def fill_map(map: folium.Map, points: list[Point], nemos: pd.DataFrame):
    # add points to map
    for p in points:
        folium.Marker(
            location=(p.y, p.x),
            icon=folium.Icon(color="green"),
            tooltip=str(p),
        ).add_to(map)
    
    # add Nemo point to map
    nemos.apply(lambda row: folium.Marker(
        location=(row["vertice"].y, row["vertice"].x),
        icon=folium.Icon(color="blue"),
        tooltip=f'{row["vertice"]} is {row["dist"]} to {row["point"]}',
    ).add_to(map), axis=1)



if __name__ == "__main__":
    # TODO 
    #  - add buffer to region when searching for pitches: we want to consider pitches that are in neighbor regions
    #  - filter points for performance
    #  - show Nemo point in a different color than top 10
    #  - config file
    #  - readme

    pts = load_points()
    region = load_region()
    centre = region.centroid
    map = folium.Map(location=(centre.y, centre.x))
    border = zip(list(region.boundary.xy[1]), list(region.boundary.xy[0]))
    folium.vector_layers.Polygon(
        border,
        tooltip=REGION,
        color="red",
    ).add_to(map)

    pts = list(pts.geoms)
    voronoi = spatial.Voronoi([(x.x, x.y) for x in pts])
    df = compute_min_distances(voronoi, points=pts, region=region)
    
    # the Nemo point corresponds to the maximum distance. Keep the first 10 Nemo points
    df = df.sort_values("dist", ascending=False).head(10)
    nemo = df.iloc[0]
    print(f"Nemo point is {nemo.vertice}, with a distance of {nemo.dist}")

    fill_map(map, points=pts, nemos=df)

    map.save("map.html")
    