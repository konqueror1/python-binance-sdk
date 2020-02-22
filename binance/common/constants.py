KLINE_TYPE_PREFIX = 'kline_'

SUBTYPE_PROP_LIST = [
    'KLINE',

    'TRADE',
    'AGG_TRADE',
    'MINI_TICKER',
    'TICKER',
    'ORDER_BOOK',

    'ALL_MARKET_MINI_TICKERS',
    'ALL_MARKET_TICKERS',

    'USER'
]

SUBTYPE_VALUE_LIST = [
    'kline',

    'trade',
    'aggTrade',
    'miniTicker',
    'ticker',
    'depth',

    'allMarketMiniTickers',
    'allMarketTickers',

    'user'
]

class SubType:
    pass

def merge_attr(target, props, values=None):
    values = values or props

    for i in range(len(props)):
        k, v = props[i], values[i]
        setattr(target, k, v)

merge_attr(SubType, SUBTYPE_PROP_LIST, SUBTYPE_VALUE_LIST)

KLINE_INVERVAL_PROP_LIST = [
    'KLINE_1M',
    'KLINE_3M',
    'KLINE_5M',
    'KLINE_15M',
    'KLINE_30M',

    'KLINE_1H',
    'KLINE_2H',
    'KLINE_4H',
    'KLINE_6H',
    'KLINE_8H',
    'KLINE_12H',

    'KLINE_DAY',
    'KLINE_3DAY',

    'KLINE_WEEK',
    'KLINE_MONTH'
]

KLINE_INTERVAL_VALUE_LIST = [
    '1m',
    '3m',
    '5m',
    '15m',
    '30m',

    '1h',
    '2h',
    '4h',
    '6h',
    '8h',
    '12h',

    '1d',
    '3d',

    '1w',
    '1M'
]

class KlineInterval:
    pass

merge_attr(KlineInterval, KLINE_INVERVAL_PROP_LIST, KLINE_INTERVAL_VALUE_LIST)

RET_OK = 0
RET_ERROR = -1
ERROR_PREFIX = '[BinanceSDK] '

# RetryPolicy
# ==================================================

ATOM_RETRY_DELAY = 0.1
MAX_RETRIES_BEFORE_RESET = 10

# If the network connection fails,
#   we increase the delay by 100ms per failure
#   and reset the retry counter after 10 failures
def DEFAULT_RETRY_POLICY(retries: int):
    delay = retries * ATOM_RETRY_DELAY
    reset = retries >= MAX_RETRIES_BEFORE_RESET
    return False, delay, reset

# Streams
# ==================================================

STREAM_HOST = 'wss://stream.binance.com'

DEFAULT_STREAM_TIMEOUT = 5

# Close code used by binance.Stream
# https://tools.ietf.org/html/rfc6455#section-7.4.2
DEFAULT_STREAM_CLOSE_CODE = 4999

DEFAULT_DEPTH_LIMIT = 100

STREAM_TYPE_MAP = {
    'e': 'type'
}

STREAM_OHLC_MAP = {
    'o': 'open',
    'h': 'high',
    'l': 'low',
    'c': 'close'
}

KEY_PAYLOAD = 'data'
KEY_PAYLOAD_TYPE = 'e'
KEY_STREAM_TYPE = 'stream'

ATOM = {}

# APIs
# ==================================================

class SecurityType:
    # {TYPE} = (NEED_API_KEY, NEED_SIGNATURE)
    NONE = (False, False)
    TRADE = (True, True)
    USER_DATA = (True, True)
    USER_STREAM = (True, False)
    MARKET_DATA = (True, False)

class RequestMethod:
    GET = 'get'
    POST = 'post'
    PUT = 'put'
    DELETE = 'delete'

HEADER_API_KEY = 'X-MBX-APIKEY'

REST_API_VERSION = 'v3'
REST_API_HOST = 'https://api.binance.com'

# WEBSITE_HOST = 'https://www.binance.com'

# Binance now supports default 443 port for websockets


# TIME_IN_FORCE_GTC = 'GTC'


# SIDE_BUY = 'BUY'
# SIDE_SELL = 'SELL'

# ORDER_TYPE_LIMIT = 'LIMIT'
# ORDER_TYPE_MARKET = 'MARKET'

# TIME_IN_FORCE_GTC = 'GTC'  # Good till cancelled
# TIME_IN_FORCE_IOC = 'IOC'  # Immediate or cancel
# TIME_IN_FORCE_FOK = 'FOK'  # Fill or kill

# For accessing the data returned by Client.aggregate_trades().
# AGG_ID = 'a'
