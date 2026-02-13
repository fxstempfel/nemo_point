import pathlib

import yaml


with open("config.yml", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)


def normalized_name(name: str) -> str:
    return name.lower().replace(" ", "_")


_target_name = normalized_name(CONFIG["target_name"])
_region_name = normalized_name(CONFIG["osm_region_name"])
OSM_REGION_PATH = pathlib.Path(CONFIG["paths"]["resources"]) / f"region_{_region_name}.wkt"
OSM_POINTS_PATH = pathlib.Path(CONFIG["paths"]["resources"]) / f"points_{_target_name}_{_region_name}.wkt"
MAP_OUTPUT_PATH = pathlib.Path(CONFIG["paths"]["output"]) / f"map_{_target_name}_{_region_name}.html"
