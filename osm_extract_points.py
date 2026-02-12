import pathlib

from OSMPythonTools.overpass import Overpass
from shapely.geometry import MultiPoint
from shapely.geometry import shape


REGION = "France métropolitaine"
BUFFER_KM = 30

# get region geometry
overpass = Overpass()
buffer_m = BUFFER_KM * 1000
query = f"""
relation
  ["boundary"="administrative"]
  ["name"="{REGION}"];
map_to_area -> .a;

(
  # within the area
  node["sport"="soccer"]["leisure"="pitch"](area.a);
  way["sport"="soccer"]["leisure"="pitch"](area.a);
  relation["sport"="soccer"]["leisure"="pitch"](area.a);

  # around the area
  node["sport"="soccer"]["leisure"="pitch"](around.a:{buffer_m});
  way["sport"="soccer"]["leisure"="pitch"](around.a:{buffer_m});jj
  relation["sport"="soccer"]["leisure"="pitch"](around.a:{buffer_m});
);

out geom;
"""
result = overpass.query(query, timeout=6000)
results = result.elements()
print(f"Found {len(results)} results")

centers = MultiPoint([shape(x.geometry()).centroid for x in results])
pathlib.Path(f"points_{REGION.lower()}.wkt").write_text(centers.wkt)
