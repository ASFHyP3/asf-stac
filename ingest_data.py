"""
Adds a STAC dataset to a STAC API application. Skips objects that
already exist.

Assumes that the dataset is arranged as a tree (connected acyclic
graph). This means that all objects should be reachable from the root
object and there should be no cycles.

Assumes that links to child objects are specified as relative
filesystem paths.

Assumes that the STAC API supports the Transaction extension.
"""

import argparse
import json
from pathlib import Path
from urllib.parse import urljoin

import requests


def traverse(stac_object_path: Path, api_url: str) -> None:
    with open(stac_object_path, 'r') as f:
        stac_object: dict = json.load(f)

    print(f'Adding STAC object {stac_object_path}')
    add_stac_object(stac_object, api_url)

    for child_path in get_child_paths(stac_object, stac_object_path.parent):
        traverse(child_path, api_url)


def get_child_paths(stac_object: dict, parent_path: Path) -> list[Path]:
    return [
        parent_path / link_object['href']
        for link_object in stac_object['links'] if link_object['rel'] in ('child', 'item')
    ]


def add_stac_object(stac_object: dict, api_url: str) -> None:
    if stac_object['type'] in ('Catalog', 'Collection'):
        endpoint = '/collections'
    else:
        assert stac_object['type'] == 'Feature'
        endpoint = f'/collections/{stac_object["collection"]}/items'

    url = urljoin(api_url, endpoint)
    response = requests.post(url, json=stac_object)

    if response.status_code == 409:
        print('Skipping existing object')
    else:
        response.raise_for_status()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('root_object_path', help='Filesystem path to the root STAC object.')
    parser.add_argument('api_url', help='URL for the STAC API.')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    traverse(Path(args.root_object_path), args.api_url)


if __name__ == '__main__':
    main()
