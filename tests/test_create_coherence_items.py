from datetime import timedelta, datetime

from shapely import geometry

import create_coherence_items
from create_coherence_items import SEASON_DATE_RANGES, SEASON_DATETIME_AVERAGES


def test_season_datetime_averages():
    assert SEASON_DATETIME_AVERAGES['WINTER'] - SEASON_DATE_RANGES['WINTER'][0] \
        == SEASON_DATE_RANGES['WINTER'][1] - SEASON_DATETIME_AVERAGES['WINTER'] \
        == timedelta(days=44, seconds=43200)

    assert SEASON_DATETIME_AVERAGES['SPRING'] - SEASON_DATE_RANGES['SPRING'][0] \
           == SEASON_DATE_RANGES['SPRING'][1] - SEASON_DATETIME_AVERAGES['SPRING'] \
           == timedelta(days=45, seconds=43200)

    assert SEASON_DATETIME_AVERAGES['SUMMER'] - SEASON_DATE_RANGES['SUMMER'][0] \
           == SEASON_DATE_RANGES['SUMMER'][1] - SEASON_DATETIME_AVERAGES['SUMMER'] \
           == timedelta(days=45, seconds=43200)

    assert SEASON_DATETIME_AVERAGES['FALL'] - SEASON_DATE_RANGES['FALL'][0] \
           == SEASON_DATE_RANGES['FALL'][1] - SEASON_DATETIME_AVERAGES['FALL'] \
           == timedelta(days=45)


def test_parse_s3_key():
    assert create_coherence_items.parse_s3_key('data/tiles/N00E005/N00E005_124D_inc.tif') \
        == create_coherence_items.ItemMetadata(
            id='N00E005_124D_inc',
            bbox=geometry.box(5, -1, 6, 0),
            tileid='N00E005',
            product='INC',
        )

    assert create_coherence_items.parse_s3_key('data/tiles/N00E005/N00E005_fall_vh_AMP.tif') \
        == create_coherence_items.ItemMetadata(
            id='N00E005_fall_vh_AMP',
            bbox=geometry.box(5, -1, 6, 0),
            tileid='N00E005',
            product='AMP',
            extra=create_coherence_items.ExtraItemMetadata(
                season='FALL',
                date_range=(datetime(2020, 9, 1), datetime(2020, 11, 30)),
                datetime=datetime(2020, 10, 16, 0),
                polarization='VH',
            ),
        )

    assert create_coherence_items.parse_s3_key('data/tiles/N00E011/N00E011_winter_vv_COH36.tif') \
        == create_coherence_items.ItemMetadata(
            id='N00E011_winter_vv_COH36',
            bbox=geometry.box(11, -1, 12, 0),
            tileid='N00E011',
            product='COH36',
            extra=create_coherence_items.ExtraItemMetadata(
                season='WINTER',
                date_range=(datetime(2019, 12, 1), datetime(2020, 2, 28)),
                datetime=datetime(2020, 1, 14, 12),
                polarization='VV',
            ),
        )


def test_item_id_from_s3_key():
    assert create_coherence_items.item_id_from_s3_key('path/to/key.tif') == 'key'


def test_bounding_box_from_tile_id():
    assert create_coherence_items.bounding_box_from_tile_id('N49E009') \
           == geometry.box(9, 48, 10, 49)

    assert create_coherence_items.bounding_box_from_tile_id('N48W090') \
        == geometry.box(-90, 47, -89, 48)

    assert create_coherence_items.bounding_box_from_tile_id('S01E012') \
        == geometry.box(12, -2, 13, -1)

    assert create_coherence_items.bounding_box_from_tile_id('S78W161') \
        == geometry.box(-161, -79, -160, -78)
