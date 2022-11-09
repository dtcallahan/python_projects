import rasterio
import glob
import pandas as pd
import geopandas as gpd
import numpy as np
from rasterio.plot import show
from Peregrine_Suitability_Functions import slopeAspect, reclassAspect


# Set up global variables, and make a list of raster files

data_path = r'C:\Users\calladel\Documents\Fall 2021\GIS Programming - GEOG 5092\Final_Project\Data'
output_path = r'C:\Users\calladel\Documents\Fall 2021\GIS Programming - GEOG 5092\Final_Project'

master_crs = 'epsg:26955'

raster_files = sorted(glob.glob(data_path + r'\*.tif'))
print(raster_files)


# Read in raster files as np arrays, reclassify for nesting suitability.

with rasterio.open(raster_files[0]) as DEM:
    DEM_array = DEM.read(1)
    DEM_array = DEM_array.astype('int32')
    slp, aspect = slopeAspect(DEM_array, 30)
    reclass_aspect = reclassAspect(aspect)
    
    slope_suit = np.where((slp > 0) & (slp <= 15), 0,
             np.where((slp > 15) & (slp <= 30), 1,
             np.where((slp > 30) & (slp <= 45), 2,
             np.where((slp > 45) & (slp <= 60), 3,
             np.where((slp > 60) & (slp <= 90), 4, 0)))))
    
    aspect_suit = np.where((reclass_aspect == 4) | (reclass_aspect == 5) | (reclass_aspect == 6), 1, 0)
    
    show(slope_suit)
    show(aspect_suit)

with rasterio.open(raster_files[1]) as roads:
    roads_array = roads.read(1)
    
    roads_suit = np.where(roads_array == 1, 0, 1)
    
    show(roads_suit)

with rasterio.open(raster_files[2]) as trails:
    trails_array = trails.read(1)
    
    trails_suit = np.where(trails_array == 1, 0, 1)
    
    show(trails_suit)

    

# Sum suitable arrays to find suitable sites, and most suitable sites

suitable_sites = roads_suit + trails_suit + slope_suit + aspect_suit
most_suitable = np.where(suitable_sites >= 5, 1, 0)
show(suitable_sites)
show(most_suitable)


# Calculating the total area of the most suitable sites

top_unique, top_counts = np.unique(most_suitable, return_counts = True)
n = 900
top_area = (np.multiply(top_counts[1], n))/1000000

print('Total area of the most suitable nesting sites:', round(top_area, 2), 'sq. km.')


# Convert suitable sites array and most suitable sites array to geotiffs

with rasterio.open(raster_files[0]) as template:
    
    with rasterio.open(output_path + r'\suitable_sites.tif', 'w',
        driver = 'GTiff',
        height = suitable_sites.shape[0],
        width = suitable_sites.shape[1],
        count = 1,
        dtype = 'int32',
        transform = template.transform,
        crs = master_crs,
        nodata = -99
    ) as out_raster:
        suitable_sites = suitable_sites.astype('int32')
        out_raster.write(suitable_sites, indexes = 1)
        
    with rasterio.open(output_path + r'\most_suitable.tif', 'w',
        driver = 'GTiff',
        height = most_suitable.shape[0],
        width = most_suitable.shape[1],
        count = 1,
        dtype = 'int32',
        transform = template.transform,
        crs = master_crs,
        nodata = -99
    ) as out_raster:
        most_suitable = most_suitable.astype('int32')
        out_raster.write(most_suitable, indexes = 1)
