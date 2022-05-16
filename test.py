from contextvars import ContextVar
import uuid

import pytest
import requests

BASE_URL = 'http://localhost:8080'
cache_key = ContextVar('cache_key')


@pytest.fixture(autouse=True)
def nginx_cache_clean():
    value = str(uuid.uuid4())
    token = cache_key.set(value)
    yield
    cache_key.reset(token)


def _get(path, params=None, *, cookies=None):
    headers = {
        'X-Cache-Key': cache_key.get(),
    }
    return requests.get(
        f'{BASE_URL}{path}', params=params, cookies=cookies, headers=headers)


def assert_miss(response):
    assert response.headers['X-Cache-Status'] in {'MISS', 'EXPIRED'}


def assert_hit(response):
    assert response.headers['X-Cache-Status'] == 'HIT'


def test_nginx_no_cache_header():
    path = '/response-headers'
    response = _get(path)
    response = _get(path)
    assert 'Cache-Control' not in response.headers
    assert_miss(response)


def test_nginx_respects_cache_control_max_age():
    path = '/response-headers'
    params = {
        'Cache-Control': 'max-age=10',
    }

    response = _get(path, params)
    assert_miss(response)

    response = _get(path, params)
    assert_hit(response)


def test_nginx_respects_cache_control_s_maxage():
    path = '/response-headers'
    params = {
        'Cache-Control': 's-maxage=10',
    }

    response = _get(path, params)
    assert_miss(response)

    response = _get(path, params)
    assert_hit(response)


def test_nginx_respects_cache_control_prefer_s_maxage():
    path = '/response-headers'
    params = {
        'Cache-Control': 'max-age=0 s-maxage=10',
    }

    response = _get(path, params)
    assert_miss(response)

    response = _get(path, params)
    assert_hit(response)


def test_nginx_respects_cache_control_prefer_s_maxage_zero():
    path = '/response-headers'
    params = {
        'Cache-Control': 'max-age=10 s-maxage=0',
    }

    response = _get(path, params)
    assert_miss(response)

    response = _get(path, params)
    assert_miss(response)


def test_nginx_proxy_cache_valid():
    path = '/proxy-cache-valid/status/200'

    response = _get(path)
    assert_miss(response)

    response = _get(path)
    assert_hit(response)


def test_nginx_proxy_cache_valid_ignored_when_max_age_is_defined():
    path = '/proxy-cache-valid/response-headers'
    params = {
        'Cache-Control': 'max-age=0',
    }

    response = _get(path, params)
    assert_miss(response)

    response = _get(path, params)
    assert_miss(response)


def test_nginx_proxy_cache_valid_ignored_when_s_maxage_is_defined():
    path = '/proxy-cache-valid/response-headers'
    params = {
        'Cache-Control': 's-maxage=0',
    }

    response = _get(path, params)
    assert_miss(response)

    response = _get(path, params)
    assert_miss(response)


def test_nginx_cache_with_cookies_in_request():
    path = '/response-headers'
    params = {
        'Cache-Control': 'max-age=10',
    }
    cookies = {
        'foo': 'bar',
    }

    response = _get(path, params, cookies=cookies)
    assert_miss(response)

    response = _get(path, params, cookies=cookies)
    assert_hit(response)


def test_nginx_never_cache_with_set_cookie_in_response():
    path = '/proxy-cache-valid/cookies/set'
    params = {
        'Cache-Control': 'max-age=10',
    }
    cookies = {
        'foo': 'bar',
    }

    response = _get(path, params, cookies=cookies)
    assert_miss(response)

    response = _get(path, params, cookies=cookies)
    assert_miss(response)
