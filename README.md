# Compute Nemo point of anything

The Nemo point is the point in the ocean that is the farthest from any land.

We can extend this concept to a point that is defined as the farthest from any point in a set of point. That is the purpose of this repository.

## Prerequisites

- Python
- Install requirements from requirements.txt
- Download the land polygon available at https://osmdata.openstreetmap.de/data/land-polygons.html. Choose the split, WGS84 polygon

## Usage 

1. Extract the target region from OSM with osm_extract_region.py. We will look for a Nemo point within this region only.
2. Extract the target points data set from OSM with osm_extract_points.py. We will look for the point that is within the defined region and the farthest from any of these points. Edit the Overpass API query to retrieve OSM objects that you target (that can be soccer pitches, swimming pools, schools, etc). The tool then takes the centroid of all these objects, to simplify the process.
3. Run nemo.py. This generates an HTML map with the Nemo point, the region boundaries, and the closest point to the Nemo point. 
