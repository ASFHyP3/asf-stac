import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from itertools import repeat
from pathlib import Path
from typing import List, Tuple, Union

import boto3
import pystac
from pystac.extensions import sar
from shapely import geometry
from tqdm import tqdm

"""
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
"""

COHERENCE_DATA_BUCKET = 'sentinel-1-global-coherence-earthbigdata'

SENTINEL1_CENTER_FREQUENCY = 5.405
SEASONS = {
    'WINTER': (datetime(2019, 12, 1), datetime(2020, 2, 28)),
    'SPRING': (datetime(2020, 3, 1), datetime(2020, 5, 31)),
    'SUMMER': (datetime(2020, 6, 1), datetime(2020, 8, 31)),
    'FALL': (datetime(2020, 9, 1), datetime(2020, 11, 30)),
}
LICENSE = 'Creative Commons Attribution 4.0 International Public License'

DATA_CITATION = (
    'Kellndorfer, J. , O. Cartus, M. Lavalle,  C. Magnard, P. Milillo, S. Oveisgharan, B. Osmanoglu, '
    'P. Rosen, and U. Wegmuller. 2022. Global seasonal Sentinel-1 interferometric coherence and backscatter data set. '
    '[Indicate subset used]. Fairbanks, Alaska USA. NASA Alaska Satellite Facility Synthetic Aperture Radar '
    'Distributed Active Archive Center. doi: https://doi.org/10.5067/8W33RRS6S2RV. [Date Accessed].'
)

LITERATURE_CITATION = (
    'Kellndorfer, J. , O. Cartus, M. Lavalle,  C. Magnard, P. Milillo, S. Oveisgharan, B. '
    'Osmanoglu, P. Rosen, and U. Wegmuller. 2022. Global seasonal Sentinel-1 interferometric coherence and '
    'backscatter data set., Scientific Data. https://doi.org/10.1038/s41597-022-01189-6'
)

DESCRIPTION = (
    'This data set is the first-of-its-kind spatial representation of multi-seasonal, global C-band '
    'Synthetic Aperture Radar (SAR) interferometric repeat-pass coherence and backscatter signatures. Coverage '
    'comprises land masses and ice sheets from 82° Northern to 79° Southern latitudes. The data set is derived from '
    'multi-temporal repeat-pass interferometric processing of about 205,000 Sentinel-1 C-band SAR images acquired in '
    'Interferometric Wide-Swath Mode from 1-Dec-2019 to 30-Nov-2020. The data set encompasses three sets of seasonal '
    '(December-February, March-May, June-August, September-November) metrics produced with a pixel spacing of three '
    'arcseconds: 1) Median 6-, 12-, 18-, 24-, 36-, and 48-days repeat-pass coherence at VV or HH polarizations, 2) '
    'Mean radiometrically terrain corrected backscatter (γ0) at VV and VH, or HH and HV polarizations, and 3) '
    'Estimated parameters of an exponential coherence decay model. The data set has been produced to obtain global, '
    'spatially detailed information on how decorrelation affects interferometric measurements of surface displacement '
    'and is rich in spatial and temporal information for a variety of mapping applications.'
)

s3 = boto3.client('s3')


def construct_url(bucket: str, key: str):
    location = s3.get_bucket_location(Bucket=bucket)['LocationConstraint']
    url = f'https://{bucket}.s3.{location}.amazonaws.com/{key}'
    return url


def get_object_urls(bucket: str, prefix: str, requester_pays: bool = False):
    kwargs = {'RequestPayer': 'requester'} if requester_pays else {}
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix, **kwargs)
    keys = [x['Key'] for x in response['Contents']]
    urls = [construct_url(bucket, x) for x in keys]
    return urls


# TODO why is there an extra zero in N48W090, will this cause issues?
def tileid_to_bbox(tileid: str) -> geometry.Polygon:
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


def parse_url(url: str) -> dict:
    parts = Path(url.upper()).stem.split('_')
    if len(parts) == 3:
        tileid, orbit, product = parts
        bbox = tileid_to_bbox(tileid)
        metadata = {'url': url, 'bbox': bbox, 'tileid': tileid, 'product': product}
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


