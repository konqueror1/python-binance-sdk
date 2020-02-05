from .utils import err_msg

class BinanceSocketAbandonedException(Exception):
    def __init__(self, url):
        self.url = url

    def __str__(self):
        return err_msg(
            'websocket "%s" is abandoned after too many retries', self.url)
