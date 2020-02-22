from binance import Client
import pytest

def test_init_client():
    """create a client with key and secret"""
    client = Client('key', 'secret')

def test_init_client_key():
    """create a client only with key"""
    client = Client('key')

def test_no_api_key():
    """create a client with no args"""
    client = Client()

