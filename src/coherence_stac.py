from datetime import datetime
from pathlib import Path

import boto3
import pystac
from pystac.extensions import sar
from shapely import geometry

'''
Design:

[x] connect to aws open bucket containing coherence data
[x] ls the prefixes we're interested in
[x] parse names (N00E014_007D_inc.tif) -> bbox, season, polarization, dataset
[x] create base sentinel-1 stac item using https://github.com/stac-extensions/sar
[x] add coherence metadata to base
[x] add to catalog
[x] save catalog locally

structure:
    item (tile + season)
        inc
        lsmap
        COH(all 4)
        rho
        rmse
        tau
'''

SENTINEL1_CENTER_FREQUENCY = 5.405
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
        metadata = {'url': url, 'bbox': bbox, tileid: tileid, 'product': product}
        return metadata

    tileid, season, polarization, product = parts
    bbox = tileid_to_bbox(tileid)
    date_range = SEASONS[season]
    metadata = {
        'url': url,
        'bbox': bbox,
        'tileid': tileid,
        'product': product,
        'date_range': date_range,
        'season': season,
        'polarization': polarization,
    }
    return metadata


def create_stac_item(yearly_assets, seasonal_assets):
    ex_asset = seasonal_assets[0]
    item_id = f'{ex_asset["tileid"]}_{ex_asset["season"]}'
    properties = {'tileid': ex_asset['tileid'], 'season': ex_asset['season']}

    item = pystac.Item(
        id=item_id,
        geometry=geometry.mapping(ex_asset['bbox']),
        bbox=ex_asset['bbox'].bounds,
        datetime=ex_asset['date_range'][0],
        properties=properties,
    )

    # TODO don't know if look properties are correct
    ext_sar = sar.SarExtension.ext(item, add_if_missing=True)
    ext_sar.apply(
        'IW',
        sar.FrequencyBand('C'),
        [sar.Polarization('VV'), sar.Polarization('VH')],
        'COH',
        SENTINEL1_CENTER_FREQUENCY,
        looks_range=7,
        looks_azimuth=12,
        observation_direction=sar.ObservationDirection('right'),
    )

    for asset in yearly_assets:
        item.add_asset(
            key=asset['product'],
            asset=pystac.Asset(href=asset['url'], media_type=pystac.MediaType.GEOTIFF),
        )

    for asset in seasonal_assets:
        key = f'{asset["product"]}_{asset["polarization"]}'
        asset_properties = {'polarization': asset['polarization']}
        if 'COH' in asset['product']:
            asset_properties['product'] = 'COH'
            asset_properties['temporal_separation'] = f'{asset["product"][-2:]} days'
        else:
            asset_properties['product'] = asset['product']

        item.add_asset(
            key=key,
            asset=pystac.Asset(href=asset['url'], media_type=pystac.MediaType.GEOTIFF, extra_fields=asset_properties),
        )
    return item


def create_stac_catalog(items):
    extension_list = [x.to_dict()['stac_extensions'] for x in items]
    extensions = list(set([num for sublist in extension_list for num in sublist]))
    catalog = pystac.Catalog(
        id='sentinel-1-global-coherence-earthbigdata',
        description='A catalog containing the Earthbigdata Sentinel-1 Global Coherence Dataset',
        catalog_type=pystac.CatalogType.ABSOLUTE_PUBLISHED,
        stac_extensions=extensions
    )
    catalog.add_items(items)
    return catalog


def save_stac_catalog_locally(catalog, catalog_name: str):
    catalog_name = Path(catalog_name)
    if not catalog_name.exists():
        catalog_name.mkdir()
    catalog.normalize_hrefs(str(catalog_name))
    catalog.save()
    return catalog_name / 'catalog.json'


if __name__ == '__main__':
    bucket = 'sentinel-1-global-coherence-earthbigdata'
    prefix = 'data/tiles/N48W005/'
    s3 = boto3.client('s3')

    urls = get_object_urls(s3, bucket, prefix, requester_pays=True)
    asset_dicts = [parse_url(x) for x in urls]
    items = []

    yearly_assets = [x for x in asset_dicts if ('inc' in x['url']) or ('lsmap' in x['url'])]
    for season in ('spring', 'summer', 'fall', 'winter'):
        seasonal_assets = [x for x in asset_dicts if season in x['url']]
        item = create_stac_item(yearly_assets, seasonal_assets)
        items.append(item)

    catalog = create_stac_catalog(items)
    save_stac_catalog_locally(catalog, 'coherence_catalog')
