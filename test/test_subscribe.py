import pytest
import asyncio

import pandas

from binance import Client, TickerHandlerBase, \
    InvalidHandlerException, SubType, OrderBookHandlerBase, \
    InvalidSubTypeParamException, InvalidSubParamsException, \
    HandlerExceptionHandlerBase

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
        def receive(self, res):
            TickerPrinter.DATA = res
            TickerPrinter.DF = super().receive(res)

    client.handler(TickerPrinter())

    await client._receive(TICKER_RES)

    assert TickerPrinter.DATA == TICKER_RES['data']
    assert isinstance(TickerPrinter.DF, pandas.DataFrame)

@pytest.mark.asyncio
async def test_handler_exception_handler(client):
    exc = Exception()

    f = asyncio.Future()

    class TickerPrinter(TickerHandlerBase):
        def receive(self, res):
            raise exc

    class ExceptionHandler(HandlerExceptionHandlerBase):
        def receive(self, e):
            f.set_result(e)

    client.handler(TickerPrinter(), ExceptionHandler())

    await client._receive(TICKER_RES)

    assert await f == exc

def test_invalid_handler(client):
    with pytest.raises(InvalidHandlerException):
        client.handler(1)

@pytest.mark.asyncio
async def test_invalid_subtype_symbol(client):
    with pytest.raises(InvalidSubTypeParamException):
        await client.subscribe(SubType.TICKER)

    with pytest.raises(InvalidSubTypeParamException):
        await client.subscribe(SubType.TICKER, 1)

    with pytest.raises(InvalidSubParamsException):
        await client.subscribe(SubType.TICKER, 1, 2)

@pytest.mark.asyncio
async def test_client_handler(client):
    f = asyncio.Future()

    class TickerHandler(TickerHandlerBase):
        # async receiver
        async def receive(self, res):
            f.set_result(res)

    client.handler(TickerHandler())
    await client.subscribe(SubType.TICKER, 'BTCUSDT')

    payload = await f

    assert payload['e'] == '24hrTicker'
    assert payload['s'] == 'BTCUSDT'

    await client.close()

@pytest.mark.asyncio
async def test_orderbook_handler(client):
    class OrderBookHandler(OrderBookHandlerBase):
        pass

    handler = OrderBookHandler()

    client.handler(handler)
    await client.subscribe(SubType.ORDER_BOOK, 'BTCUSDT')

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

# TODO
# stop()
# subscribe overloading
# dev: user handler
# stream reconnect, exceptions, abandon
# all market ticker/mini ticker handlers
# orderbook staled payload, invalid item in pending queue
