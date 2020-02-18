import pytest
import pandas

from binance import Client, TickerHandlerBase, HandlerExceptionHandler

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

