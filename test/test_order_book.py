import pytest
from aioresponses import aioresponses

from binance import Client, OrderBook

@pytest.mark.asyncio
async def test_order_book():
    with aioresponses() as m:
        json_obj = {
            'lastUpdateId': 10,
            'asks': [
                [100, 10]
            ],
            'bids': [
                [99, 100],
                [98, 2]
            ]
        }
        m.get('https://api.binance.com/api/v3/depth?limit=100&symbol=btcusdt', payload=json_obj, status=200)

        client = Client('api_key')

        orderbook = OrderBook('BTCUSDT', client=client)

        await orderbook.updated()

        assert orderbook.asks == [[100, 10]]
        assert orderbook.bids == [[98, 2], [99, 100]]
