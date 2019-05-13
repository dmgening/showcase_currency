import pytest

from showcase_currency.app import app_factory

@pytest.fixture()
async def application(loop):
    app = await app_factory()
    yield app
    await app['redis'].flushall()

@pytest.fixture()
def client(application, loop, aiohttp_client):
    return loop.run_until_complete(aiohttp_client(application))