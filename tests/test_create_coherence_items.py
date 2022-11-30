from datetime import timedelta

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

