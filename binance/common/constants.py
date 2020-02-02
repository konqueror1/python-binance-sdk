__all__ = [
    'SubType', 'KlineType',
    'RET_OK', 'RET_ERROR'
]

KLINE_TYPE_LIST = [
    'K_1M',
    'K_3M',
    'K_5M',
    'K_15M',
    'K_30M',

    'K_1H',
    'K_2H',
    'K_4H',
    'K_6H',
    'K_12H',

    'K_DAY',
    'K_WEEK',
    'K_MONTH'
]

OTHER_TYPE_LIST = [
    'TICKER',
    'QUOTE',
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

PUBLIC_API_VERSION = 'v1'
WITHDRAW_API_VERSION = 'v3'
PRIVATE_API_VERSION = 'v3'
API_HOST = 'https://api.binance.com'
WEBSITE_HOST = 'https://www.binance.com'
