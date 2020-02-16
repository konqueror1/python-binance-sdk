KLINE_TYPE_PREFIX = 'kline_'

SUBTYPE_PROP_LIST = [
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
    'KLINE_MONTH',

    'TRADE',
    'AGG_TRADE',
    'MINI_TICKER',
    'TICKER',
    'ORDER_BOOK',

    'ALL_MARKET_MINI_TICKERS',
    'ALL_MARKET_TICKERS',

    'USER'
]

KLINE_SUBTYPE_LIST = [KLINE_TYPE_PREFIX + x for x in [
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
]]

SUBTYPE_VALUE_LIST = KLINE_SUBTYPE_LIST + [
    'trade',
    'aggTrade',
    'miniTicker',
    'ticker',
    'depth',

    'allMarketMiniTickers',
    'allMarketTickers',

    'user'
]

SUBTYPE_MAP = {}

class SubType(object):
    pass

for i in range(len(SUBTYPE_PROP_LIST)):
    k, v = SUBTYPE_PROP_LIST[i], SUBTYPE_VALUE_LIST[i]

    setattr(SubType, k, v)
    SUBTYPE_MAP[v] = k

RET_OK = 0
RET_ERROR = -1
ERROR_PREFIX = '[BinanceSDK] '

# TODO: api version always changes,
#   so that it should not be hardcoded globally.
# api versions should be api-specific
PUBLIC_API_VERSION = 'v1'
WITHDRAW_API_VERSION = 'v3'
PRIVATE_API_VERSION = 'v3'

API_HOST = 'https://api.binance.com'
WEBSITE_HOST = 'https://www.binance.com'

# Binance now supports default 443 port for websockets
STREAM_HOST = 'wss://stream.binance.com'

TIME_IN_FORCE_GTC = 'GTC'

ATOM_RETRY_DELAY = 0.1
MAX_RETRIES_BEFORE_RESET = 10

def DEFAULT_RETRY_POLICY(retries: int):
    delay = retries * ATOM_RETRY_DELAY
    reset = retries >= MAX_RETRIES_BEFORE_RESET
    return False, delay, reset

DEFAULT_STREAM_TIMEOUT = 5

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
