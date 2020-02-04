__all__ = [
    'SubType', 'KlineType',
    'RET_OK', 'RET_ERROR'
]

KLINE_TYPE_LIST = [
    'KLINE_1M',
    'KLINE_3M',
    'KLINE_5M',
    'KLINE_15M',
    'KLINE_30M',

    'KLINE_1H',
    'KLINE_2H',
    'KLINE_4H',
    'KLINE_6H',
    'KLINE_12H',

    'KLINE_DAY',
    'KLINE_3DAY',
    'KLINE_WEEK',
    'KLINE_MONTH'
]

OTHER_TYPE_LIST = [
    'AGG_TRADE',
    'TICKER',
    'ORDER_BOOK'
]

SUBTYPE_MAP = {}
subtype_counter = 0

KTYPE_MAP = {}
ktype_counter = 0

class SubType(object):
    pass

class KlineType(object):
    pass

for t in KLINE_TYPE_LIST:
    setattr(SubType, t, t)
    SUBTYPE_MAP[t] = ++ subtype_counter

    setattr(KlineType, t, t)
    KTYPE_MAP[t] = ++ ktype_counter

for t in OTHER_TYPE_LIST:
    setattr(SubType, t, t)
    SUBTYPE_MAP[t] = ++ subtype_counter

KLINE_SUBTYPE_LIST = [
    getattr(SubType, t) for i in KLINE_TYPE_LIST
]

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
STREAM_HOST = 'wss://stream.binance.com'

TIME_IN_FORCE_GTC = 'GTC'
