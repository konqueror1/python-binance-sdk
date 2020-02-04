from threading import Lock

from .client_base import ClientBase
from .client_getters import ClientGetters
from binance.subscribe.manager import SubscriptionManager
# from binance.subscribe.handler_context import HandlerContext

from binance.common.constants import \
    API_HOST, WEBSITE_HOST, STREAM_HOST

class Client(ClientBase, ClientGetters, SubscriptionManager):
    def __init__(
        self,
        api_key,
        api_secret,
        requests_params=None,
        # so that you can change api_host for CN network
        api_host=API_HOST,
        website_host=WEBSITE_HOST,
        stream_host=STREAM_HOST
    ):
        """Binance API Client constructor

        :param api_key: Api Key
        :type api_key: str.
        :param api_secret: Api Secret
        :type api_secret: str.
        :param requests_params: optional - Dictionary of requests params to use for all calls
        :type requests_params: dict.

        """

        self._api_key = api_key
        self._api_secret = api_secret
        self._requests_params = requests_params
        self._api_host = api_host
        self._website_host = website_host
        self._stream_host = stream_host

        self._hanging = False
        self._hang_lock = Lock()

        self._receiving = False

        # self._handler_ctx = HandlerContext()
