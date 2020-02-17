import pytest
import requests_mock

from binance import Client, InvalidResponseException

client = Client('api_key', 'api_secret')

async def test_invalid_json():
    """Test Invalid response Exception"""

    with pytest.raises(InvalidResponseException):
        with requests_mock.mock() as m:
            m.get('https://www.binance.com/exchange/public/product', text='<head></html>')
            await client.get_products()


# def test_api_exception():
#     """Test API response Exception"""

#     with pytest.raises(BinanceAPIException):
#         with requests_mock.mock() as m:
#             json_obj = {"code": 1002, "msg": "Invalid API call"}
#             m.get('https://api.binance.com/api/v1/time', json=json_obj, status_code=400)
#             client.get_server_time()


# def test_api_exception_invalid_json():
#     """Test API response Exception"""

#     with pytest.raises(BinanceAPIException):
#         with requests_mock.mock() as m:
#             not_json_str = "<html><body>Error</body></html>"
#             m.get('https://api.binance.com/api/v1/time', text=not_json_str, status_code=400)
#             client.get_server_time()


# def test_withdraw_api_exception():
#     """Test Withdraw API response Exception"""

#     with pytest.raises(BinanceWithdrawException):

#         with requests_mock.mock() as m:
#             json_obj = {"success": False, "msg": "Insufficient funds"}
#             m.register_uri('POST', requests_mock.ANY, json=json_obj, status_code=200)
#             client.withdraw(asset='BTC', address='BTCADDRESS', amount=100)
