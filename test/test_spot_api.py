import pytest
import asyncio
import re

from aioresponses import aioresponses, CallbackResult

from binance import Client

CASES = [
    dict(
        name='get_server_time',
        uri='https://api.binance.com/api/v3/time',
        method='get'
    )
]

def callback(url, **kwargs):
    print(url, kwargs)
    return CallbackResult(status=200)

@pytest.mark.asyncio
async def test_apis():
    with aioresponses() as m:
        client = Client('api_key')

        pattern = re.compile(r'^https://api.binance.com')
        m.get(pattern, callback=callback, repeat=True)

        for case in CASES:
            name = case['name']
            args = case.get('a', tuple())
            kwargs = case.get('ka', {})

            await getattr(client, name)(*args, **kwargs)


