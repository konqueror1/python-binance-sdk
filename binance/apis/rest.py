import asyncio
import time

from binance.common.utils import interval_to_milliseconds, convert_ts_str
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
        name = 'get_24hr_ticker_price_changes',
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

    async def get_symbol_info(self, symbol):
        res = await self.get_exchange_info()

        for item in res['symbols']:
            if item['symbol'] == symbol.upper():
                return item

        return None

    # User data stream endpoints

    async def get_listen_key(self):
        res = await self.post(
            self._rest_uri('userDataStream', REST_API_VERSION),
            security_type = SecurityType.USER_STREAM
        )
        return res['listenKey']

    async def keepalive_listen_key(self, listenKey):
        return await self.put(
            self._rest_uri('userDataStream', REST_API_VERSION),
            security_type = SecurityType.USER_STREAM,
            listenKey = listenKey
        )

    async def close_listen_key(self, listenKey):
        params = {
            'listenKey': listenKey
        }
        return await self.delete(
            self._rest_uri('userDataStream', REST_API_VERSION),
            security_type = SecurityType.USER_STREAM,
            listenKey = listenKey
        )

for getter_setting in APIS:
    define_getter(RestAPIGetters, **getter_setting)
