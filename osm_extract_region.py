import pathlib

from OSMPythonTools.overpass import Overpass
from shapely.geometry import shape


NAME = "France métropolitaine"

overpass = Overpass()

result = overpass.query(f"""
    relation
      ["boundary"="administrative"]
      ["name"="{NAME}"];
    out geom;
""")
relations = result.relations()
region = relations[0]
geometry = shape(region.geometry())

pathlib.Path(f"region_{NAME.lower()}.wkt").write_text(geometry.wkt)
