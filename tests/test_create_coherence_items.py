from datetime import timedelta

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
