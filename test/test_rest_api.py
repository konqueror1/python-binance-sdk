import pytest
import asyncio
import re
import os

from aioresponses import aioresponses, CallbackResult

from binance import Client, KlineInterval
from binance.common.utils import json_stringify

mock = False
api_key = os.environ.get('BNC_API_KEY', 'api_key')
MAX_PRINT = 150

CASES = [
    dict(
        name='ping'
    ),
    dict(
        # name of the spot method
        name='get_server_time',
        # arguments, defaults to ()
        # a=tuple(),
        # keyworded arguments, defaults to {}
        # ka={},
        #########################################
        # uri to be requested
        uri='https://api.binance.com/api/v3/time',
        # request method, defaults to 'get'
        # method='get'
    ),
    dict(
        name='get_exchange_info',
        # uri='https://www'
    ),
    # dict(
    #     name='get_symbol_info',
    #     a=('BTCUSDT',)
    # ),
    dict(
        name='get_orderbook',
        ka=dict(
            symbol='BTCUSDT',
            limit=100
        )
    ),
    dict(
        name='get_recent_trades',
        ka=dict(
            symbol='BTCUSDT',
            limit=100
        )
    ),
    # dict(
    #     name='get_historical_trades',
    #     ka=dict(
    #         symbol='BTCUSDT'
    #     )
    # ),
    dict(
        name='get_aggregate_trades',
        ka=dict(
            symbol='BTCUSDT'
        )
    ),
    dict(
        name='get_klines',
        ka=dict(
            symbol='BTCUSDT',
            interval=KlineInterval.KLINE_DAY
        )
    ),
]

def callback(method, url, **kwargs):
    def real_callback(url, **kwargs):
        print(url, kwargs)
        return CallbackResult(status=200)
    return real_callback

def print_str(name, d):
    s = json_stringify(d)

    length = len(s)
    if length > MAX_PRINT:
        print(name, s[:MAX_PRINT], 'and %s more' % (length - MAX_PRINT))
    else:
        print(name, s)

@pytest.mark.asyncio
async def test_apis():
    client = Client(api_key)

    print('')

    async def go():
        for case in CASES:
            name = case['name']
            args = case.get('a', tuple())
            kwargs = case.get('ka', {})

            ret = await getattr(client, name)(*args, **kwargs)

            if not mock:
                print_str(name + ':', ret)

    if not mock:
        await go()
        return

    with aioresponses() as m:
        pattern = re.compile(r'^https://(?:api|www).binance.com')

        if mock:
            m.get(pattern, callback=callback('get'), repeat=True)

        await go()





