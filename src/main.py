import asyncio
import os

from aiohttp import web
from aioredis import create_redis_pool

from routes import routes_list


async def create_app() -> web.Application:
    app = web.Application()
    app.add_routes(routes_list)

    redis_host = os.environ.get('REDIS', '127.0.0.1')

    app['redis'] = await create_redis_pool(f'redis://{redis_host}')
    return app


def main() -> None:
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(create_app())
    web.run_app(app, host='0.0.0.0', port=8080)


if __name__ == "__main__":
    main()
