import aioredis
from aiohttp import web

from .convert import convert_view
from .upload import upload_view


async def init_redis_pool(app):
    app['redis'] = await aioredis.create_redis_pool(
        'redis://localhost', minsize=5, maxsize=10, loop=app.loop)


async def app_factory():
    app = web.Application() # FIXME: Depricated, find a way to ensure same loop
    app.add_routes([web.get('/convert', convert_view),
                    web.post('/upload', upload_view)])
    app.on_startup.append(init_redis_pool)
    return app