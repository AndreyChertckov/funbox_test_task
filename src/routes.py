from aiohttp import web
from handlers import post_visited_links, get_visited_domains


routes_list = [
    web.post('/visited_links', post_visited_links),
    web.get('/visited_domains', get_visited_domains)
]
