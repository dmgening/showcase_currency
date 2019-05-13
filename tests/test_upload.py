import pytest
import factory


class UploadRequestFactory(factory.Factory):
    class Meta:
        model = dict
        rename = {'from_': 'from'}

    from_ = factory.Faker('currency_code') 
    to = factory.Faker('currency_code') 
    rate = factory.Faker('pyfloat', positive=True)


@pytest.fixture()
def payload(request):
    return UploadRequestFactory()

async def assert_error(response, message, data=None, status=400):
    assert response.status == status
    payload = await response.json()
    assert list(payload.keys()) == ['error']
    assert payload['error']['message'] == message
    if data is not None:
        assert payload['error']['data'] == data
    else:
        assert 'data' not in payload['error']


async def test_upload(client, payload):
    response = await client.post('/upload', json=[payload, ])
    assert response.status == 200
    assert await response.json() == {'result': 'OK'}


async def test_malformed_json(client):
    response = await client.post('/upload', data='malformed')
    await assert_error(response, 'Malformed request body')


async def test_payload_validation(client, payload):
    payload['from'] = 123
    response = await client.post('/upload', json=[payload, ])
    await assert_error(response, 'Request validation error', 
                       {'0': {'from': ['Not a valid string.']}})
