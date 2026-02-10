import pathlib

from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.overpass import overpassQueryBuilder, Overpass
from shapely import MultiPoint
from shapely.geometry import shape


nominatim = Nominatim()
area_id = nominatim.query("France métropolitaine").areaId()

overpass = Overpass()
query = overpassQueryBuilder(
    area=area_id,
    elementType="nwr",
    selector=['"sport"="soccer"', '"leisure"="pitch"'], 
    out="geom",
)
result = overpass.query(query, timeout=600)
results = result.elements()
print(f"Found {len(results)} results")

centers = MultiPoint([shape(x.geometry()).centroid for x in results])

pathlib.Path("points.wkt").write_text(centers.wkt)
