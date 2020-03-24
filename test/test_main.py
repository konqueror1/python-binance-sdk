from binance import Client


def test_init_client():
    """create a client with key and secret"""
    Client('key', 'secret')


def test_init_client_key():
    """create a client only with key"""
    Client('key')


def test_no_api_key():
    """create a client with no args"""
    Client()
