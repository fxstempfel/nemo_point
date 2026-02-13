# Compute Nemo point of anything

The Nemo point is the point in the ocean that is the farthest from any land.

We can extend this concept to a point that is defined as the farthest from any point in a set of point. That is the purpose of this repository.

## Prerequisites

- Install Python
- Install requirements from requirements.txt
- Download the land polygon available at https://osmdata.openstreetmap.de/data/land-polygons.html. Choose the split, WGS84 polygon

## Usage

1. Edit `config.yml` for your use case.
2. Extract the target region from OSM with osm_extract_region.py. We will look for a Nemo point within this region only. This step can be a bit long since it loads the land polygon for the whole world. You can always use a land polygon for your region of interest to improve performance.
3. Extract the target points data set from OSM with osm_extract_points.py. We take points within the defined region and around it, within the specified buffer. Edit `osm_filters` in the configuration to retrieve OSM objects that you target (that can be soccer pitches, swimming pools, schools, etc). The script takes the centroid of all these objects, to simplify the process.
4. Run nemo.py, which looks for the point that is within the defined region and the farthest from any of the points extracted at the previous step. This generates an HTML map with the Nemo point, the region boundaries, and the closest point to the Nemo point. The next few Nemo candidates are included as well.

## Example

The example included in this repository is the point in Metropolitan France that is the farthest from any soccer pitch.
