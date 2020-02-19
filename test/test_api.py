import pytest
from aioresponses import aioresponses

from binance import Client, \
    InvalidResponseException, StatusException, APISecretNotDefinedException

@pytest.mark.asyncio
async def test_no_secret():
    client = Client('api_key')

    for method in ['get', 'post', 'delete', 'put']:
        with pytest.raises(APISecretNotDefinedException):
            await getattr(client, method)('/foo', True)

@pytest.mark.asyncio
async def test_invalid_json():
    """Test Invalid response Exception"""

    with pytest.raises(InvalidResponseException):
        with aioresponses() as m:
            m.get('https://www.binance.com/exchange/public/product', body='<head></html>')

            client = Client('api_key')
            await client.get_products()

@pytest.mark.asyncio
async def test_api_exception():
    """Test Status Exception"""
    with pytest.raises(StatusException):
        with aioresponses() as m:
            json_obj = {"code": 1002, "msg": "Invalid API call"}
            m.get('https://api.binance.com/api/v3/time', payload=json_obj, status=400)

            client = Client('api_key')
            await client.get_server_time()

@pytest.mark.asyncio
async def test_api_exception_invalid_json():
    """
    Test Status Exception, StatusException comes before InvalidResponseException
    """

    with pytest.raises(StatusException):
        with aioresponses() as m:
            not_json_str = "<html><body>Error</body></html>"
            m.get('https://api.binance.com/api/v3/time', body=not_json_str, status=400)

            client = Client('api_key')
            await client.get_server_time()
