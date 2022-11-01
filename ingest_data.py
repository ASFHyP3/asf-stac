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
    # Assumes relative links.
    return [
        parent_path / link_object['href']
        for link_object in stac_object['links'] if link_object['rel'] in ('child', 'item')
    ]


def add_stac_object(stac_object: dict, api_url: str) -> None:
    if stac_object['type'] in ('Catalog', 'Collection'):  # TODO: is there a separate POST /catalogs endpoint?
        endpoint = '/collections'
    else:
        assert stac_object['type'] == 'Feature'
        endpoint = f'/collections/{stac_object["collection"]}/items'
    url = urljoin(api_url, endpoint)
    response = requests.post(url, json=stac_object)
    response.raise_for_status()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Add STAC catalog data to a STAC API application.')
    parser.add_argument('catalog_path')
    parser.add_argument('api_url')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    traverse(Path(args.catalog_path), args.api_url)


if __name__ == '__main__':
    main()
