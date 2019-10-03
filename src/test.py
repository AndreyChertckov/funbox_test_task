import os
import time
import functools

import pytest
from aiohttp import web
from aioredis import create_redis_pool

from routes import routes_list


async def create_test_app() -> web.Application:
    app = web.Application()
    app.add_routes(routes_list)

    redis_host = os.environ.get('REDIS', '127.0.0.1')
    redis_pool = await create_redis_pool(f'redis://{redis_host}')
    await redis_pool.flushall()
    time = 1500000000
    transaction = redis_pool.multi_exec()
    transaction.lpush(time, 'ya.ru', 'funbox.ru', 'google.com')
    transaction.zadd('times', time, time)
    await transaction.execute()
    app['redis'] = redis_pool

    return app


@pytest.fixture
def cli(loop, aiohttp_client):
    app = loop.run_until_complete(create_test_app())
    return loop.run_until_complete(aiohttp_client(app))


async def test_post_visited_links_empty(cli):
    resp = await cli.post('/visited_links', json={'links': []})
    assert resp.status == 400
    resp_json = await resp.json()
    assert 'error' in resp_json['status']
    assert 'Field links is required.' == resp_json['status']['error']


async def test_post_visited_links(cli):
    current_time = int(time.time())
    resp = await cli.post('/visited_links', json={'links': ['https://ya.ru/index.html']})
    assert resp.status == 200
    resp_json = await resp.json()
    assert resp_json['status'] == 'ok'
    keys = await cli.app['redis'].zrangebyscore('times', min=current_time)
    assert keys
    domains = set()
    for key in keys:
        domains_raw = await cli.app['redis'].lrange(key, 0, -1)
        temp_domains = list(map(functools.partial(bytes.decode, encoding='UTF-8'), domains_raw))
        domains.update(temp_domains)
    assert len(domains) == 1
    


async def test_get_visited_domains_empty(cli):
    resp = await cli.get('/visited_domains')
    assert resp.status == 200
    resp_json = await resp.json()
    assert resp_json['status'] == 'ok'
    assert len(resp_json['domains']) == 3
    assert 'ya.ru' in resp_json['domains']
    assert 'funbox.ru' in resp_json['domains']
    assert 'google.com' in resp_json['domains']


async def test_get_visited_domains_to(cli):
    resp = await cli.get('/visited_domains?to=1500000001')
    assert resp.status == 200
    resp_json = await resp.json()
    assert resp_json['status'] == 'ok'
    assert len(resp_json['domains']) == 3
    assert 'ya.ru' in resp_json['domains']
    assert 'funbox.ru' in resp_json['domains']
    assert 'google.com' in resp_json['domains']


async def test_get_visited_domains_from(cli):
    resp = await cli.get('/visited_domains?from=1500000001&to=1500000002')
    assert resp.status == 404
    resp_json = await resp.json()
    assert 'error' in resp_json['status']
    assert 'Not found.' == resp_json['status']['error']
