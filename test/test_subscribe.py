import pytest
import asyncio

import pandas

from binance import (
    Client,
    SubType,
    KlineInterval,

    TickerHandlerBase,
    KlineHandlerBase,

    InvalidHandlerException,
    OrderBookHandlerBase,
    InvalidSubTypeParamException,
    InvalidSubParamsException,
    HandlerExceptionHandlerBase,
    UnsupportedSubTypeException
)


@pytest.fixture
def client():
    return Client('api_key').start()


TICKER_RES = dict(
    data=dict(
        e='24hrTicker',
        foo='bar'
    )
)


@pytest.mark.asyncio
async def test_ticker_handler(client):
    class TickerPrinter(TickerHandlerBase):
        DATA = None
        DF = None

        # sync receiver
        def receive(self, payload):
            TickerPrinter.DATA = payload
            TickerPrinter.DF = super().receive(payload)

    client.handler(TickerPrinter())

    await client._receive(TICKER_RES)

    assert TickerPrinter.DATA == TICKER_RES['data']
    assert isinstance(TickerPrinter.DF, pandas.DataFrame)
    await client.close()


@pytest.mark.asyncio
async def test_handler_exception_handler(client):
    exc = Exception()

    f = asyncio.Future()

    class TickerPrinter(TickerHandlerBase):
        def receive(self, payload):
            raise exc

    class ExceptionHandler(HandlerExceptionHandlerBase):
        def receive(self, e):
            f.set_result(e)

    client.handler(TickerPrinter(), ExceptionHandler())

    await client._receive(TICKER_RES)

    assert await f == exc
    await client.close()


def test_invalid_handler(client):
    with pytest.raises(InvalidHandlerException, match='invalid handler'):
        client.handler(1)


@pytest.mark.asyncio
async def test_invalid_subtype_symbol(client):
    with pytest.raises(InvalidSubTypeParamException, match='invalid param'):
        await client.subscribe(SubType.TICKER)

    with pytest.raises(InvalidSubTypeParamException, match='string expected'):
        await client.subscribe(SubType.TICKER, 1)

    with pytest.raises(InvalidSubTypeParamException, match='string expected'):
        await client.subscribe(SubType.TICKER, None)

    with pytest.raises(InvalidSubParamsException, match='invalid subscribe'):
        await client.subscribe(SubType.TICKER, 1, 2)

    with pytest.raises(UnsupportedSubTypeException, match='subtype "unknown"'):
        await client.subscribe('unknown')

    with pytest.raises(InvalidSubTypeParamException, match='symbol'):
        await client.subscribe(SubType.KLINE)

    with pytest.raises(InvalidSubTypeParamException, match='not specified'):
        await client.subscribe(SubType.KLINE, 'BTCUSDT')

    with pytest.raises(InvalidSubTypeParamException, match='KlineInterval'):
        await client.subscribe(SubType.KLINE, 'BTCUSDT', 1)


@pytest.mark.asyncio
async def test_client_handler(client):
    f = asyncio.Future()

    class TickerHandler(TickerHandlerBase):
        # async receiver
        async def receive(self, payload):
            f.set_result(payload)

    client.handler(TickerHandler())
    await client.subscribe(SubType.TICKER, 'BTCUSDT')

    payload = await f

    assert payload['e'] == '24hrTicker'
    assert payload['s'] == 'BTCUSDT'

    await client.close()


@pytest.mark.asyncio
async def test_client_kline_handler(client):
    f = asyncio.Future()

    class KlineHandler(KlineHandlerBase):
        # async receiver
        async def receive(self, payload):
            f.set_result(payload)

    client.handler(KlineHandler())
    await client.subscribe(SubType.KLINE, 'BTCUSDT', KlineInterval.DAY)

    payload = await f

    assert payload['e'] == 'kline'
    assert payload['s'] == 'BTCUSDT'

    await client.close()


async def run_orderbook_handler(client, init_orderbook_first):
    f = asyncio.Future()

    class OrderBookHandler(OrderBookHandlerBase):
        def receive(self, payload):
            f.set_result(super().receive(payload))

    handler = OrderBookHandler()

    if init_orderbook_first:
        orderbook = handler.orderbook('BTCUSDT')

    client.handler(handler)
    await client.subscribe(SubType.ORDER_BOOK, 'BTCUSDT')

    info, [bids, asks] = await f
    assert isinstance(info, pandas.DataFrame)
    assert isinstance(bids, pandas.DataFrame)
    assert isinstance(asks, pandas.DataFrame)

    if not init_orderbook_first:
        orderbook = handler.orderbook('BTCUSDT')

    async def assert_no_change():
        asks = [*orderbook.asks]
        await asyncio.sleep(0.2)

        # should have no change
        assert asks == orderbook.asks

    await orderbook.updated()

    assert len(orderbook.asks) != 0
    assert len(orderbook.bids) != 0

    assert await client.list_subscriptions() == ['btcusdt@depth']

    client.stop()
    await assert_no_change()

    client.start()

    await client.unsubscribe(SubType.ORDER_BOOK, 'BTCUSDT')

    await assert_no_change()

    await client.close()


@pytest.mark.asyncio
async def test_orderbook_handler_init_orderbook_ahead(client):
    await run_orderbook_handler(client, True)


@pytest.mark.asyncio
async def test_orderbook_handler_init_orderbook_after(client):
    await run_orderbook_handler(client, False)


# TODO
# stop()
# subscribe overloading
