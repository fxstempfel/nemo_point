import pathlib

import yaml


with open("config.yml", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)


def normalized_name(name: str) -> str:
    return name.lower().replace(" ", "_")


OSM_REGION_PATH = pathlib.Path(CONFIG["paths"]["resources"]) / f"region_{normalized_name(CONFIG["osm_region_name"])}.wkt"
OSM_POINTS_PATH = pathlib.Path(CONFIG["paths"]["resources"]) / f"points_{normalized_name(CONFIG["osm_region_name"])}.wkt"
MAP_OUTPUT_PATH = pathlib.Path(CONFIG["paths"]["output"]) / f"map_{normalized_name(CONFIG["osm_region_name"])}.html"