def create_stac_item(yearly_assets: List[dict], seasonal_assets: List[dict]) -> pystac.Item:
    ex_asset = seasonal_assets[0]
    item_id = f'{ex_asset["tileid"]}_{ex_asset["season"]}'
    start_date = ex_asset['date_range'][0]
    end_date = ex_asset['date_range'][1]
    mid_date = start_date + (end_date - start_date) / 2
    polarizations = list(set([x['polarization'].upper() for x in seasonal_assets]))
    properties = {
        'tileid': ex_asset['tileid'],
        'season': ex_asset['season'],
        'start_datetime': start_date.isoformat(),
        'end_datetime': end_date.isoformat(),
    }
    item = pystac.Item(
        id=item_id,
        geometry=geometry.mapping(ex_asset['bbox']),
        bbox=ex_asset['bbox'].bounds,
        datetime=mid_date,
        properties=properties,
    )

    ext_sar = sar.SarExtension.ext(item, add_if_missing=True)
    ext_sar.apply(
        'IW',
        sar.FrequencyBand('C'),
        [sar.Polarization(x) for x in polarizations],
        'COH',
        SENTINEL1_CENTER_FREQUENCY,
        looks_range=12,
        looks_azimuth=3,
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
            asset_properties['temporal_separation'] = f'{int(asset["product"][-2:])} days'
        else:
            asset_properties['product'] = asset['product']

        item.add_asset(
            key=key,
            asset=pystac.Asset(href=asset['url'], media_type=pystac.MediaType.GEOTIFF, extra_fields=asset_properties),
        )
    return item


def create_tile_stac_collection(
        bucket: str, prefix: str,
        date_interval: Tuple[datetime, datetime] = (datetime(2019, 12, 1), datetime(2020, 11, 30))
) -> pystac.collection.Collection:
    urls = get_object_urls(bucket, prefix, requester_pays=True)
    asset_dicts = [parse_url(x) for x in urls]
    items = []

    yearly_assets = [x for x in asset_dicts if ('inc' in x['url']) or ('lsmap' in x['url'])]
    seasons = [x['season'] for x in asset_dicts if not (('inc' in x['url']) or ('lsmap' in x['url']))]
    seasons = list(set(seasons))
    for season in seasons:
        seasonal_assets = [x for x in asset_dicts if season.lower() in x['url']]
        item = create_stac_item(yearly_assets, seasonal_assets)
        items.append(item)

    tileid = asset_dicts[0]['tileid']
    spatial_extent = pystac.SpatialExtent(items[0].bbox)
    temporal_extent = pystac.TemporalExtent(intervals=[date_interval])
    collection_extent = pystac.Extent(spatial=spatial_extent, temporal=temporal_extent)
    collection = pystac.Collection(
        id=tileid,
        description=f'Sentinel-1 Coherence Tile {tileid}',
        extent=collection_extent,
    )
    collection.add_items(items)
    return collection


def safe_create_tile_stac_collection(bucket: str, prefix: str) -> Union[str, pystac.collection.Collection]:
    try:
        collection = create_tile_stac_collection(bucket, prefix)
    except IndexError:
        collection = prefix
    return collection


def create_stac_catalog() -> pystac.catalog.Catalog:
    extra_fields = {'License': LICENSE, 'Data Citation': DATA_CITATION, 'Literature Citation': LITERATURE_CITATION}
    catalog = pystac.Catalog(
        id='sentinel-1-global-coherence-earthbigdata',
        description=DESCRIPTION,
        catalog_type=pystac.CatalogType.RELATIVE_PUBLISHED,
        extra_fields=extra_fields,
    )
    return catalog


def save_stac_catalog_locally(catalog: pystac.catalog.Catalog, catalog_location: Path):
    if not catalog_location.exists():
        catalog_location.mkdir()

    catalog.normalize_hrefs(str(catalog_location))
    catalog.save()

    return catalog_location / 'catalog.json'


def save_stac_catalog_s3(catalog: pystac.catalog.Catalog, bucket: str, key: str) -> str:
    base_url = construct_url(bucket, key)
    catalog.normalize_hrefs(str(base_url))
    catalog.save(dest_href=base_url)
    return base_url


def get_all_tiles(bucket: str, prefix: str, requester_pays: bool = False) -> set:
    kwargs = {
        'Bucket': bucket,
        'Prefix': prefix,
    }
    if requester_pays:
        kwargs['RequestPayer'] = 'requester'

    paginator = s3.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(**kwargs)
    tile_set = set()
    for page in page_iterator:
        keys = [x['Key'] for x in page['Contents']]
        page_tiles = [x.split('/')[2] for x in keys if '.' not in x.split('/')[2]]
        tile_set.update(page_tiles)
        break

    return tile_set


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-c', '--catalog', type=Path, default=Path('coherence_catalog'),
                        help='Location to save the catalog')
    parser.add_argument('-b', '--bucket', help='bucket to upload completed catalog')
    parser.add_argument('-p', '--prefix', help='bucket to upload completed catalog')
    parser.add_argument('-t', '--tile-list', type=Path, help='Line-seperated list of tiles to create collections for')

    parser.add_argument('-v', '--verbose', action='store_true', help='Turn on verbose logging')
    args = parser.parse_args()

    if args.tile_list:
        with open(args.tile_list, 'r') as f:
            tiles = {x.strip() for x in f.readlines()}
    else:
        tiles = get_all_tiles(COHERENCE_DATA_BUCKET, 'data/tiles/')

    prefixes = [f'data/tiles/{x}/' for x in tiles]

    print('creating items...')
    with ThreadPoolExecutor(max_workers=20) as executor:
        tile_collections = list(
            tqdm(
                executor.map(safe_create_tile_stac_collection, repeat(COHERENCE_DATA_BUCKET), prefixes),
                total=len(prefixes),
            )
        )

    print('creating catalog...')
    invalid_tiles = []
    catalog = create_stac_catalog()
    for collection in tqdm(tile_collections):
        if isinstance(collection, pystac.collection.Collection):
            catalog.add_child(collection)
        else:
            print(f'WARNING: Invalid collection! {collection}')
            invalid_tiles.append(collection)

    print('saving catalog...')
    if args.bucket:
        catalog_location = save_stac_catalog_s3(catalog, args.bucket, args.prefix)
    else:
        catalog_location = save_stac_catalog_locally(catalog, args.catalog)
    print(f'Done! Created {catalog_location}')


if __name__ == '__main__':
    main()
