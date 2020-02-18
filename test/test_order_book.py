import pytest
from aioresponses import aioresponses

from binance import Client, OrderBook

@pytest.mark.asyncio
async def test_order_book():
    with aioresponses() as m:
        a00, b00, b01, a10 = [100, 10], [99, 100], [98, 2], [101, 3]
        asks=[a00]
        bids=[b00, b01]
        bids_sort = [b01, b00]

        m.get('https://api.binance.com/api/v3/depth?limit=100&symbol=btcusdt', payload=dict(
            lastUpdateId=10,
            asks=asks,
            bids=bids
        ), status=200)

        client = Client('api_key')

        orderbook = OrderBook('BTCUSDT', client=client)

        assert not orderbook.ready
        await orderbook.updated()
        assert orderbook.ready

        assert orderbook.asks == asks
        assert orderbook.bids == bids_sort

        asks1 = [a10, a00]
        asks1_sort = [a00, a10]

        m.get('https://api.binance.com/api/v3/depth?limit=100&symbol=btcusdt', payload=dict(
            lastUpdateId=13,
            asks=asks1,
            bids=bids
        ), status=200)

        f = orderbook.updated()

        updated = orderbook.update(dict(
            U=12,
            u=13,
            a=[],
            b=[]
        ))

        assert not updated
        assert not orderbook.ready

        await f
        assert orderbook.ready

        assert orderbook.asks == asks1_sort
        assert orderbook.bids == bids_sort

        assert orderbook.update(dict(
            U=14,
            u=15,
            a=[[95, 1]],
            b=[]
        ))

        assert orderbook.asks == [[95, 1], *asks1_sort]
