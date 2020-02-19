from binance.getters import *
from binance.subscribe.manager import SubscriptionManager
from binance.common.constants import (
    API_HOST, WEBSITE_HOST, STREAM_HOST,
    DEFAULT_RETRY_POLICY, DEFAULT_STREAM_TIMEOUT
)

from .base import ClientBase

class Client(
    ClientBase,
    SpotGetters,
    SubscriptionManager
):
    def __init__(
        self,
        api_key,
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

        :param api_key: API Key
        :type api_key: str.
        :param api_secret: API Secret
        :type api_secret: str.
        :param requests_params: optional - Dictionary of requests params to use for all calls
        :type requests_params: dict.

        """

        self._api_key = api_key

        self._api_secret = None
        self.secret(api_secret)

        self._requests_params = requests_params
        self._api_host = api_host
        self._website_host = website_host
        self._stream_host = stream_host

        self._stream_kwargs = dict(
            retry_policy=stream_retry_policy,
            timeout=stream_timeout
        )

        self._receiving = False
        self._handler_ctx = None
        self._data_stream = None

    def secret(self, secret):
        if secret:
            self._api_secret = secret
        return self
