from typing import (
    Awaitable
)

from binance.common.constants import (
    REST_API_VERSION,
    SecurityType,
    RequestMethod
)

# Rest APIs ref:
# https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md
APIS = [

    # General Endpoints

    dict(
        name='ping',
        path='ping',

        # Support params, defaults to `True`
        params=False,

        # request method, defaults to 'get'
        # method = RequestMethod.GET

        # SecurityType, defaults to NONE (False, False)
        # ref: https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#endpoint-security-type
        # security_type=SecurityType.NONE

        # api version
        # version=REST_API_VERSION
    ),

    dict(
        name='get_server_time',
        path='time',
        params=False
    ),

    dict(
        name='get_exchange_info',
        path='exchangeInfo',
        params=False
    ),

    # Market Data endpoints

    dict(
        name='get_orderbook',
        path='depth'
    ),

    dict(
        name='get_recent_trades',
        path='trades'
    ),

    dict(
        name='get_historical_trades',
        path='historicalTrades',
        security_type=SecurityType.MARKET_DATA
    ),

    dict(
        name='get_aggregate_trades',
        path='aggTrades'
    ),

    dict(
        name='get_klines',
        path='klines'
    ),

    dict(
        name='get_average_price',
        path='avgPrice'
    ),

    dict(
        name='get_ticker',
        path='ticker/24hr'
    ),

    dict(
        name='get_ticker_price',
        path='ticker/price'
    ),

    dict(
        name='get_orderbook_ticker',
        path='ticker/bookTicker'
    ),

    # Account endpoints

    dict(
        name='create_order',
        path='order',
        method=RequestMethod.POST,
        security_type=SecurityType.TRADE
    ),

    dict(
        name='create_test_order',
        path='order/test',
        method=RequestMethod.POST,
        security_type=SecurityType.TRADE
    ),

    dict(
        name='get_order',
        path='order',
        security_type=SecurityType.USER_DATA
    ),

    dict(
        name='cancel_order',
        path='order',
        method=RequestMethod.DELETE,
        security_type=SecurityType.TRADE
    ),

    dict(
        name='get_open_orders',
        path='openOrders',
        security_type=SecurityType.USER_DATA
    ),

    dict(
        name='get_all_orders',
        path='allOrders',
        security_type=SecurityType.USER_DATA
    ),

    # Create a one-cancels-the-other order
    dict(
        name='create_oco',
        path='order/oco',
        method=RequestMethod.POST,
        security_type=SecurityType.TRADE
    ),

    dict(
        name='cancel_oco',
        path='orderList',
        method=RequestMethod.DELETE,
        security_type=SecurityType.NONE
    ),

    dict(
        name='get_oco',
        path='orderList',
        security_type=SecurityType.USER_DATA
    ),

    dict(
        name='get_all_oco',
        path='allOrderList',
        security_type=SecurityType.USER_DATA
    ),

    dict(
        name='get_open_oco',
        path='openOrderList',
        security_type=SecurityType.USER_DATA
    ),

    dict(
        name='get_account',
        path='account',
        security_type=SecurityType.USER_DATA
    ),

    dict(
        name='get_trades',
        path='myTrades',
        security_type=SecurityType.USER_DATA
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

    origin = getattr(Target, name)

    # Migrate the docstring to the new getter
    getter.__doc__ = origin.__doc__

    setattr(Target, name, getter)

# Google Style guide:
# https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html
# Sphinx extension supports a mixed style of
#   google and reStructuredText formatting

# Neither VSCode Python language server nor Jedi server could handle
#   class methods which are dynamically added by `setattr`, see:
# https://jedi.readthedocs.io/en/latest/docs/features.html#not-supported
#
# So, however, we need to just create those methods and docstrings first,
#   then override them.

# pylint: disable=no-member


class RestAPIGetters:
    _api_host: str

    def _rest_uri(self, path, version=REST_API_VERSION) -> str:
        return self._api_host + '/api/' + version + '/' + path

    def ping(self) -> Awaitable:
        """Tests connectivity to the Rest API

        Returns:
            dict: An empty dict `{}`
        """
        ...  # pragma: no cover

    def get_server_time(self) -> Awaitable:
        """Tests connectivity to the Rest API and gets the current server time.

        Returns:
            dict: A dict contains only one key `serverTime`. For example::

                {"serverTime": 1499827319559}
        """
        ...  # pragma: no cover

    def get_exchange_info(self) -> Awaitable:
        """Gets Current exchange trading rules and symbol information.

        Returns:
            dict: A dict of the exchange info. For example::

                {
                    'timezone': 'UTC',
                    'serverTime': 1565246363776,
                    'rateLimits': [
                        {
                            # These are defined in the `ENUM definitions` section under `Rate Limiters (rateLimitType)`.
                            # All limits are optional
                        }
                    ],
                    'exchangeFilters': [
                        # These are the defined filters in the `Filters` section.
                        # All filters are optional.
                    ],
                    'symbols': [
                        {
                            'symbol': 'ETHBTC',
                            'status': 'TRADING',
                            'baseAsset': 'ETH',
                            'baseAssetPrecision': 8,
                            'quoteAsset': 'BTC',
                            'quotePrecision': 8,
                            'baseCommissionPrecision': 8,
                            'quoteCommissionPrecision': 8,
                            'orderTypes': [
                                'LIMIT',
                                'LIMIT_MAKER',
                                'MARKET',
                                'STOP_LOSS',
                                'STOP_LOSS_LIMIT',
                                'TAKE_PROFIT',
                                'TAKE_PROFIT_LIMIT'
                            ],
                            'icebergAllowed': True,
                            'ocoAllowed': True,
                            'quoteOrderQtyMarketAllowed': True,
                            'isSpotTradingAllowed': True,
                            'isMarginTradingAllowed': True,
                            'filters': [
                                # These are defined in the Filters section.
                                # All filters are optional
                            ]
                        }
                    ]
                }
        """
        ...  # pragma: no cover

    # Market Data endpoints

    def get_orderbook(self, **kwargs) -> Awaitable:
        """Gets the orderbook for a certain symbol.

        Args:
            symbol (str): The symbol of the orderbook.
            limit (:obj:`int`, optional): Defaults to 100; max 5000. Valid limits: [5, 10, 20, 50, 100, 500, 1000, 5000].

        Returns:
            dict: The orderbook. For example::

                {
                    'lastUpdateId': 1027024,
                    'bids': [
                        [
                            '4.00000000',  # PRICE
                            '431.00000000' # QTY
                        ]
                    ],
                    'asks': [
                        [
                            '4.00000200',
                            '12.00000000'
                        ]
                    ]
                }
        """
        ...  # pragma: no cover

    def get_recent_trades(self, **kwargs) -> Awaitable:
        """Gets recent trades.

        Args:
            symbol (str): The symbol.
            limit (:obj:`int`, optional): Defaults to 100; max 5000.

        Returns:
            list: A list of recent trade orders. For example::

                [
                    {
                        'id': 28457,
                        'price': '4.00000100',
                        'qty': '12.00000000',
                        'quoteQty': '48.000012',
                        'time': 1499865549590,
                        'isBuyerMaker': True,
                        'isBestMatch': True
                    }

                    # ...
                ]
        """
        ...  # pragma: no cover

    def get_historical_trades(self, **kwargs) -> Awaitable:
        """Get older trades.

        Args:
            symbol (str): The symbol name
            limit (:obj:`int`, optional): Defaults to 500, max 1000.
            fromId (:obj:`long`, optional): TradeId to fetch from. Default gets most recent trades.

        Returns:
            list: A list of trade orders. For example::

                [
                    {
                        'id': 28457,
                        'price': '4.00000100',
                        'qty': '12.00000000',
                        'quoteQty': '48.000012',
                        'time': 1499865549590,
                        'isBuyerMaker': True,
                        'isBestMatch': True
                    }

                    # ...
                ]
        """
        ...  # pragma: no cover

    def get_aggregate_trades(self, **kwargs) -> Awaitable:
        """Gets compressed, aggregate trades. Trades that fill at the time, from the same order, with the same price will have the quantity aggregated.

        Args:
            symbol (str): The symbol name.
            fromId (:obj:`long`, optional): ID to get aggregate trades from INCLUSIVE.
            startTime (:obj:`long`, optional): Timestamp in ms to get aggregate trades from INCLUSIVE.
            endTime (:obj:`long`, optional): Timestamp in ms to get aggregate trades until INCLUSIVE.
            limit (:obj:`int`, optional): Defaults to 500, max 1000.

            If both ``startTime`` and ``endTime`` are sent, time between ``startTime`` and ``endTime`` must be less than 1 hour.
            If ``fromId``, ``startTime``, and ``endTime`` are not sent, the most recent aggregate trades will be returned.

        Returns:
            list: A list of aggregated trade orders. For example::

                [
                    {
                        'a': 26129,         # Aggregate tradeId
                        'p': '0.01633102',  # Price
                        'q': '4.70443515',  # Quantity
                        'f': 27781,         # First tradeId
                        'l': 27781,         # Last tradeId
                        'T': 1498793709153, # Timestamp
                        'm': True,          # Was the buyer the maker?
                        'M': True           # Was the trade the best price match?
                    }
                ]
        """
        ...  # pragma: no cover

    def get_klines(self, **kwargs) -> Awaitable:
        """Gets kline/candlestick bars for a symbol. Klines are uniquely identified by their open time.

        Args:
            symbol (str):
            interval (KlineInterval):
            startTime (:obj:`long`, optional):
            endTime (:obj:`long`, optional):
            limit (:obj:`int`, optional): Defaults to 500, max 1000.

            If ``startTime`` and ``endTime`` are not sent, the most recent klines are returned.

        Returns:
            list: A list of candlesticks. For example::

                [
                    [
                        1499040000000,      # Open time
                        '0.01634790',       # Open
                        '0.80000000',       # High
                        '0.01575800',       # Low
                        '0.01577100',       # Close
                        '148976.11427815',  # Volume
                        1499644799999,      # Close time
                        '2434.19055334',    # Quote asset volume
                        308,                # Number of trades
                        '1756.87402397',    # Taker buy base asset volume
                        '28.46694368',      # Taker buy quote asset volume
                        '17928899.62484339' # Ignore.
                    ]
                ]
        """
        ...  # pragma: no cover

    def get_average_price(self, **kwargs) -> Awaitable:
        """Gets current average price for a symbol.

        Args:
            symbol (str): The symbol name.

        Returns:
            dict: For example::

                {
                    'mins': 5,
                    'price': '9.35751834'
                }
        """
        ...  # pragma: no cover

    def get_ticker(self, **kwargs) -> Awaitable:
        """Gets 24 hour rolling window price change statistics. Careful when accessing this with no symbol.

        Weight: 1 for a single symbol, 40 when the symbol parameter is omitted.

        Args:
            symbol (:obj:`str`, optional): If the ``symbol`` is not sent, tickers for all symbols will be returned in a list.

        Returns:
            dict: If the ``symbol`` parameter is specified::

                {
                    'symbol': 'BNBBTC',
                    'priceChange': '-94.99999800',
                    'priceChangePercent': '-95.960',
                    'weightedAvgPrice': '0.29628482',
                    'prevClosePrice': '0.10002000',
                    'lastPrice': '4.00000200',
                    'lastQty': '200.00000000',
                    'bidPrice': '4.00000000',
                    'askPrice': '4.00000200',
                    'openPrice': '99.00000000',
                    'highPrice': '100.00000000',
                    'lowPrice': '0.10000000',
                    'volume': '8913.30000000',
                    'quoteVolume': '15.30000000',
                    'openTime': 1499783499040,
                    'closeTime': 1499869899040,
                    'firstId': 28385,   # First tradeId
                    'lastId': 28460,    # Last tradeId
                    'count': 76         # Trade count
                }

            list: If the ``symbol`` parameter is omitted::

                [
                    {
                        'symbol': 'BNBBTC',
                        'priceChange': '-94.99999800',
                        'priceChangePercent': '-95.960',
                        'weightedAvgPrice': '0.29628482',
                        'prevClosePrice': '0.10002000',
                        'lastPrice': '4.00000200',
                        'lastQty': '200.00000000',
                        'bidPrice': '4.00000000',
                        'askPrice': '4.00000200',
                        'openPrice': '99.00000000',
                        'highPrice': '100.00000000',
                        'lowPrice': '0.10000000',
                        'volume': '8913.30000000',
                        'quoteVolume': '15.30000000',
                        'openTime': 1499783499040,
                        'closeTime': 1499869899040,
                        'firstId': 28385,   # First tradeId
                        'lastId': 28460,    # Last tradeId
                        'count': 76         # Trade count
                    }
                ]

        """
        ...  # pragma: no cover

    def get_ticker_price(self) -> Awaitable:
        """Gets latest price for a symbol or symbols.

        Weight: 1 for a single symbol; 2 when the symbol parameter is omitted.

        Args:
            symbol (:obj:`str`, optional): If the ``symbol`` is not sent, prices for all symbols will be returned in a list.

        Returns:
            dict: If the ``symbol`` parameter is specified::

                {
                    'symbol': 'LTCBTC',
                    'price': '4.00000200'
                }

            list: If the ``symbol`` parameter is omitted::

                [
                    {
                        'symbol': 'LTCBTC',
                        'price': '4.00000200'
                    },
                    {
                        'symbol': 'ETHBTC',
                        'price': '0.07946600'
                    }
                ]
        """
        ...  # pragma: no cover

    def get_orderbook_ticker(self) -> Awaitable:
        """Gets the best price/quantity on the order book for a symbol or symbols.

        Weight: 1 for a single symbol; 2 when the symbol parameter is omitted.

        Args:
            symbol (:obj:`str`, optional): If the ``symbol`` is not sent, bookTickers for all symbols will be returned in a list.

        Returns:
            dict: If the ``symbol`` parameter is specified::

                {
                    'symbol': 'LTCBTC',
                    'bidPrice': '4.00000000',
                    'bidQty': '431.00000000',
                    'askPrice': '4.00000200',
                    'askQty': '9.00000000'
                }


            list: If the ``symbol`` parameter is omitted::

                [
                    {
                        'symbol': 'LTCBTC',
                        'bidPrice': '4.00000000',
                        'bidQty': '431.00000000',
                        'askPrice': '4.00000200',
                        'askQty': '9.00000000'
                    },
                    {
                        'symbol': 'ETHBTC',
                        'bidPrice': '0.07946700',
                        'bidQty': '9.00000000',
                        'askPrice': '100000.00000000',
                        'askQty': '1000.00000000'
                    }
                ]
        """
        ...  # pragma: no cover

    # Account endpoints

    def create_order(self, **kwargs) -> Awaitable:
        """Sends in a new order.

        Weight: 1

        Args:
            symbol (str): The symbol name.
            side (OrderSide):
            type (OrderType):
            timeInForce (:obj:`TimeInForce`, optional):
            quantity (:obj:`float`, optional):
            quoteOrderQty (:obj:`float`, optional):
            price (:obj:`float`, optional):
            newClientOrderId (:obj:`str`, optional): A unique id for the order. Automatically generated if not sent.
            stopPrice (:obj:`float`, optional): Used with `STOP_LOSS`, `STOP_LOSS_LIMIT`, `TAKE_PROFIT`, and `TAKE_PROFIT_LIMIT` orders.
            icebergQty (:obj:`float`, optional): Used with `LIMIT`, `STOP_LOSS_LIMIT`, and `TAKE_PROFIT_LIMIT` to create an iceberg order.
            newOrderRespType (:obj:`OrderRespType`, optional): Set the response JSON. `ACK`, `RESULT`, or `FULL`; `MARKET` and `LIMIT` order types default to `FULL`, all other orders default to `ACK`.
            recvWindow (:obj:`long`, optional): The value cannot be greater than 60000.
            timestamp (long):

        Additional mandatory parameters based on ``type`` (OrderType):
            LIMIT: ``timeInForce``, ``quantity``, ``price``
            MARKET:	``quantity`` or ``quoteOrderQty``
            STOP_LOSS: ``quantity``, ``stopPrice``
            STOP_LOSS_LIMIT: ``timeInForce``, ``quantity``, ``price``, ``stopPrice``
            TAKE_PROFIT: ``quantity``, ``stopPrice``
            TAKE_PROFIT_LIMIT: ``timeInForce``, ``quantity``, ``price``, ``stopPrice``
            LIMIT_MAKER: ``quantity``, ``price``

        Returns:
            Response `ACK`::

                {
                    'symbol': 'BTCUSDT',
                    'orderId': 28,
                    'orderListId': -1, # Unless OCO, value will be - 1
                    'clientOrderId': '6gCrw2kRUAF9CvJDGP16IP',
                    'transactTime': 1507725176595
                }

            Response `RESULT`::

                {
                    'symbol': 'BTCUSDT',
                    'orderId': 28,
                    'orderListId': -1, # Unless OCO, value will be - 1
                    'clientOrderId': '6gCrw2kRUAF9CvJDGP16IP',
                    'transactTime': 1507725176595,
                    'price': '0.00000000',
                    'origQty': '10.00000000',
                    'executedQty': '10.00000000',
                    'cummulativeQuoteQty': '10.00000000',
                    'status': 'FILLED',
                    'timeInForce': 'GTC',
                    'type': 'MARKET',
                    'side': 'SELL'
                }

            Response `FULL`::

                {
                    'symbol': 'BTCUSDT',
                    'orderId': 28,
                    'orderListId': -1, # Unless OCO, value will be - 1
                    'clientOrderId': '6gCrw2kRUAF9CvJDGP16IP',
                    'transactTime': 1507725176595,
                    'price': '0.00000000',
                    'origQty': '10.00000000',
                    'executedQty': '10.00000000',
                    'cummulativeQuoteQty': '10.00000000',
                    'status': 'FILLED',
                    'timeInForce': 'GTC',
                    'type': 'MARKET',
                    'side': 'SELL',
                    'fills': [
                        {
                            'price': '4000.00000000',
                            'qty': '1.00000000',
                            'commission': '4.00000000',
                            'commissionAsset': 'USDT'
                        },
                        {
                            'price': '3999.00000000',
                            'qty': '5.00000000',
                            'commission': '19.99500000',
                            'commissionAsset': 'USDT'
                        }

                        # ,...
                    ]
                }
        """
        ...  # pragma: no cover

    def create_test_order(self, **kwargs) -> Awaitable:
        """Tests new order creation and signature/recvWindow long. Creates and validates a new order but does not send it into the matching engine.

        Which has the same parameters as `client.create_order()`
        """
        ...  # pragma: no cover

    def get_order(self, **kwargs) -> Awaitable:
        """Checks an order's status.

        Args:
            symbol (str):
            orderId (:obj:`long`, optional):
            origClientOrderId (:obj:`str`, optional): The value cannot be greater than 60000
            recvWindow (:obj:`long`, optional):
            timestamp (long):

            Either ``orderId`` or ``origClientOrderId`` must be sent.
            For some historical orders `cummulativeQuoteQty` will be < 0, meaning the data is not available at this time.

        Returns:
            dict: A dict of order info. For example::

                {
                    'symbol': 'LTCBTC',
                    'orderId': 1,
                    'orderListId': -1 # Unless part of an OCO, the value will always be - 1.
                    'clientOrderId': 'myOrder1',
                    'price': '0.1',
                    'origQty': '1.0',
                    'executedQty': '0.0',
                    'cummulativeQuoteQty': '0.0',
                    'status': 'NEW',
                    'timeInForce': 'GTC',
                    'type': 'LIMIT',
                    'side': 'BUY',
                    'stopPrice': '0.0',
                    'icebergQty': '0.0',
                    'time': 1499827319559,
                    'updateTime': 1499827319559,
                    'isWorking': True,
                    'origQuoteOrderQty': '0.000000'
                }
        """
        ...  # pragma: no cover

    def cancel_order(self, **kwargs) -> Awaitable:
        """Cancel an active order.

        Args:
            symbol (str):
            orderId (:obj:`long`, optional):
            origClientOrderId (:obj:`str`, optional):
            newClientOrderId (:obj:`str`, optional): Used to uniquely identify this cancel. Automatically generated by default.
            recvWindow (:obj:`long`, optional): The value cannot be greater than 60000
            timestamp (long):

            Either ``orderId`` or ``origClientOrderId`` must be sent.

        Returns:
            dict: A dict of order status. For example::

                {
                    'symbol': 'LTCBTC',
                    'origClientOrderId': 'myOrder1',
                    'orderId': 4,
                    'orderListId': -1, # Unless part of an OCO, the value will always be - 1.
                    'clientOrderId': 'cancelMyOrder1',
                    'price': '2.00000000',
                    'origQty': '1.00000000',
                    'executedQty': '0.00000000',
                    'cummulativeQuoteQty': '0.00000000',
                    'status': 'CANCELED',
                    'timeInForce': 'GTC',
                    'type': 'LIMIT',
                    'side': 'BUY'
                }

        """
        ...  # pragma: no cover

    def get_open_orders(self, **kwargs) -> Awaitable:
        """Gets all open orders on a symbol. Careful when accessing this with no symbol.

        Args:
            symbol (str):
            recvWindow (:obj:`long`, optional): The value cannot be greater than 60000
            timestamp (long):

            If the ``symbol`` is not sent, orders for all symbols will be returned in an list.

        Returns:
            list: For example::

                [
                    {
                        'symbol': 'LTCBTC',
                        'orderId': 1,
                        'orderListId': -1, # Unless OCO, the value will always be - 1
                        'clientOrderId': 'myOrder1',
                        'price': '0.1',
                        'origQty': '1.0',
                        'executedQty': '0.0',
                        'cummulativeQuoteQty': '0.0',
                        'status': 'NEW',
                        'timeInForce': 'GTC',
                        'type': 'LIMIT',
                        'side': 'BUY',
                        'stopPrice': '0.0',
                        'icebergQty': '0.0',
                        'time': 1499827319559,
                        'updateTime': 1499827319559,
                        'isWorking': True,
                        'origQuoteOrderQty': '0.000000'
                    }
                ]

        """
        ...  # pragma: no cover

    def get_all_orders(self, **kwargs) -> Awaitable:
        """Gets all account orders, either active, or canceled, or filled.

        Args:
            symbol (str):
            orderId (:obj:`long`, optional):
            startTime (:obj:`long`, optional):
            endTime (:obj:`long`, optional):
            limit (:obj:`int`, optional): Defaults to 500, max 1000.
            recvWindow (:obj:`long`, optional): The value cannot be greater than 60000
            timestamp (long):

            If ``orderId`` is set, it will get orders >= that ``orderId``. Otherwise most recent orders are returned.
            For some historical orders `cummulativeQuoteQty` will be < 0, meaning the data is not available at this time.

        Returns:
            list: A list of dicts of all queried orders. For example::

                [
                    {
                        'symbol': 'LTCBTC',
                        'orderId': 1,
                        'orderListId': -1, # Unless OCO, the value will always be - 1
                        'clientOrderId': 'myOrder1',
                        'price': '0.1',
                        'origQty': '1.0',
                        'executedQty': '0.0',
                        'cummulativeQuoteQty': '0.0',
                        'status': 'NEW',
                        'timeInForce': 'GTC',
                        'type': 'LIMIT',
                        'side': 'BUY',
                        'stopPrice': '0.0',
                        'icebergQty': '0.0',
                        'time': 1499827319559,
                        'updateTime': 1499827319559,
                        'isWorking': True,
                        'origQuoteOrderQty': '0.000000'
                    }
                ]
        """
        ...  # pragma: no cover

    def create_oco(self, **kwargs) -> Awaitable:
        """Sends in a new one-cancels-the-other order

        Args:
            symbol (str):
            listClientOrderId (:obj:`str`, optional): A unique Id for the entire orderList
            side (OrderSide):
            quantity (float):
            limitClientOrderId (:obj:`str`, optional): A unique Id for the limit order
            price (float):
            limitIcebergQty (:obj:`float`, optional): Used to make the LIMIT_MAKER leg an iceberg order.
            stopClientOrderId (:obj:`str`, optional): A unique Id for the stop loss/stop loss limit leg
            stopPrice (float):
            stopLimitPrice (:obj:`float`, optional): If provided, stopLimitTimeInForce is required.
            stopIcebergQty (:obj:`float`, optional): Used with STOP_LOSS_LIMIT leg to make an iceberg order.
            stopLimitTimeInForce (:obj:`TimeInForce`, optional): time in force.
            newOrderRespType (:obj:`OrderRespType`, optional) Set the response JSON.
            recvWindow (:obj:`long`, optional): The value cannot be greater than 60000
            timestamp (long):

        Additional Info:
            Price Restrictions:
                SELL: Limit Price > Last Price > Stop Price
                BUY: Limit Price < Last Price < Stop Price
            Quantity Restrictions:
                Both legs must have the same quantity.
                ICEBERG quantities however do not have to be the same

        Returns:
            dict: A dict of the oco order. For example::

                {
                    'orderListId': 0,
                    'contingencyType': 'OCO',
                    'listStatusType': 'EXEC_STARTED',
                    'listOrderStatus': 'EXECUTING',
                    'listClientOrderId': 'JYVpp3F0f5CAG15DhtrqLp',
                    'transactionTime': 1563417480525,
                    'symbol': 'LTCBTC',
                    'orders': [
                        {
                            'symbol': 'LTCBTC',
                            'orderId': 2,
                            'clientOrderId': 'Kk7sqHb9J6mJWTMDVW7Vos'
                        },
                        {
                            'symbol': 'LTCBTC',
                            'orderId': 3,
                            'clientOrderId': 'xTXKaGYd4bluPVp78IVRvl'
                        }
                    ],
                    'orderReports': [
                        {
                            'symbol': 'LTCBTC',
                            'orderId': 2,
                            'orderListId': 0,
                            'clientOrderId': 'Kk7sqHb9J6mJWTMDVW7Vos',
                            'transactTime': 1563417480525,
                            'price': '0.000000',
                            'origQty': '0.624363',
                            'executedQty': '0.000000',
                            'cummulativeQuoteQty': '0.000000',
                            'status': 'NEW',
                            'timeInForce': 'GTC',
                            'type': 'STOP_LOSS',
                            'side': 'BUY',
                            'stopPrice': '0.960664'
                        },
                        {
                            'symbol': 'LTCBTC',
                            'orderId': 3,
                            'orderListId': 0,
                            'clientOrderId': 'xTXKaGYd4bluPVp78IVRvl',
                            'transactTime': 1563417480525,
                            'price': '0.036435',
                            'origQty': '0.624363',
                            'executedQty': '0.000000',
                            'cummulativeQuoteQty': '0.000000',
                            'status': 'NEW',
                            'timeInForce': 'GTC',
                            'type': 'LIMIT_MAKER',
                            'side': 'BUY'
                        }
                    ]
                }
        """
        ...  # pragma: no cover

    def cancel_oco(self, **kwargs) -> Awaitable:
        """Cancels an entire Order List

        Weight: 1

        Args:
            symbol (str):
            orderListId (:obj:`long`, optional):
            listClientOrderId (:obj:`str`, optional): A unique Id for the entire orderList.
            newClientOrderId (:obj:`str`, optional): Used to uniquely identify this cancel. Automatically generated by default.
            recvWindow (:obj:`long`, optional): The value cannot be greater than 60000。
            timestamp (long):

            Either ``orderListId`` or ``listClientOrderId`` must be provided.

            Canceling an individual leg will cancel the entire OCO

        Returns:
            dict: For example::

                {
                    'orderListId': 0,
                    'contingencyType': 'OCO',
                    'listStatusType': 'ALL_DONE',
                    'listOrderStatus': 'ALL_DONE',
                    'listClientOrderId': 'C3wyj4WVEktd7u9aVBRXcN',
                    'transactionTime': 1574040868128,
                    'symbol': 'LTCBTC',
                    'orders': [
                        {
                            'symbol': 'LTCBTC',
                            'orderId': 2,
                            'clientOrderId': 'pO9ufTiFGg3nw2fOdgeOXa'
                        },
                        {
                            'symbol': 'LTCBTC',
                            'orderId': 3,
                            'clientOrderId': 'TXOvglzXuaubXAaENpaRCB'
                        }
                    ],
                    'orderReports': [
                        {
                            'symbol': 'LTCBTC',
                            'origClientOrderId': 'pO9ufTiFGg3nw2fOdgeOXa',
                            'orderId': 2,
                            'orderListId': 0,
                            'clientOrderId': 'unfWT8ig8i0uj6lPuYLez6',
                            'price': '1.00000000',
                            'origQty': '10.00000000',
                            'executedQty': '0.00000000',
                            'cummulativeQuoteQty': '0.00000000',
                            'status': 'CANCELED',
                            'timeInForce': 'GTC',
                            'type': 'STOP_LOSS_LIMIT',
                            'side': 'SELL',
                            'stopPrice': '1.00000000'
                        },
                        {
                            'symbol': 'LTCBTC',
                            'origClientOrderId': 'TXOvglzXuaubXAaENpaRCB',
                            'orderId': 3,
                            'orderListId': 0,
                            'clientOrderId': 'unfWT8ig8i0uj6lPuYLez6',
                            'price': '3.00000000',
                            'origQty': '10.00000000',
                            'executedQty': '0.00000000',
                            'cummulativeQuoteQty': '0.00000000',
                            'status': 'CANCELED',
                            'timeInForce': 'GTC',
                            'type': 'LIMIT_MAKER',
                            'side': 'SELL'
                        }
                    ]
                }
        """
        ...  # pragma: no cover

    def get_oco(self, **kwargs) -> Awaitable:
        """Retrieves a specific OCO based on provided optional parameters.

        Weight: 1

        Args:
            orderListId (:obj:`long`, optional):
            origClientOrderId (:obj:`str`, optional): A unique Id for the entire orderList.
            recvWindow (:obj:`long`, optional): The value cannot be greater than 60000。
            timestamp (long):

            Either ``orderListId`` or ``listClientOrderId`` must be provided

        Returns:
            dict: For example::

                {
                    'orderListId': 27,
                    'contingencyType': 'OCO',
                    'listStatusType': 'EXEC_STARTED',
                    'listOrderStatus': 'EXECUTING',
                    'listClientOrderId': 'h2USkA5YQpaXHPIrkd96xE',
                    'transactionTime': 1565245656253,
                    'symbol': 'LTCBTC',
                    'orders': [
                        {
                            'symbol': 'LTCBTC',
                            'orderId': 4,
                            'clientOrderId': 'qD1gy3kc3Gx0rihm9Y3xwS'
                        },
                        {
                            'symbol': 'LTCBTC',
                            'orderId': 5,
                            'clientOrderId': 'ARzZ9I00CPM8i3NhmU9Ega'
                        }
                    ]
                }

        """
        ...  # pragma: no cover

    def get_all_oco(self, **kwargs) -> Awaitable:
        """Retrieves all OCO based on provided optional parameters.

        Weight: 10

        Args:
            fromId (:obj:`long`, optional): If supplied, neither ``startTime`` or ``endTime`` can be provided
            startTime (:obj:`long`, optional):
            endTime (:obj:`long`, optional):
            limit (:obj:`int`, optional): Defaults to 500, max 1000.
            recvWindow (:obj:`long`, optional): The value cannot be greater than 60000。
            timestamp (long):

        Returns:
            dict: A list of dicts of queried oco. For example::

                [
                    {
                        'orderListId': 29,
                        'contingencyType': 'OCO',
                        'listStatusType': 'EXEC_STARTED',
                        'listOrderStatus': 'EXECUTING',
                        'listClientOrderId': 'amEEAXryFzFwYF1FeRpUoZ',
                        'transactionTime': 1565245913483,
                        'symbol': 'LTCBTC',
                        'orders': [
                            {
                                'symbol': 'LTCBTC',
                                'orderId': 4,
                                'clientOrderId': 'oD7aesZqjEGlZrbtRpy5zB'
                            },
                            {
                                'symbol': 'LTCBTC',
                                'orderId': 5,
                                'clientOrderId': 'Jr1h6xirOxgeJOUuYQS7V3'
                            }
                        ]
                    },
                    {
                        'orderListId': 28,
                        'contingencyType': 'OCO',
                        'listStatusType': 'EXEC_STARTED',
                        'listOrderStatus': 'EXECUTING',
                        'listClientOrderId': 'hG7hFNxJV6cZy3Ze4AUT4d',
                        'transactionTime': 1565245913407,
                        'symbol': 'LTCBTC',
                        'orders': [
                            {
                                'symbol': 'LTCBTC',
                                'orderId': 2,
                                'clientOrderId': 'j6lFOfbmFMRjTYA7rRJ0LP'
                            },
                            {
                                'symbol': 'LTCBTC',
                                'orderId': 3,
                                'clientOrderId': 'z0KCjOdditiLS5ekAFtK81'
                            }
                        ]
                    }
                ]
        """
        ...  # pragma: no cover

    def get_open_oco(self, **kwargs) -> Awaitable:
        """Retrieves open OCO.

        Weight: 2

        Args:
            recvWindow (:obj:`long`, optional): The value cannot be greater than 60000。
            timestamp (long):

        Returns:
            list: For example::

                [
                    {
                        'orderListId': 31,
                        'contingencyType': 'OCO',
                        'listStatusType': 'EXEC_STARTED',
                        'listOrderStatus': 'EXECUTING',
                        'listClientOrderId': 'wuB13fmulKj3YjdqWEcsnp',
                        'transactionTime': 1565246080644,
                        'symbol': '1565246079109',
                        'orders': [
                            {
                                'symbol': 'LTCBTC',
                                'orderId': 4,
                                'clientOrderId': 'r3EH2N76dHfLoSZWIUw1bT'
                            },
                            {
                                'symbol': 'LTCBTC',
                                'orderId': 5,
                                'clientOrderId': 'Cv1SnyPD3qhqpbjpYEHbd2'
                            }
                        ]
                    }
                ]
        """
        ...  # pragma: no cover

    def get_account(self, **kwargs) -> Awaitable:
        """Gets current account information.

        Weight: 5

        Args:
            recvWindow (:obj:`long`, optional): The value cannot be greater than 60000。
            timestamp (long):

        Returns:
            dict: For example::

                {
                    'makerCommission': 15,
                    'takerCommission': 15,
                    'buyerCommission': 0,
                    'sellerCommission': 0,
                    'canTrade': True,
                    'canWithdraw': True,
                    'canDeposit': True,
                    'updateTime': 123456789,
                    'accountType': 'SPOT',
                    'balances': [
                        {
                            'asset': 'BTC',
                            'free': '4723846.89208129',
                            'locked': '0.00000000'
                        },
                        {
                            'asset': 'LTC',
                            'free': '4763368.68006011',
                            'locked': '0.00000000'
                        }
                    ]
                }
        """
        ...  # pragma: no cover

    def get_trades(self, **kwargs) -> Awaitable:
        """Gets trades for a specific account and symbol.

        Args:
            symbol (str):
            startTime (:obj:`long`, optional):
            endTime (:obj:`long`, optional):
            fromId (:obj:`long`, optional): TradeId to fetch from. Default gets most recent trades.
            limit (:obj:`int`, optional): Defaults to 500, max 1000.
            recvWindow (:obj:`long`, optional): The value cannot be greater than 60000。
            timestamp (long):

            If ``fromId`` is set, it will get orders >= that ``fromId``. Otherwise most recent orders are returned.

        Returns:
            list: For example::

                [
                    {
                        'symbol': 'BNBBTC',
                        'id': 28457,
                        'orderId': 100234,
                        'orderListId': -1,
                        'price': '4.00000100',
                        'qty': '12.00000000',
                        'quoteQty': '48.000012',
                        'commission': '10.10000000',
                        'commissionAsset': 'BNB',
                        'time': 1499865549590,
                        'isBuyer': True,
                        'isMaker': False,
                        'isBestMatch': True
                    }
                ]

        """
        ...  # pragma: no cover

    # User data stream endpoints

    async def get_listen_key(self) -> str:
        """Starts a new user data stream and returns the listen key. The stream will close after 60 minutes unless a keepalive is sent.

        Returns:
            The listen key
        """
        res = await self.post(  # type: ignore
            self._rest_uri('userDataStream'),
            security_type=SecurityType.USER_STREAM
        )
        return res['listenKey']

    def keepalive_listen_key(self, listen_key: str) -> Awaitable:
        """Keepalives a user data stream to prevent a time out. User data streams will close after 60 minutes. It's recommended to send a ping about every 30 minutes.

        Args：
            listen_key: user stream listen key
        """
        return self.put(  # type: ignore
            self._rest_uri('userDataStream'),
            security_type=SecurityType.USER_STREAM,
            listenKey=listen_key
        )

    def close_listen_key(self, listen_key: str) -> Awaitable:
        """Closes out a user data stream.

        Args:
            listen_key: user stream listen key
        """
        return self.delete(  # type: ignore
            self._rest_uri('userDataStream'),
            security_type=SecurityType.USER_STREAM,
            listenKey=listen_key
        )


for getter_setting in APIS:
    define_getter(RestAPIGetters, **getter_setting)
