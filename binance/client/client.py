from threading import Lock

from .client_base import ClientBase
from .client_getters import ClientGetters
from binance.subscribe.manager import SubscriptionManager
from binance.subscribe.handler_context import HandlerContext

from binance.common.constants import \
    API_HOST, WEBSITE_HOST, STREAM_HOST, \
    DEFAULT_RETRY_POLICY, DEFAULT_STREAM_TIMEOUT

class Client(ClientBase, ClientGetters, SubscriptionManager):
    def __init__(
        self,
        api_key=None,
        api_secret=None,
        requests_params=None,
        # so that you can change api_host for CN network
        api_host=API_HOST,
        website_host=WEBSITE_HOST,
        stream_host=STREAM_HOST,
        stream_retry_policy=DEFAULT_RETRY_POLICY,
        stream_timeout=DEFAULT_STREAM_TIMEOUT
    ):
        """Binance API Client constructor

        :param api_key: Api Key
        :type api_key: str.
        :param api_secret: Api Secret
        :type api_secret: str.
        :param requests_params: optional - Dictionary of requests params to use for all calls
        :type requests_params: dict.

        """

        self._api_key = None
        self._api_secret = None
        self._requests_params = requests_params
        self._api_host = api_host
        self._website_host = website_host
        self._stream_host = stream_host
        self._stream_retry_policy = stream_retry_policy
        self._stream_timeout = stream_timeout

        # self._hanging = False
        # self._hang_lock = Lock()

        self._receiving = False

        self._handler_ctx = HandlerContext()

        self._data_stream = None

    def key(self, key):
        if key:
            self._api_key = key
        return self

    def secret(self, secret):
        if secret:
            self._api_secret = secret
        return self
