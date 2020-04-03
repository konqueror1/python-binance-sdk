import pytest
from aioresponses import aioresponses

from binance import (
    Client,
    StatusException
)

# TODO:
# global request_params
# keyword argument request_params

URL = 'https://api.binance.com/api/v3/foo'
URL2 = URL + '/bar'


def redirect(m):
    m.get(
        URL,
        status=307,
        headers={
            'Location': URL2
        }
    )


@pytest.mark.asyncio
async def test_global_request_params():
    payload = {
        'foo': 'bar'
    }

    client = Client(
        request_params={
            'allow_redirects': True
        }
    )

    with aioresponses() as m:
        redirect(m)

        m.get(
            URL2,
            payload=payload,
            status=200
        )

        res = await client.get(URL)

        assert res == payload


@pytest.mark.asyncio
async def test_request_params():
    client = Client()

    with aioresponses() as m:
        redirect(m)

        with pytest.raises(
            StatusException,
            match='status 307'
        ):
            await client.get(
                URL,
                request_params={
                    'allow_redirects': False
                }
            )


@pytest.mark.asyncio
async def test_force_params():
    payload = {
        'foo': 'bar'
    }

    client = Client()

    with aioresponses() as m:
        m.post(
            URL + '?foo=bar',
            payload=payload,
            status=200
        )

        res = await client.post(
            URL,
            foo='bar',
            force_params=True
        )

        assert res == payload
