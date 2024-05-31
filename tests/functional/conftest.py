import json
from json import JSONDecodeError

import pytest
import aiohttp

from tests.functional.settings import settings

pytest_plugins = (
    "tests.functional.fixtures.connections",
    "tests.functional.fixtures.db_operations",
    "tests.functional.fixtures.token_operations",
)


@pytest.fixture
def make_get_request(session: aiohttp.ClientSession):
    async def inner(path: str, query_data: dict = None, cookies: dict = None):
        url = "http://" + settings.get_api_host + "/auth/v1" + path
        if cookies:
            session.cookie_jar.update_cookies(cookies)
        async with session.get(url, params=query_data) as response:
            body = await response.read()
        try:
            body = json.loads(body)
        except JSONDecodeError:
            pass
        status = response.status
        cookies = response.cookies
        session.cookie_jar.clear()
        return body, status, cookies

    return inner


@pytest.fixture
def make_post_request(session: aiohttp.ClientSession):
    async def inner(path: str, query_data: dict = None, body: dict = None, cookies: dict = None):
        url = "http://" + settings.get_api_host + "/auth/v1" + path
        if cookies:
            session.cookie_jar.update_cookies(cookies)
        async with session.post(url, params=query_data, json=body) as response:
            body = await response.read()
        try:
            body = json.loads(body)
        except JSONDecodeError:
            pass
        status = response.status
        cookies = response.cookies
        session.cookie_jar.clear()
        return body, status, cookies

    return inner


@pytest.fixture
def make_patch_request(session: aiohttp.ClientSession):
    async def inner(path: str, query_data: dict = None, body: dict = None, cookies: dict = None):
        url = "http://" + settings.get_api_host + "/auth/v1" + path
        if cookies:
            session.cookie_jar.update_cookies(cookies)
        async with session.patch(url, json=body) as response:
            body = await response.read()
        try:
            body = json.loads(body)
        except JSONDecodeError:
            pass
        status = response.status
        cookies = response.cookies
        session.cookie_jar.clear()
        return body, status, cookies

    return inner


@pytest.fixture
def make_put_request(session: aiohttp.ClientSession):
    async def inner(path: str, query_data: dict = None, body: dict = None, cookies: dict = None):
        url = "http://" + settings.get_api_host + "/auth/v1" + path
        if cookies:
            session.cookie_jar.update_cookies(cookies)
        async with session.put(url, params=query_data, json=body) as response:
            body = await response.read()
        try:
            body = json.loads(body)
        except JSONDecodeError:
            pass
        status = response.status
        cookies = response.cookies
        session.cookie_jar.clear()
        return body, status, cookies

    return inner


@pytest.fixture
def make_delete_request(session: aiohttp.ClientSession):
    async def inner(path: str, query_data: dict = None, body: dict = None, cookies: dict = None):
        url = "http://" + settings.get_api_host + "/auth/v1" + path
        if cookies:
            session.cookie_jar.update_cookies(cookies)
        async with session.delete(url, params=query_data) as response:
            body = await response.read()
        try:
            body = json.loads(body)
        except JSONDecodeError:
            pass
        status = response.status
        cookies = response.cookies
        session.cookie_jar.clear()
        return body, status, cookies

    return inner
