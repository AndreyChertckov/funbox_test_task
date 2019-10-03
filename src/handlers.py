import time
from aiohttp.web import Request, Response, json_response
from utils import get_domains
import functools


async def post_visited_links(request: Request) -> Response:
    data = await request.json()
    if not 'links' in data or not data['links']:
        return json_response({'status': {'error': 'Field links is required.'}}, status=400)
    current_time = int(time.time())
    domains = list(set(get_domains(data['links'])))
    transaction = request.app['redis'].multi_exec()
    transaction.lpush(current_time, *domains)
    transaction.zadd('times', current_time, current_time)
    await transaction.execute()
    return json_response({'status': 'ok'})


async def get_visited_domains(request: Request) -> Response:
    query = request.query
    from_ = float(query.get('from', '-inf'))
    to_ = float(query.get('to', 'inf'))
    keys = await request.app['redis'].zrangebyscore('times', min=from_, max=to_)
     
    if not keys:
        return json_response({'status': {'error': 'Not found.'}}, status=404)
    domains = set()
    for key in keys:
        domains_raw = await request.app['redis'].lrange(key, 0, -1)
        temp_domains = list(map(functools.partial(bytes.decode, encoding='UTF-8'), domains_raw))
        domains.update(temp_domains)
    return json_response({'domains': list(domains), 'status': 'ok'})
