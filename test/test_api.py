import pytest
import requests_mock

from binance import Client, \
    InvalidResponseException, StatusException

client = Client('api_key', 'api_secret')

@pytest.mark.asyncio
async def test_invalid_json():
    """Test Invalid response Exception"""

    with pytest.raises(InvalidResponseException):
        with requests_mock.mock() as m:
            m.get('https://www.binance.com/exchange/public/product', text='<head></html>')
            await client.get_products()

@pytest.mark.asyncio
async def test_api_exception():
    """Test Status Exception"""
    with pytest.raises(StatusException):
        with requests_mock.mock() as m:
            json_obj = {"code": 1002, "msg": "Invalid API call"}
            m.get('https://api.binance.com/api/v1/time', json=json_obj, status_code=400)
            await client.get_server_time()

@pytest.mark.asyncio
async def test_api_exception_invalid_json():
    """
    Test Status Exception, StatusException comes before InvalidResponseException
    """

    with pytest.raises(StatusException):
        with requests_mock.mock() as m:
            not_json_str = "<html><body>Error</body></html>"
            m.get('https://api.binance.com/api/v1/time', text=not_json_str, status_code=400)
            await client.get_server_time()
