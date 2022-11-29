import argparse
import json
import os
import urllib.parse
from dataclasses import dataclass

from datetime import datetime
from pathlib import Path

import boto3
from shapely import geometry

s3 = boto3.client('s3')

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


@dataclass(frozen=True)
class ExtraItemMetadata:
    season: str
    date_range: tuple[datetime, datetime]
    datetime: datetime
    polarization: str


@dataclass(frozen=True)
class ItemMetadata:
    id: str
    bbox: geometry.Polygon
    tileid: str
    product: str
    extra: ExtraItemMetadata = None


def get_s3_url() -> str:
    bucket = 'sentinel-1-global-coherence-earthbigdata'
    location = s3.get_bucket_location(Bucket=bucket)['LocationConstraint']
    return f'https://{bucket}.s3.{location}.amazonaws.com'


def write_stac_items(s3_keys: list[str], s3_url: str) -> None:
    dirname = 'stac-items'
    if not os.path.exists(dirname):
        os.mkdir(dirname)

    for count, s3_key in enumerate(s3_keys, start=1):
        print(f'Creating STAC items: {count}/{len(s3_keys)}', end='\r')
        item = create_stac_item(s3_key, s3_url)
        with open(os.path.join(dirname, item['id'] + '.json'), 'w') as f:
            json.dump(item, f)


def create_stac_item(s3_key: str, s3_url: str) -> dict:
    # TODO tests
    metadata = parse_s3_key(s3_key)
    item = {
        "type": "Feature",
        "stac_version": "1.0.0",
        "id": metadata.id,
        "properties": {
            "tileid": metadata.tileid,
            "sar:instrument_mode": "IW",
            "sar:frequency_band": "C",
            "sar:product_type": metadata.product,  # TODO this was hard-coded to COH in Forrest's stac ext code?
            "sar:center_frequency": 5.405,
            "sar:looks_range": 12,
            "sar:looks_azimuth": 3,
            "sar:observation_direction": "right",
            "start_datetime": datetime_to_str(SEASON_DATE_RANGES['WINTER'][0]),
            "end_datetime": datetime_to_str(SEASON_DATE_RANGES['FALL'][1]),
        },
        "geometry": geometry.mapping(metadata.bbox),
        "assets": {
            "DATA": {
                "href": urllib.parse.urljoin(s3_url, s3_key),
                "type": "image/tiff; application=geotiff",
            },
        },
        "bbox": metadata.bbox.bounds,
        "stac_extensions": ["https://stac-extensions.github.io/sar/v1.0.0/schema.json"],
        "collection": "sentinel-1-global-coherence",
    }
    if metadata.extra:
        item['properties'].update(
            {
                "season": metadata.extra.season,
                "start_datetime": datetime_to_str(metadata.extra.date_range[0]),
                "end_datetime": datetime_to_str(metadata.extra.date_range[1]),
                "datetime": datetime_to_str(metadata.extra.datetime),
                "sar:polarizations": [metadata.extra.polarization],
            }
        )
    return item


def datetime_to_str(dt: datetime) -> str:
    # TODO can we assume utc?
    return dt.isoformat() + 'Z'


def parse_s3_key(s3_key: str) -> ItemMetadata:
    # TODO tests
    item_id = item_id_from_s3_key(s3_key)
    parts = item_id.upper().split('_')
    if len(parts) == 3:
        tileid, _, product = parts
        bbox = tileid_to_bbox(tileid)
        metadata = ItemMetadata(
            id=item_id,
            bbox=bbox,
            tileid=tileid,
            product=product,
        )
    else:
        tileid, season, polarization, product = parts
        bbox = tileid_to_bbox(tileid)
        metadata = ItemMetadata(
            id=item_id,
            bbox=bbox,
            tileid=tileid,
            product=product,
            extra=ExtraItemMetadata(
                season=season,
                date_range=SEASON_DATE_RANGES[season],
                datetime=SEASON_DATETIME_AVERAGES[season],
                polarization=polarization,
            ),
        )
    return metadata


def item_id_from_s3_key(s3_key: str) -> str:
    basename = s3_key.split('/')[-1]
    return basename.split('.')[0]


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
    parser.add_argument('-n', '--number-of-items', type=int, help='Number of items to create')
    return parser.parse_args()


def main():
    args = parse_args()

    with open(args.s3_objects, 'r') as f:
        s3_keys = f.read().splitlines()[:args.number_of_items]

    s3_url = get_s3_url()
    write_stac_items(s3_keys, s3_url)


if __name__ == '__main__':
    main()
