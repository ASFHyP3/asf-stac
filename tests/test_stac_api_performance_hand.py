import requests


SEARCH_URL = 'https://stac.asf.alaska.edu/search'

HAND_COLLECTION = 'glo-30-hand'
ITEMS_URL = f'https://stac.asf.alaska.edu/collections/{HAND_COLLECTION}/items'


def test_search():
    params = {
        'query': {
            'collection': {
                'eq': HAND_COLLECTION,
            },
        },
        'limit': 100,
    }
    response = requests.post(SEARCH_URL, json=params)
    response.raise_for_status()
    items = response.json()['features']
    assert len(items) == 100
    assert response.elapsed.total_seconds() <= 5


def test_search_by_bbox():
    params = {
        'query': {
            'collection': {
                'eq': HAND_COLLECTION,
            },
        },
        'bbox': [8, 8, 10, 10],
        'limit': 100,
    }
    response = requests.post(SEARCH_URL, json=params)
    response.raise_for_status()
    items = response.json()['features']
    assert len(items) == 9
    assert response.elapsed.total_seconds() <= 5


def test_search_by_intersects():
    params = {
        'query': {
            'collection': {
                'eq': HAND_COLLECTION,
            },
        },
        'intersects': {
            'type': 'Point',
            'coordinates': [9.5, 9.5],
        },
        'limit': 100,
    }
    response = requests.post(SEARCH_URL, json=params)
    response.raise_for_status()
    items = response.json()['features']
    assert len(items) == 1
    assert response.elapsed.total_seconds() <= 5


def test_search_by_item_id():
    params = {
        'query': {
            'collection': {
                'eq': HAND_COLLECTION,
            },
        },
        'ids': ['Copernicus_DSM_COG_10_N00_00_E014_00_HAND', ],
    }
    response = requests.post(SEARCH_URL, json=params)
    response.raise_for_status()
    items = response.json()['features']
    assert len(items) == 1
    assert items[0]['id'] == 'Copernicus_DSM_COG_10_N00_00_E014_00_HAND'
    assert response.elapsed.total_seconds() <= 5


def test_get_item_id():
    response = requests.get(f'{ITEMS_URL}/Copernicus_DSM_COG_10_N00_00_E017_00_HAND')
    response.raise_for_status()
    item = response.json()
    assert item['id'] == 'Copernicus_DSM_COG_10_N00_00_E017_00_HAND'
    assert response.elapsed.total_seconds() <= 5
