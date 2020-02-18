import pytest
from aioresponses import aioresponses

from binance import Client, OrderBook

def test_order_book_no_client():
    orderbook = OrderBook('BTCUSDT')
    assert not orderbook._fetching

@pytest.mark.asyncio
async def test_order_book():
    with aioresponses() as m:
        a00, b00, b01, a10 = [100, 10], [99, 100], [98, 2], [101, 3]
        asks=[a00]
        bids=[b00, b01]
        bids_sort = [b01, b00]

        m.get('https://api.binance.com/api/v3/depth?limit=100&symbol=BTCUSDT', payload=dict(
            lastUpdateId=10,
            asks=asks,
            bids=bids
        ), status=200)

        client = Client('api_key')

        # initialization
        #################################################################
        print('round one')

        orderbook = OrderBook('BTCUSDT', client=client)

        assert not orderbook.ready
        await orderbook.updated()
        assert orderbook.ready

        assert orderbook.asks == asks
        assert orderbook.bids == bids_sort

        asks1 = [a10, a00]
        asks1_sort = [a00, a10]

        m.get('https://api.binance.com/api/v3/depth?limit=100&symbol=BTCUSDT', payload=dict(
            lastUpdateId=13,
            asks=asks1,
            bids=bids
        ), status=200)

        f = orderbook.updated()

        print('round two')

        # wrong stream message,
        # and orderbook will fetch the snapshot again
        updated = orderbook.update(dict(
            # U=11 is missing
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

        # valid stream message
        assert orderbook.update(dict(
            U=14,
            u=15,
            a=[[95, 1]],
            b=[]
        ))

        assert orderbook.asks == [[95, 1], *asks1_sort]

        print('round three')

        # m.get('https://api.binance.com/api/v3/depth?limit=100&symbol=btcusdt', payload=dict(
        #     lastUpdateId=13,
        #     asks=asks1,
        #     bids=bids
        # ), status=200)

        # f = orderbook.updated()

        # updated = orderbook.update(dict(
        #     # U=16 is missing
        #     U=17,
        #     u=18,
        #     a=[],
        #     b=[]
        # ))

        # assert not updated

        # # orderbook is fetching
        # updated = orderbook.update(dict(
        #     U=14,
        #     u=15,
        #     a=[[95, 1]],
        #     b=[]
        # ))

        # assert not updated

        # await f

        # assert orderbook.asks == [[95, 1], *asks1_sort]
