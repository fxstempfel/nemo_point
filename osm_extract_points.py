from OSMPythonTools.overpass import Overpass
from shapely.geometry import MultiPoint
from shapely.geometry import shape

import util


# get region geometry with an Overpass query
overpass = Overpass()
buffer_m = util.CONFIG["buffer_km"] * 1000

filters = [
    "".join(f'["{key}"="{val}"]' for key, val in filter.items())
    for filter in util.CONFIG["osm_filters"]
]
objects = "\n".join(
    f"  {obj}{f}({area});"
    for obj in ("node","way", "relation")
    # area.a within the area, around.a:<buffer> around the area within the buffer
    for area in ("area.a", f"around.a:{buffer_m}")
    for f in filters
)
query = f"""
relation
  ["boundary"="administrative"]
  ["name"="{util.CONFIG['osm_region_name']}"];
map_to_area -> .a;

(
{objects}
);

out geom;
"""
result = overpass.query(query, timeout=6000)
results = result.elements()
print(f"Found {len(results)} results")

centers = MultiPoint([shape(x.geometry()).centroid for x in results])
util.OSM_POINTS_PATH.write_text(centers.wkt)
