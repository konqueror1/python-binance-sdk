from enum import Enum as _Enum

__all__ = (
    'SubType',
    'KlineInterval',
    'SecurityType',
    'RequestMethod',
    'TimeInForce',
    'OrderSide'
)

KLINE_TYPE_PREFIX = 'kline_'


class Enum(_Enum):
    def __str__(self):
        return self.value


class SubType(Enum):
    KLINE = 'kline'

    TRADE = 'trade'
    AGG_TRADE = 'aggTrade'
    MINI_TICKER = 'miniTicker'
    TICKER = 'ticker'
    ORDER_BOOK = 'depth'

    ALL_MARKET_MINI_TICKERS = 'allMarketMiniTickers'
    ALL_MARKET_TICKERS = 'allMarketTickers'

    USER = 'user'


class KlineInterval(Enum):
    M1 = '1m'
    M3 = '3m'
    M5 = '5m'
    M15 = '15m'
    M30 = '30m'

    H = '1h'
    H2 = '2h'
    H4 = '4h'
    H6 = '6h'
    H8 = '8h'
    H12 = '12h'

    DAY = '1d'
    DAY3 = '3d'

    WEEK = '1w'
    MONTH = '1M'


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


class SecurityType(Enum):
    # {TYPE} = (NEED_API_KEY, NEED_SIGNATURE)
    NONE = (False, False)
    TRADE = (True, True)
    USER_DATA = (True, True)
    USER_STREAM = (True, False)
    MARKET_DATA = (True, False)


class RequestMethod(Enum):
    GET = 'get'
    POST = 'post'
    PUT = 'put'
    DELETE = 'delete'


class OrderSide(Enum):
    BUY = 'BUY'
    SELL = 'SELL'


class OrderType(Enum):
    LIMIT = 'LIMIT'
    MARKET = 'MARKET'
    STOP_LOSS = 'STOP_LOSS'
    STOP_LOSS_LIMIT = 'STOP_LOSS_LIMIT'
    TAKE_PROFIT = 'TAKE_PROFIT'
    TAKE_PROFIT_LIMIT = 'TAKE_PROFIT_LIMIT'
    LIMIT_MAKER = 'LIMIT_MAKER'


class OrderRespType(Enum):
    ACK = 'ACK'
    RESULT = 'RESULT'
    FULL = 'FULL'


class TimeInForce(Enum):
    GTC = 'GTC'
    IOC = 'IOC'
    FOK = 'FOK'


HEADER_API_KEY = 'X-MBX-APIKEY'

REST_API_VERSION = 'v3'
REST_API_HOST = 'https://api.binance.com'
