import create_hand_items


def test_create_stac_item():
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
    ) == {
           'type': 'Feature',
           'stac_version': '1.0.0',
           'id': 'Copernicus_DSM_COG_10_N00_00_E006_00_HAND',
           'properties': {
               'datetime': None,
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
       }
