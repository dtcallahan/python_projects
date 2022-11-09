"""The nearest neighbor problem

Problem Statement
Resample the WTK raster by downsampling it to 1/8 of the original resolution.
Generate 1000 random sample points, make sure that such point does not fall on a zero value cell.
For each sample point get the closest 8 values around it.
"""

from scipy.spatial import ckdtree, kdtree

import numpy as np
from scipy.spatial import cKDTree
import rasterio
from rasterio.enums import Resampling
from rasterio.plot import show
import random
import pandas as pd
from shapely.geometry import Point
import geopandas as gpd

random.seed(0)

wkt_path = '/Users/roliveir/Documents/GEOG5092/Fall-2021/week6/data/wtk_conus_100m_mean_masked.tif'

sampling_factor = 1/8

with rasterio.open(wkt_path) as wtk_raster:
    data = wtk_raster.read(
        out_shape=[
            wtk_raster.count,
            int(wtk_raster.height * sampling_factor),
            int(wtk_raster.width * sampling_factor)
        ],
        resampling=Resampling.average
    )

    old_transform = wtk_raster.transform
    new_transform = wtk_raster.transform * wtk_raster.transform.scale(
        (wtk_raster.width / data.shape[2]),
        (wtk_raster.height / data.shape[1])
    )

    with rasterio.open('./out_data/resampled_wtk.tif', 'w',
                       driver='GTiff',
                       height=data.shape[1],
                       width=data.shape[2],
                       count=1,
                       dtype='float32',
                       crs=wtk_raster.crs,
                       transform=new_transform,
                       nodata=wtk_raster.nodata,
    ) as out_raster:
        data = data.astype('float32')
        out_raster.write(data, indexes=1)

with rasterio.open('./out_data/resampled_wtk.tif') as resampled_raster:
    cell_size = resampled_raster.transform[0]
    
    n_samples = 1000
    created_samples = 0
    extent = resampled_raster.bounds
    points = []

    while created_samples < n_samples:
        point = [random.uniform(extent[0], extent[2]),
                 random.uniform(extent[1], extent[3])]

        value_generator = resampled_raster.sample([point])
        
        for value in value_generator:
            if value > 0:
                points.append(point)
                created_samples += 1

x_ccords = np.arange(extent[0] + cell_size / 2, extent[2], cell_size)
y_ccords = np.arange(extent[1] + cell_size / 2, extent[3], cell_size)

x, y = np.meshgrid(x_ccords, y_ccords)

coords = np.c_[x.flatten(), y.flatten()]

tree = cKDTree(coords)

dist, indexes = tree.query(points, k=1)

with rasterio.open('./out_data/resampled_wtk.tif') as resampled_raster:
    data = resampled_raster.read(1)
    
    data = data.flatten()
        
    search = data[indexes]

    df = pd.DataFrame()
    df['coords'] = points
    df['values'] = search
    df['geometry'] = df.apply(lambda row: Point(row['coords'][0], row['coords'][1]), axis=1)

    df = gpd.GeoDataFrame(df, geometry='geometry', crs=resampled_raster.crs)
    df.to_file('./out_data/nearest_points_results.shp')
            