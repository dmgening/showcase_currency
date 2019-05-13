from aiohttp import web

from .app import app_factory

web.run_app(app_factory())