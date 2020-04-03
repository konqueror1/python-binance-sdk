import pytest
import asyncio

from binance import (
    Client,
    TickerHandlerBase,
    ReuseHandlerException,

    AccountInfoHandlerBase,
    AccountPositionHandlerBase,
    BalanceUpdateHandlerBase,
    OrderUpdateHandlerBase,
    OrderListStatusHandlerBase
)


@pytest.fixture
def client():
    return Client('api_key').start()


def test_handler_reuse():
    client = Client('api_key')
    client2 = Client('api_key')

    handler = TickerHandlerBase()

    with pytest.raises(ReuseHandlerException, match='more than one'):
        client.handler(handler)
        client2.handler(handler)


async def run_user_handler(client, HandlerBase, payload):
    future = asyncio.Future()

    class Handler(HandlerBase):
        def receive(self, res):
            future.set_result(res)

    client.start()
    client.handler(Handler())
    await client._receive(payload)

    received = await future
    assert received == payload


@pytest.mark.asyncio
async def test_account_info(client):
    await run_user_handler(client, AccountInfoHandlerBase, {
        'e': 'outboundAccountInfo',
        'E': 1499405658849,
        'm': 0,
        't': 0,
        'b': 0,
        's': 0,
    })


@pytest.mark.asyncio
async def test_account_pos(client):
    await run_user_handler(client, AccountPositionHandlerBase, {
        'e': 'outboundAccountPosition',
        'E': 1564034571105,
        'u': 1564034571073,
        'B': [
            {
                'a': 'ETH',
                'f': '10000.000000',
                'l': '0.000000'
            }
        ]
    })


@pytest.mark.asyncio
async def test_balance_update(client):
    await run_user_handler(client, BalanceUpdateHandlerBase, {
        'e': 'balanceUpdate',
        'E': 1573200697110,
        'a': 'BTC',
        'd': '100.00000000',
        'T': 1573200697068
    })


@pytest.mark.asyncio
async def test_order_update(client):
    await run_user_handler(client, OrderUpdateHandlerBase, {
        'e': 'executionReport',
        'E': 1499405658658,
        's': 'ETHBTC',
        'c': 'mUvoqJxFIILMdfAW5iGSOW',
        'S': 'BUY',
        'o': 'LIMIT'
    })


@pytest.mark.asyncio
async def test_order_list_status(client):
    await run_user_handler(client, OrderListStatusHandlerBase, {
        'e': 'listStatus',
        'E': 1564035303637,
        's': 'ETHBTC',
        'g': 2,
        'c': 'OCO',
        'l': 'EXEC_STARTED',
        'L': 'EXECUTING'
    })
