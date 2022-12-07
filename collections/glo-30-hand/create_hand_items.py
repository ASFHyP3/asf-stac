import argparse
import urllib.parse
from pathlib import Path, PurePath

import asf_stac_util
import boto3
from osgeo import gdal
from shapely import geometry

gdal.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN', 'EMPTY_DIR')

s3 = boto3.client('s3')

COLLECTION_ID = 'glo-30-hand'


def get_s3_url() -> str:
    bucket = 'glo-30-hand'
    location = s3.get_bucket_location(Bucket=bucket)['LocationConstraint']
    return f'https://{bucket}.s3.{location}.amazonaws.com/'


def write_stac_items(s3_keys: list[str], s3_url: str, output_file: Path) -> None:
    with output_file.open('w') as f:
        for count, s3_key in enumerate(s3_keys, start=1):
            print(f'Creating STAC items: {count}/{len(s3_keys)}', end='\r')
            gdal_info_output = gdal_info(s3_key, s3_url)
            stac_item = create_stac_item(s3_key, s3_url, gdal_info_output)
            f.write(asf_stac_util.jsonify_stac_item(stac_item) + '\n')


def gdal_info(s3_key: str, s3_url: str) -> dict:
    url = f'/vsicurl/{urllib.parse.urljoin(s3_url, s3_key)}'
    return gdal.Info(url, format='json')


def create_stac_item(s3_key: str, s3_url: str, gdal_info_output: dict) -> dict:
    item_id = PurePath(s3_key).stem
    item_geometry = gdal_info_output['wgs84Extent']
    return {
        'type': 'Feature',
        'stac_version': '1.0.0',
        'id': item_id,
        'properties': {
            'datetime': None,
            'start_datetime': '2010-12-01T00:00:00Z',
            'end_datetime': '2015-02-01T00:00:00Z',
        },
        'geometry': item_geometry,
        'assets': {
            'data': {
                'href': urllib.parse.urljoin(s3_url, s3_key),
                'type': 'image/tiff; application=geotiff',
            },
        },
        'bbox': geometry.shape(item_geometry).bounds,
        'stac_extensions': [],
        'collection': COLLECTION_ID,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('s3_objects', type=Path, help='Path to a text file containing the list of S3 objects')
    parser.add_argument('-o', '--output-file', type=Path, help='Path for the output file',
                        default='glo-30-hand.ndjson')
    parser.add_argument('-n', '--number-of-items', type=int, help='Number of items to create')
    return parser.parse_args()


def main():
    args = parse_args()

    with args.s3_objects.open() as f:
        s3_keys = f.read().splitlines()[:args.number_of_items]

    s3_url = get_s3_url()
    write_stac_items(s3_keys, s3_url, args.output_file)


if __name__ == '__main__':
    main()
