"""
Adds STAC catalogs, collections, and items to a STAC API application. Skips objects that
already exist.

Assumes that the STAC objects to be ingested are individual json files on the local file system.

Assumes that the STAC API supports the Transaction extension.
"""

import argparse
import json
import urllib
from glob import glob
from urllib.parse import urljoin

import requests


def get_endpoint(stac_object: dict) -> str:
    if stac_object['type'] in ('Catalog', 'Collection'):
        endpoint = '/collections'
    else:
        assert stac_object['type'] == 'Feature'
        endpoint = f'/collections/{stac_object["collection"]}/items'
    return endpoint


def add_stac_object(stac_object: dict, api_url: str, session: requests.Session) -> None:
    print(stac_object['id'])
    url = urllib.parse.urljoin(api_url, get_endpoint(stac_object))
    response = session.post(url, json=stac_object)

    if response.status_code == 409:
        print('Skipping existing object')
    else:
        response.raise_for_status()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('api_url', help='URL for the STAC API.')
    parser.add_argument('json_dir', help='Path to directory containing STAC item JSON files.')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    session = requests.Session()
    json_files = glob(f'{args.json_dir}/*.json')
    for count, json_file in enumerate(json_files, start=1):
        with open(json_file) as f:
            stac_object = json.load(f)
        print(f'{count}/{len(json_files)} ', end='')
        add_stac_object(stac_object, args.api_url, session)


if __name__ == '__main__':
    main()
