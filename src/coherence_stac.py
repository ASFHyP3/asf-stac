from datetime import datetime
from pathlib import Path

import boto3
# import pystac
from shapely import geometry

'''
Design:

[x] connect to aws open bucket containing coherence data
[x] ls the prefixes we're interested in
[x] parse names (N00E014_007D_inc.tif) -> bbox, season, polarization, dataset
[ ] create base sentinel-1 stac item using https://github.com/stac-extensions/sar
[ ] add coherence metadata to base
[ ] add to catalog
[ ] save catalog locally

structure:
    item (tile + season)
        inc
        lsmap
        COH(all 4)
        rho
        rmse
        tau
'''

SEASONS = {
    'winter': (datetime(2019, 12, 1), datetime(2020, 2, 28)),
    'spring': (datetime(2020, 3, 1), datetime(2020, 5, 31)),
    'summer': (datetime(2020, 6, 1), datetime(2020, 8, 31)),
    'fall': (datetime(2020, 9, 1), datetime(2020, 11, 30)),
}


def construct_urls(s3_client, bucket, keys):
    location = s3_client.get_bucket_location(Bucket=bucket)['LocationConstraint']
    urls = [f'https://{bucket}.s3.{location}.amazonaws.com/{k}' for k in keys]
    return urls


def get_object_urls(s3_client, bucket, prefix, requester_pays=False):
    kwargs = {'RequestPayer': 'requester'} if requester_pays else {}
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix, **kwargs)
    keys = [x['Key'] for x in response['Contents']]
    urls = construct_urls(s3_client, bucket, keys)
    return urls


# TODO why is there an extra zero in N48W090, will this cause issues?
def tileid_to_bbox(tileid):
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


def parse_url(url):
    parts = Path(url).stem.split('_')
    if len(parts) == 3:
        tileid, orbit, product = parts
        bbox = tileid_to_bbox(tileid)
        return {'url': url, 'bbox': bbox, 'product': product}

    tileid, season, polarization, product = parts
    bbox = tileid_to_bbox(tileid)
    date_range = SEASONS[season]
    return {'url': url, 'bbox': bbox, 'product': product, 'date_range': date_range, 'polarization': polarization}


if __name__ == '__main__':
    bucket = 'sentinel-1-global-coherence-earthbigdata'
    prefix = 'data/tiles/N48W005/'
    s3 = boto3.client('s3')
    urls = get_object_urls(s3, bucket, prefix, requester_pays=True)
    asset_dicts = [parse_url[x] for x in urls]
