from .utils import err_msg

class BinanceSocketAbandonedException(Exception):
    def __init__(self, url):
        self.url = url

    def __str__(self):
        return err_msg(
            'websocket "%s" is abandoned after too many retries', self.url)

class BinanceAPIKeyNotDefinedException(Exception):
    def __init__(self, url):
        self.url = url

    def __str__(self):
        return err_msg(
            'api_key is required for requesting "%s"', self.url)

class BinanceAPISecretNotDefinedException(Exception):
    def __init__(self, url):
        self.url = url

    def __str__(self):
        return err_msg(
            'api_secret is required for requesting "%s"', self.url)
