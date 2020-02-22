from binance.common.constants import (
    REST_API_VERSION,
    SecurityType,
    RequestMethod
)

# Ref:
# https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md
APIS = [

    # General Endpoints

    dict(
        name   = 'ping',
        path   = 'ping',

        # Support params, defaults to `True`
        params = False,

        # request method, defaults to 'get'
        # method = RequestMethod.GET

        # SecurityType, defaults to NONE (False, False)
        # ref: https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#endpoint-security-type
        # security_type=SecurityType.NONE

        # api version
        # version=REST_API_VERSION
    ),

    dict(
        name   = 'get_server_time',
        path   = 'time',
        params = False
    ),

    dict(
        name   = 'get_exchange_info',
        path   = 'exchangeInfo',
        params = False
    ),

    # Market Data endpoints

    dict(
        name = 'get_orderbook',
        path = 'depth'
    ),

    dict(
        name = 'get_recent_trades',
        path = 'trades'
    ),

    dict(
        name = 'get_historical_trades',
        path = 'historicalTrades',
        security_type = SecurityType.MARKET_DATA
    ),

    dict(
        name = 'get_aggregate_trades',
        path = 'aggTrades'
    ),

    dict(
        name = 'get_klines',
        path = 'klines'
    ),

    dict(
        name = 'get_average_price',
        path = 'avgPrice'
    ),

    dict(
        name = 'get_ticker',
        path = 'ticker/24hr'
    ),

    dict(
        name = 'get_ticker_price',
        path = 'ticker/price'
    ),

    dict(
        name = 'get_orderbook_ticker',
        path = 'ticker/bookTicker'
    ),

    dict(
        name = 'create_order',
        path = 'order',
        method = RequestMethod.POST,
        security_type = SecurityType.TRADE
    ),

    dict(
        name = 'create_test_order',
        path = 'order/test',
        method = RequestMethod.POST,
        security_type = SecurityType.TRADE
    ),

    dict(
        name = 'get_order',
        path = 'order',
        security_type = SecurityType.USER_DATA
    ),

    dict(
        name = 'cancel_order',
        path = 'order',
        method = RequestMethod.DELETE,
        security_type = SecurityType.TRADE
    ),

    dict(
        name = 'get_open_orders',
        path = 'openOrders',
        security_type = SecurityType.USER_DATA
    ),

    dict(
        name = 'get_all_orders',
        path = 'allOrders',
        security_type = SecurityType.USER_DATA
    ),

    # Create a one-cancels-the-other order
    dict(
        name = 'create_oco',
        path = 'order/oco',
        method = RequestMethod.POST,
        security_type = SecurityType.TRADE
    ),

    dict(
        name = 'cancel_oco',
        path = 'orderList',
        method = RequestMethod.DELETE,
        security_type = SecurityType.NONE
    ),

    dict(
        name = 'get_oco',
        path = 'orderList',
        security_type = SecurityType.USER_DATA
    ),

    dict(
        name = 'get_all_oco',
        path = 'allOrderList',
        security_type = SecurityType.USER_DATA
    ),

    dict(
        name = 'get_open_oco',
        path = 'openOrderList',
        security_type = SecurityType.USER_DATA
    ),

    dict(
        name = 'get_account',
        path = 'account',
        security_type = SecurityType.USER_DATA
    ),

    dict(
        name = 'get_my_trade',
        path = 'myTrades',
        security_type = SecurityType.USER_DATA
    )
]

def define_getter(
    Target,
    name,
    path,
    params=True,
    version=REST_API_VERSION,
    method=RequestMethod.GET,
    security_type=SecurityType.NONE
):
    def getter(self, **kwargs):
        uri = self._rest_uri(path, version)
        ka = kwargs if params else {}

        return self._request(
            method,
            uri,
            security_type,
            **ka
        )

    setattr(Target, name, getter)

class RestAPIGetters:
    def _rest_uri(self, path, version):
        return self._api_host + '/api/' + version + '/' + path

    # User data stream endpoints

    async def get_listen_key(self):
        """Starts a new user data stream and returns the listen key. The stream will close after 60 minutes unless a keepalive is sent.

        Returns:
          The listen key
        """
        res = await self.post(
            self._rest_uri('userDataStream', REST_API_VERSION),
            security_type = SecurityType.USER_STREAM
        )
        return res['listenKey']

    def keepalive_listen_key(self, listen_key: str):
        """Keepalives a user data stream to prevent a time out. User data streams will close after 60 minutes. It's recommended to send a ping about every 30 minutes.

        Args：
          listen_key: user stream listen key
        """
        return self.put(
            self._rest_uri('userDataStream', REST_API_VERSION),
            security_type = SecurityType.USER_STREAM,
            listenKey = listen_key
        )

    def close_listen_key(self, listen_key: str):
        """Close out a user data stream.

        Args:
            listen_key: user stream listen key
        """
        return self.delete(
            self._rest_uri('userDataStream', REST_API_VERSION),
            security_type = SecurityType.USER_STREAM,
            listenKey = listen_key
        )

for getter_setting in APIS:
    define_getter(RestAPIGetters, **getter_setting)
