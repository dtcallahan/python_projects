from rasterio.mask import mask
import numpy as np
from shapely.geometry import Polygon
import geopandas as gpd


def mean_ws(geodataframe_of_regions, wtk_raster_ob, region_identifier):
    """Takes a geodataframe, masks against the provided WTK raster and return a
    dictionary of averaged values for each region.

    Parameters
    ----------
    geodataframe_of_regions : Geopandas Geodataframe
        Input geodataframe
    wtk_raster_ob : Rasterio raster
        Opened raster object
    region_identifier : str
        Defines the region name on the geodataframe

    Returns
    -------
    dict
        Dict of averaged wind speeds
    """
    if geodataframe_of_regions.crs != wtk_raster_ob.crs:
        geodataframe_of_regions = geodataframe_of_regions.to_crs(wtk_raster_ob.crs)

    results = []
    for idx, region in geodataframe_of_regions.iterrows():
        try:
            masked_wtk, transform = mask(dataset=wtk_raster_ob,
                                        shapes=[region['geometry']],
                                        crop=True)
            region_ws = masked_wtk.mean()
            
            data_dict = {
                region_identifier: region[region_identifier],
                "avg_ws": region_ws
                }
            
            results.append(data_dict)
        
        except Exception as e:
            print('Oh no it bork on', region[region_identifier], e)

    return results

def create_grid(cell_size, bounds, crs):

    xmin = bounds[0]
    xmax = bounds[2]
    ymin = bounds[1]
    ymax = bounds[3]

    rows = int(np.ceil((ymax - ymin) / cell_size))
    cols = int(np.ceil((xmax - xmin) / cell_size))

    x_left_origin = xmin
    x_right_origin = xmin - cell_size

    y_top_origin = ymax
    y_bottom_origin = ymax - cell_size

    polygons = []
    ids = []
    for i in range(cols):
        y_top = y_top_origin
        y_bottom = y_bottom_origin
        for j in range(rows):
            #build poly
            poly = Polygon([
                (x_left_origin, y_top), (x_right_origin, y_top),
                (x_right_origin, y_bottom), (x_left_origin, y_bottom)
            ])

            polygons.append(poly)
            ids.append(f'{str(i)} - {str(j)}')

            y_top = y_top - cell_size
            y_bottom = y_bottom - cell_size
        
        x_left_origin = x_left_origin - cell_size
        x_right_origin = x_right_origin - cell_size
    
    grid = gpd.GeoDataFrame({'ids': ids, 'geometry': polygons}, crs=crs, geometry='geometry')

    return grid