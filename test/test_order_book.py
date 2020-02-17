import pytest
import requests_mock

from binance import Client, OrderBook

@pytest.fixture
def client():
    return Client('api_key')

@pytest.mark.asyncio
async def test_order_book(client):
    with requests_mock.mock() as m:
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
        m.get('https://api.binance.com/api/v3/depth', json=json_obj, status_code=200)

        orderbook = OrderBook('BTCUSDT', client=client)

        await orderbook.updated()

        assert orderbook.asks == [[100, 10]]
        assert orderbook.bids == [[98, 2], [99, 100]]
