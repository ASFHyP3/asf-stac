from datetime import datetime, timezone

import create_hand_items


def test_get_dem_url():
    expected = 'https://copernicus-dem-30m.s3.eu-central-1.amazonaws.com/Copernicus_DSM_COG_10_N00_00_E006_00_DEM/' \
               'Copernicus_DSM_COG_10_N00_00_E006_00_DEM.tif'
    assert create_hand_items.get_dem_url('Copernicus_DSM_COG_10_N00_00_E006_00_HAND') == expected

    expected = 'https://copernicus-dem-30m.s3.eu-central-1.amazonaws.com/Copernicus_DSM_COG_10_S81_00_W132_00_DEM/' \
               'Copernicus_DSM_COG_10_S81_00_W132_00_DEM.tif'
    assert create_hand_items.get_dem_url('Copernicus_DSM_COG_10_S81_00_W132_00_HAND') == expected


def test_gdal_info():
    assert create_hand_items.gdal_info(
        'v1/2021/Copernicus_DSM_COG_10_N02_00_W062_00_HAND.tif',
        'https://glo-30-hand.s3.us-west-2.amazonaws.com/',
    )['wgs84Extent'] == {
               'type': 'Polygon',
               'coordinates': [[[-62.0001389, 3.0001389],
                                [-62.0001389, 2.0001389],
                                [-61.0001389, 2.0001389],
                                [-61.0001389, 3.0001389],
                                [-62.0001389, 3.0001389]]],
           }


def test_create_stac_item():
    expected = {
        'type': 'Feature',
        'stac_version': '1.0.0',
        'id': 'Copernicus_DSM_COG_10_N00_00_E006_00_HAND',
        'properties': {
            'datetime': None,
            'start_datetime': datetime(2010, 12, 1, tzinfo=timezone.utc),
            'end_datetime': datetime(2015, 2, 1, tzinfo=timezone.utc),
        },
        'geometry': {
            'type': 'Polygon',
            'coordinates': [[[5.9998611, 1.0001389],
                             [5.9998611, 0.0001389],
                             [6.9998611, 0.0001389],
                             [6.9998611, 1.0001389],
                             [5.9998611, 1.0001389]]],
        },
        'assets': {
            'data': {
                'href': 'foo.com/v1/2021/Copernicus_DSM_COG_10_N00_00_E006_00_HAND.tif',
                'type': 'image/tiff; application=geotiff',
            },
        },
        'bbox': (5.9998611, 0.0001389, 6.9998611, 1.0001389),
        'stac_extensions': [],
        'collection': create_hand_items.COLLECTION_ID,
        'links': [
            {
                'href': 'https://copernicus-dem-30m.s3.eu-central-1.amazonaws.com/'
                        'Copernicus_DSM_COG_10_N00_00_E006_00_DEM/Copernicus_DSM_COG_10_N00_00_E006_00_DEM.tif',
                'type': 'image/tiff; application=geotiff',
                'title': 'GLO-30 Public Copernicus Digital Elevation Model GeoTIFF '
                         'used as input to create this HAND GeoTIFF',
                'rel': 'related',
            },
        ],
    }

    assert create_hand_items.create_stac_item(
        'v1/2021/Copernicus_DSM_COG_10_N00_00_E006_00_HAND.tif',
        'foo.com/',
        {'wgs84Extent': {
            'type': 'Polygon',
            'coordinates': [[[5.9998611, 1.0001389],
                             [5.9998611, 0.0001389],
                             [6.9998611, 0.0001389],
                             [6.9998611, 1.0001389],
                             [5.9998611, 1.0001389]]],
        }},
    ) == expected
