from binance import Client
# import pytest

# # TEST_SYMBOL = "BNBBTC"

# # @pytest.fixture
# # def fresh_cache():
# #     return DepthCache(TEST_SYMBOL)

def test_init_client():
    """create a client with key and secret"""
    client = Client('key', 'secret')

def test_init_client_key():
    """create a client only with key"""
    client = Client('key')
