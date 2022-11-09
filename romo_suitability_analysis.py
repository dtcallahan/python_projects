import pandas as pd
import geopandas as gpd
import os
import time

t0 = time.time()

data_dir = '/Users/roliveir/GEOG5092/week3/week3_data'

buffer_dist = 100

roads = gpd.read_file(os.path.join(data_dir, 'Transportation/ROMO_TRANS_Road_ln.shp'))
trails = gpd.read_file(os.path.join(data_dir, 'Trails/ROMO_TRANS_Trail_ln.shp'))
campsites = gpd.read_file(os.path.join(data_dir, 'BackcountryCampsites/campsites.shp'))
lakes = gpd.read_file(os.path.join(data_dir, 'Lakes/lakes.shp'))
streams = gpd.read_file(os.path.join(data_dir, 'Streams_Rivers/streams.shp'))
boundaries = gpd.read_file(os.path.join(data_dir, 'ParkBoundary/nps_boundary.shp'))

master_crs = roads.crs

romo_bnd = boundaries[boundaries['UNIT_CODE'] == 'ROMO']
romo_bnd = romo_bnd.to_crs(master_crs)

print('All data read..')

human_label = ['roads', 'trails', 'campsites']
human_sources = [roads, trails, campsites]

water_label = ['lakes', 'streams']
water_source = [lakes, streams]

def clip_and_buffer_geodataframes(list_gdfs, 
                                  list_of_labels, 
                                  boundary, 
                                  master_crs, 
                                  buffer_dist=100):
    """Given a number of geodataframes, clips each one against the park boundary,
    perform a buffer operation using the provided distance, and dissolve all
    buffer into a single poly.

    Parameters
    ----------
    list_gdfs : list
        List of geodataframes.
    list_of_labels : list
        List of labels.
    boundary : Geopandas Geodataframe
        Park boundary
    master_crs : CRS
        CRS information to be use on all re-project operations.
        Final geodataframe will be on this projection.
    buffer_dist : int, optional
        Buffer distance in meters, by default 100

    Returns
    -------
    Geopandas Geodataframe
        Geodataframe containing the buffer.
    """
    buffer_geoms = []

    for idx, e in enumerate(list_gdfs):
        gdf_buffer = gpd.GeoDataFrame()

        if e.crs != master_crs:
            print(list_of_labels[idx], 'is not on the master projection, reprojecting now...')
            e = e.to_crs(master_crs)

        # Clip each feature to the park bnd, this reduces the number of features we are dealing with.
        print('Clipping', list_of_labels[idx])
        e = gpd.overlay(e, boundary, how='intersection')

        print('Buffering', list_of_labels[idx])
        gdf_buffer['geometry'] = e.buffer(buffer_dist)
        gdf_buffer['source'] = list_of_labels[idx]

        # Dissolving each feature after the buffer improved performance by a lot!
        print('Dissolving', list_of_labels[idx])
        gdf_buffer = gdf_buffer.dissolve(by='source')

        buffer_geoms.append(gdf_buffer)

    unioned_gdf = pd.concat(buffer_geoms)
    unioned_gdf.crs = master_crs

    return unioned_gdf


near_human = clip_and_buffer_geodataframes(human_sources,
                                           human_label,
                                           romo_bnd,
                                           master_crs,
                                           buffer_dist=buffer_dist)

near_water = clip_and_buffer_geodataframes(water_source,
                                           water_label,
                                           romo_bnd,
                                           master_crs,
                                           buffer_dist=buffer_dist)

print('All buffers done')

alway_human = gpd.overlay(romo_bnd, near_human, how='difference')
print('alway_human done')

print('Processing forest')
vegetation = gpd.read_file(os.path.join(data_dir, 'Vegetation/vegetation.shp'))
pine = vegetation[vegetation['MapClass'].str.contains('Pine')]
pine['veg_type'] = 'Pine'
pine = pine.dissolve(by='veg_type')
pine.drop(columns=['OBJECTID', 'SHAPE_Leng', 'SHAPE_Area', 'Poly_ID',
                   'NVC_Elcode', 'Associatio', 'MapClass_C', 'MapClass',
                   'X_Centroid', 'Y_Centroid'], inplace=True)
print('Pine gdf done')

print('Intersecting final areas')
int_water_human = gpd.overlay(near_water, near_human, how='intersection')
suitable_habitat = gpd.overlay(int_water_human, pine, how='intersection')       

suitable_habitat.to_file(os.path.join(data_dir, f'output/suitable_habitat_{buffer_dist}.shp'))

print('Done', round((time.time() - t0)/60, 2), 'min')
