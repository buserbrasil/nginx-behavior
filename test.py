import requests

BASE_URL = 'http://localhost:8080'


def _get(path, params=None):
    return requests.get(f'{BASE_URL}{path}', params=params)


def test_nginx_no_cache_header():
    path = '/response-headers'
    response = _get(path)
    response = _get(path)
    assert 'Cache-Control' not in response.headers
    assert response.headers['X-Cache-Status'] == 'MISS'


def test_nginx_respects_cache_control_max_age():
    path = '/response-headers'
    params = {
        'Cache-Control': 'max-age=10',
    }

    response = _get(path, params)
    assert response.headers['X-Cache-Status'] in {'MISS', 'EXPIRED'}

    response = _get(path, params)
    assert response.headers['X-Cache-Status'] == 'HIT'


def test_nginx_respects_cache_control_s_maxage():
    path = '/response-headers'
    params = {
        'Cache-Control': 's-maxage=10',
    }

    response = _get(path, params)
    assert response.headers['X-Cache-Status'] in {'MISS', 'EXPIRED'}

    response = _get(path, params)
    assert response.headers['X-Cache-Status'] == 'HIT'


def test_nginx_respects_cache_control_prefer_s_maxage():
    path = '/response-headers'
    params = {
        'Cache-Control': 'max-age=0 s-maxage=10',
    }

    response = _get(path, params)
    assert response.headers['X-Cache-Status'] in {'MISS', 'EXPIRED'}

    response = _get(path, params)
    assert response.headers['X-Cache-Status'] == 'HIT'


def test_nginx_respects_cache_control_prefer_s_maxage():
    path = '/response-headers'
    params = {
        'Cache-Control': 'max-age=10 s-maxage=0',
    }

    response = _get(path, params)
    assert response.headers['X-Cache-Status'] == 'MISS'

    response = _get(path, params)
    assert response.headers['X-Cache-Status'] == 'MISS'
