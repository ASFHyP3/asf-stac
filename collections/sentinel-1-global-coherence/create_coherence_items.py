import argparse

from datetime import datetime
from pathlib import Path

from shapely import geometry

SEASON_DATE_RANGES = {
    'WINTER': (datetime(2019, 12, 1), datetime(2020, 2, 28)),
    'SPRING': (datetime(2020, 3, 1), datetime(2020, 5, 31)),
    'SUMMER': (datetime(2020, 6, 1), datetime(2020, 8, 31)),
    'FALL': (datetime(2020, 9, 1), datetime(2020, 11, 30)),
}

SEASON_DATETIME_AVERAGES = {
    'WINTER': datetime(2020, 1, 14, 12),
    'SPRING': datetime(2020, 4, 15, 12),
    'SUMMER': datetime(2020, 7, 16, 12),
    'FALL': datetime(2020, 10, 16, 0),
}


# TODO metadata won't always have the required fields
# TODO use stac extension
def create_stac_item(s3_key: str) -> dict:
    # TODO tests
    item_id = s3_key.split('/')[-1]  # TODO include this in metadata?
    metadata = parse_s3_key(s3_key)
    return {
        "type": "Feature",
        "stac_version": "1.0.0",
        "id": item_id,
        "properties": {
            "tileid": metadata['tileid'],
            "season": metadata['season'],
            "start_datetime": metadata['date_range'][0],
            "end_datetime": metadata['date_range'][1],
            "sar:instrument_mode": "IW",  # TODO is this variable?
            "sar:frequency_band": "C",  # TODO is this variable?
            "sar:polarizations": [metadata['polarization']],  # TODO is this correct?
            "sar:product_type": metadata['product'],
            "sar:center_frequency": 5.405,  # TODO is this variable?
            "sar:looks_range": 12,  # TODO is this variable?
            "sar:looks_azimuth": 3,  # TODO is this variable?
            "sar:observation_direction": "right",  # TODO is this variable?
            "datetime": metadata['datetime'],
        },
        "geometry": geometry.mapping(metadata['bbox']),
        "assets": {
            "DATA": {
                "href": get_url(s3_key),
                "type": "image/tiff; application=geotiff",
            },
        },
        "bbox": metadata['bbox'].bounds,
        "stac_extensions": ["https://stac-extensions.github.io/sar/v1.0.0/schema.json"],
        "collection": "sentinel-1-global-coherence",
    }


def parse_s3_key(key: str) -> dict:
    # TODO tests
    parts = key.upper().split('/')[-1].split('_')
    if len(parts) == 3:
        tileid, _, product = parts
        bbox = tileid_to_bbox(tileid)
        metadata = {
            'bbox': bbox,
            'tileid': tileid,
            'product': product,
        }
    else:
        tileid, season, polarization, product = parts
        bbox = tileid_to_bbox(tileid)
        metadata = {
            'bbox': bbox,
            'tileid': tileid,
            'product': product,
            'date_range': SEASON_DATE_RANGES[season],
            'datetime': SEASON_DATETIME_AVERAGES[season],
            'season': season,
            'polarization': polarization,
        }
    return metadata


# TODO why is there an extra zero in N48W090, will this cause issues?
def tileid_to_bbox(tileid: str) -> geometry.Polygon:
    # TODO tests
    north = int(tileid[1:3])
    if tileid[0] == 'S':
        north *= -1
    south = north - 1

    west = int(tileid[4:7])
    if tileid[3] == 'W':
        west *= -1
    east = west + 1
    bbox = geometry.box(west, south, east, north)
    return bbox


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('s3_objects', type=Path, help='Path to a text file containing the list of S3 objects')
    return parser.parse_args()


def main():
    args = parse_args()

    with open(args.s3_objects, 'r') as f:
        s3_keys = f.readlines()

    # TODO generate stac items


if __name__ == '__main__':
    main()
