import pytest
import asyncio

import pandas

from binance import Client, TickerHandlerBase, HandlerExceptionHandler, \
    InvalidHandlerException, SubType

@pytest.fixture
def client():
    return Client('api_key').start()

@pytest.mark.asyncio
async def test_ticker_handler(client):
    class TickerPrinter(TickerHandlerBase):
        DATA = None
        DF = None

        def receive(self, res):
            TickerPrinter.DATA = res
            TickerPrinter.DF = super().receive(res)

    client.handler(TickerPrinter(), HandlerExceptionHandler())

    data = dict(
        e='24hrTicker',
        foo='bar'
    )
    res = dict(
        data=data
    )

    await client._receive(res)

    assert TickerPrinter.DATA == data
    assert isinstance(TickerPrinter.DF, pandas.DataFrame)

def test_invalid_handler():
    with pytest.raises(InvalidHandlerException):
        client = Client('api_key')
        client.handler(1)

@pytest.mark.asyncio
async def test_client_handler(client):
    f = asyncio.Future()

    class TickerHandler(TickerHandlerBase):
        def receive(self, res):
            f.set_result(res)

    client.handler(TickerHandler())
    await client.subscribe(SubType.TICKER, 'BTCUSDT')

    payload = await f

    assert payload['e'] == '24hrTicker'
    assert payload['s'] == 'BTCUSDT'

    await client.close()
