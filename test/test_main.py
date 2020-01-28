from binance import Client
import pytest

# TEST_SYMBOL = "BNBBTC"

# @pytest.fixture
# def fresh_cache():
#     return DepthCache(TEST_SYMBOL)


def test_client():
    """Verify basic functionality for adding a bid to the cache"""
    client = Client()
