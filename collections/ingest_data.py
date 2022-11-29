"""
Adds STAC catalogs, collections, and items to a STAC API application. Skips objects that
already exist.

Assumes that the STAC objects to be ingested are individual json files on the local file system.

Assumes that the STAC API supports the Transaction extension.
"""

import argparse
import json
from urllib.parse import urljoin

import requests


class ServerSession(requests.Session):
    def __init__(self, prefix_url: str):
        super(ServerSession, self).__init__()
        self.prefix_url = prefix_url

    def request(self, method, url, *args, **kwargs):
        url = urljoin(self.prefix_url, url)
        return super(ServerSession, self).request(method, url, *args, **kwargs)


def get_endpoint(stac_object: dict) -> str:
    if stac_object['type'] in ('Catalog', 'Collection'):
        endpoint = '/collections'
    else:
        assert stac_object['type'] == 'Feature'
        endpoint = f'/collections/{stac_object["collection"]}/items'
    return endpoint


def add_stac_object(stac_object: dict, session: ServerSession) -> None:
    print(stac_object['id'])
    endpoint = get_endpoint(stac_object)
    response = session.post(endpoint, json=stac_object)

    if response.status_code == 409:
        print('Skipping existing object')
    else:
        response.raise_for_status()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('api_url', help='URL for the STAC API.')
    parser.add_argument('json_files', nargs='+', help='JSON files to ingest')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    session = ServerSession(args.api_url)
    for json_file in args.json_files:
        with open(json_file) as f:
            stac_object = json.load(f)
        add_stac_object(stac_object, session)


if __name__ == '__main__':
    main()
