import pytest
import factory

from showcase_currency.store import CurrencyUploader


class RateFactory(factory.Factory):
    class Meta:
        model = dict
        rename = {'from_': 'from'}

    from_ = factory.Faker('currency_code') 
    to = factory.Faker('currency_code') 
    rate = factory.Faker('pyfloat', positive=True)


class ConvertRequestFactory(factory.Factory):
    class Meta:
        model = dict
        rename = {'from_': 'from'}

    from_ = factory.Faker('currency_code') 
    to = factory.Faker('currency_code') 
    amount = factory.Faker('pyint')


@pytest.fixture()
async def rate(application):
    rates = RateFactory()
    uploader = CurrencyUploader(application['redis'])
    uploader.save(rates['from'], rates['to'], rates['rate'])
    await uploader.execute()
    return rates


@pytest.fixture()
def params(rate):
    return ConvertRequestFactory(from_=rate['from'], to=rate['to'])


async def test_convert(client, params, rate):
    response = await client.get('/convert', params=params)
    assert response.status == 200
    expected = rate['rate'] * params['amount']
    assert (await response.json())['result'] == expected