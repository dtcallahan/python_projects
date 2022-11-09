import os
from sentinelhub import SHConfig
from sentinelhub import MimeType, CRS, BBox, SentinelHubRequest, SentinelHubDownloadClient, \
    DataCollection, bbox_to_dimensions, DownloadRequest

config = SHConfig()

# To set-up your own credentials: https://www.sentinel-hub.com/
config.instance_id = ''
config.sh_client_id = ''
config.sh_client_secret = ''

hooverdam_coords_wgs84 = [-114, 35.5, -115, 36.5]

resolution = 60
hooverdam_bbox = BBox(bbox=hooverdam_coords_wgs84, crs=CRS.WGS84)
hooverdam_size = bbox_to_dimensions(hooverdam_bbox, resolution=resolution)

print(f'Image shape at {resolution} m resolution: {hooverdam_size} pixels')

evalscript_all_bands = """
    //VERSION=3
    function setup() {
        return {
            input: [{
                bands: ["B03","B05"],
                units: "DN"
            }],
            output: {
                bands: 2,
                sampleType: "INT16"
            }
        };
    }

    function evaluatePixel(sample) {
        return [sample.B03,            
                sample.B05];
    }
"""

request_all_bands = SentinelHubRequest(
    data_folder='data',
    evalscript=evalscript_all_bands,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL2_L1C,
            time_interval=('2020-01-01', '2020-06-30'),
            mosaicking_order='leastCC'
    )],
    responses=[
        SentinelHubRequest.output_response('default', MimeType.TIFF)
    ],
    bbox=hooverdam_bbox,
    size=hooverdam_size,
    config=config
)

all_bands_response = request_all_bands.save_data()


