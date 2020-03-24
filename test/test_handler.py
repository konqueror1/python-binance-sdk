import pytest

from binance import Client, TickerHandlerBase, ReuseHandlerException


def test_handler_reuse():
    client = Client('api_key')
    client2 = Client('api_key')

    handler = TickerHandlerBase()

    with pytest.raises(ReuseHandlerException, match='more than one'):
        client.handler(handler)
        client2.handler(handler)
