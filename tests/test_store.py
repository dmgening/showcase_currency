import factory
import pytest

from showcase_currency.store import CurrencyUploader, currency_convert, _rate_key


class ConversionFactory(factory.Factory):
    class Meta:
        model = dict

    source = factory.Faker('currency_code') 
    target = factory.Faker('currency_code') 
    rate = factory.Faker('pyfloat', positive=True)


@pytest.fixture
def redis(application):
    return application['redis']


@pytest.fixture
def conversion():
    return ConversionFactory.stub()


@pytest.fixture
async def saved_conversion(redis, conversion):
    await test_uploader(redis, conversion)
    return conversion


def test_rate_key_generator(conversion):
    key = _rate_key(conversion.source.lower(), conversion.target.lower())
    assert key == f'{conversion.source}:{conversion.target}'


async def test_uploader(redis, conversion):
    uploader = CurrencyUploader(redis)
    uploader.save(conversion.source, conversion.target, conversion.rate)
    await uploader.execute()

    rate = await redis.get(_rate_key(conversion.source, conversion.target))
    assert float(rate) == conversion.rate


async def test_uploader_replace(redis, conversion):
    await test_uploader(redis, conversion)

    uploader = CurrencyUploader(redis, replace=True)
    uploader.save(conversion.target, conversion.source, conversion.rate)
    await uploader.execute()

    assert await redis.get(_rate_key(conversion.source, conversion.target)) is None
    rate = await redis.get(_rate_key(conversion.target, conversion.source))
    assert float(rate) == conversion.rate


async def test_convert(redis, saved_conversion):
    converted = await currency_convert(redis, saved_conversion.source, 
                                       saved_conversion.target, 10)
    assert converted == saved_conversion.rate * 10


async def test_convert_reverse(redis, saved_conversion):
    converted = await currency_convert(redis, saved_conversion.target, 
                                       saved_conversion.source, 10)
    assert converted == (1 / saved_conversion.rate) * 10
