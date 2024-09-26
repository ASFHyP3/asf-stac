import requests


SEARCH_URL = 'https://stac.asf.alaska.edu/search'


def test_search():
    params = {
        'query': {
            'collection': {
                'eq': 'sentinel-1-global-coherence',
            },
        },
        'limit': 100,
    }
    response = requests.post(SEARCH_URL, json=params)
    response.raise_for_status()
    items = response.json()['features']
    assert len(items) == 100
    for item in items:
        assert item['collection'] == 'sentinel-1-global-coherence'
    assert response.elapsed.total_seconds() <= 5


def test_search_by_bbox():
    params = {
        'query': {
            'collection': {
                'eq': 'sentinel-1-global-coherence',
            },
        },
        'bbox': [8, 8, 10, 10],
        'limit': 100,
    }
    response = requests.post(SEARCH_URL, json=params)
    response.raise_for_status()
    items = response.json()['features']
    assert len(items) == 100
    assert response.elapsed.total_seconds() <= 5


def test_search_by_intersects():
    params = {
        'query': {
            'collection': {
                'eq': 'sentinel-1-global-coherence',
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
    assert len(items) == 40
    assert response.elapsed.total_seconds() <= 5


def test_search_by_season():
    params = {
        'query': {
            'collection': {
                'eq': 'sentinel-1-global-coherence',
            },
            'season': {
                'eq': 'summer',
            },
        },
        'limit': 100,
    }
    response = requests.post(SEARCH_URL, json=params)
    response.raise_for_status()
    items = response.json()['features']
    assert len(items) == 100
    for item in items:
        assert item['properties']['season'] == 'summer'
    assert response.elapsed.total_seconds() <= 5


def test_search_by_tile():
    params = {
        'query': {
            'collection': {
                'eq': 'sentinel-1-global-coherence',
            },
            'tile': {
                'eq': 'N10E010',
            },
        },
        'limit': 100,
    }
    response = requests.post(SEARCH_URL, json=params)
    response.raise_for_status()
    items = response.json()['features']
    assert len(items) == 40
    for item in items:
        assert item['properties']['tile'] == 'N10E010'
    assert response.elapsed.total_seconds() <= 5


def test_search_by_product_type():
    params = {
        'query': {
            'collection': {
                'eq': 'sentinel-1-global-coherence',
            },
            'sar:product_type': {
                'eq': 'COH12',
            },
        },
        'limit': 100,
    }
    response = requests.post(SEARCH_URL, json=params)
    response.raise_for_status()
    items = response.json()['features']
    assert len(items) == 100
    for item in items:
        assert item['properties']['sar:product_type'] == 'COH12'
    assert response.elapsed.total_seconds() <= 5


def test_search_by_polarization():
    params = {
        'query': {
            'collection': {
                'eq': 'sentinel-1-global-coherence',
            },
            'sar:polarizations': {
                'eq': ['VH'],
            },
        },
        'limit': 100,
    }
    response = requests.post(SEARCH_URL, json=params)
    response.raise_for_status()
    items = response.json()['features']
    assert len(items) == 100
    for item in items:
        assert item['properties']['sar:polarizations'] == ['VH']
    assert response.elapsed.total_seconds() <= 5
