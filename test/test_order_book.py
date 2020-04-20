import pytest
import asyncio

from aioresponses import aioresponses

from binance import Client, OrderBook


def test_order_book_no_client():
    orderbook = OrderBook('BTCUSDT')
    assert not orderbook._fetching


@pytest.mark.asyncio
async def test_order_book():
    with aioresponses() as m:
        a00, b00, b01, a10 = [100, 10], [99, 100], [98, 2], [101, 3]
        asks = [a00]
        bids = [b00, b01]
        bids_sort = [b01, b00]

        asks1 = [a10, a00]
        asks1_sort = [a00, a10]

        client = Client('api_key')

        def preset_10():
            m.get('https://api.binance.com/api/v3/depth?limit=100&symbol=BTCUSDT', payload=dict(
                lastUpdateId=10,
                asks=asks,
                bids=bids
            ), status=200)

        def assert_state_a():
            assert orderbook.asks == asks
            assert orderbook.bids == bids_sort

        def preset_13():
            m.get(
                'https://api.binance.com/api/v3/depth?limit=100&symbol=BTCUSDT', payload=dict(
                    lastUpdateId=13,
                    asks=asks1,
                    bids=bids
                ),
                status=200
            )

        def assert_state_b():
            assert orderbook.asks == asks1_sort
            assert orderbook.bids == bids_sort

        def assert_state_c():
            assert orderbook.asks == [[95, 1], *asks1_sort]
            assert orderbook.bids == bids_sort

        print('\nround one  : normal initialization')

        preset_10()

        orderbook = OrderBook('BTCUSDT', client)

        assert not orderbook.ready
        await orderbook.updated()
        assert orderbook.ready

        assert_state_a()

        print('round two  : wrong update, refetch, retry policy and finally fetched')

        f = orderbook.updated()

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

        await asyncio.sleep(0.5)
        # delay initialize preset b
        preset_13()

        await f
        assert orderbook.ready

        assert_state_b()

        # valid stream message
        assert orderbook.update(dict(
            U=14,
            u=15,
            a=[[95, 1]],
            b=[]
        ))

        assert orderbook.asks == [[95, 1], *asks1_sort]

        print('round three: new update when still refetching')

        preset_13()

        f = orderbook.updated()

        updated = orderbook.update(dict(
            # U=16 is missing
            U=17,
            u=18,
            a=[],
            b=[]
        ))

        assert not updated

        # orderbook is fetching
        updated = orderbook.update(dict(
            U=14,
            u=15,
            a=[[95, 1]],
            b=[]
        ))

        assert not updated

        await f

        assert_state_c()

        print('round four : retry policy -> abandon')

        def no_retry_policy(fails):
            return True, 0

        orderbook.set_retry_policy(no_retry_policy)

        async def test_no_retry_policy():
            orderbook.update(dict(
                # U=16 is missing
                U=17,
                u=18,
                a=[],
                b=[]
            ))

            exc = None

            try:
                await orderbook.updated()
            except Exception as e:
                exc = e

            assert exc is not None

            preset_13()

            await orderbook.fetch()

            assert orderbook.ready

            orderbook.update(dict(
                U=14,
                u=15,
                a=[[95, 1]],
                b=[]
            ))

            assert_state_c()

        await test_no_retry_policy()

        print('round five : no retry policy')

        orderbook.set_retry_policy(None)

        await test_no_retry_policy()

        print('round six  : part of unsolved_queue is invalid')

        preset_10()
        # will fetch twice
        preset_10()

        def allow_retry_once(fails: int):
            if fails > 1:
                return True, 0

            return False, 0

        orderbook.set_retry_policy(allow_retry_once)

        # however, use private method, do not do this unless for testing

        orderbook._fetching = True

        asyncio.create_task(orderbook._fetch())

        f = orderbook.updated()

        # valid, but now is fetching
        orderbook.update(dict(
            U=11,
            u=12,
            a=[],
            b=[]
        ))

        # invalid, and it will also clean the previous one
        orderbook.update(dict(
            U=14,
            u=15,
            a=[[95, 1]],
            b=[]
        ))

        # orderbook will refetch

        orderbook.update(dict(
            U=11,
            u=12,
            a=[a10],
            b=[]
        ))

        await f

        assert_state_b()
