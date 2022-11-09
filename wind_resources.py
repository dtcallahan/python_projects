"""Problem statement:
Our job is to perform a wind resource characterization analyses.
To summarize wind speed at 100 meter hub height at the following spatial
resolutions:
    * States
    * Counties
    * Regular grid
"""

import rasterio
import geopandas as gpd
import pandas as pd
import numpy as np
import os

from utilities import mean_ws, create_grid

IN_DATA_DIR = './data'
OUT_DATA_DIR = './out_data_2021'

with rasterio.open(os.path.join(IN_DATA_DIR, 'wtk_conus_100m_mean_masked.tif')) as raster_obj:
    data = raster_obj.read(1)
    states = gpd.read_file(os.path.join(IN_DATA_DIR, 'us_states.geojson'))
    counties = gpd.read_file(os.path.join(IN_DATA_DIR, 'us_counties.geojson'))
    
    grid =  create_grid(100000, bounds=raster_obj.bounds, crs=raster_obj.crs)

    processed_states =  mean_ws(geodataframe_of_regions=states,
            wtk_raster_ob=raster_obj,
            region_identifier='state_name')
    
    processed_counties =  mean_ws(geodataframe_of_regions=counties,
            wtk_raster_ob=raster_obj,
            region_identifier='name')
    
    processed_grid =  mean_ws(geodataframe_of_regions=grid,
            wtk_raster_ob=raster_obj,
            region_identifier='ids')

