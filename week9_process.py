import rasterio
import glob
import numpy as np
from rasterio.plot import show
from sklearn.cluster import KMeans

np.seterr(divide='ignore', invalid='ignore')

DATA_DIR = './data'

tiffs = glob.glob(DATA_DIR + '/**/*.tiff')

with rasterio.open(tiffs[0]) as raster:
    print(raster.count, 'bands on this raster')

    no_data = raster.nodata
    band3 = raster.read(1)
    band5 = raster.read(2)

    NDWI_array = (band3.astype('float32') - band5.astype('float32')) / (band3.astype('float32') + band5.astype('float32'))

    out_meta = raster.meta.copy()
    out_meta.update({'dtype': 'float32'})

    with rasterio.open(f"{DATA_DIR}/ndwi_result.tiff", 'w', **out_meta) as out_raster:
        out_raster.write(NDWI_array, 1)

    NDWI_array = np.where(np.isnan(NDWI_array), 0, NDWI_array)

    raster_data = NDWI_array
    shape = NDWI_array.shape
    samples = np.column_stack([raster_data.flatten(), raster_data.flatten()])
    kmeans = KMeans(n_clusters=2, random_state=0).fit_predict(samples)
    result_kmeans = kmeans.reshape(shape).astype('float32')


    with rasterio.open(f"{DATA_DIR}/ndwi_kmeans.tiff", 'w', **out_meta) as out_raster:
        out_raster.write(result_kmeans, 1)
