import traceback

from binance.common.constants import STREAM_TYPE_MAP, STREAM_OHLC_MAP

from .base import Handler

__all__ = (
    'HandlerExceptionHandlerBase',
    'TradeHandlerBase',
    'AggTradeHandlerBase',
    'KlineHandlerBase',
    'MiniTickerHandlerBase',
    'TickerHandlerBase',
    'AllMarketMiniTickersHandlerBase',
    'AllMarketTickersHandlerBase'
)


class HandlerExceptionHandlerBase(Handler):
    def receive(self, e):
        traceback.print_exc()
        return e


BASE_TRADE_COLUMNS_MAP = {
    **STREAM_TYPE_MAP,
    'E': 'event_time',
    's': 'symbol',
    'p': 'price',
    'q': 'quantity',
    'T': 'trade_time',
    'm': 'is_maker'
}

TRADE_COLUMNS_MAP = {
    **BASE_TRADE_COLUMNS_MAP,
    't': 'trade_id',
    'b': 'buyer_order_id',
    'a': 'seller_order_id'
}

TRADE_COLUMNS = TRADE_COLUMNS_MAP.keys()


class TradeHandlerBase(Handler):
    COLUMNS_MAP = TRADE_COLUMNS_MAP
    COLUMNS = TRADE_COLUMNS


AGG_TRADE_COLUMNS_MAP = {
    **BASE_TRADE_COLUMNS_MAP,
    'a': 'agg_trade_id',
    'f': 'first_trade_id',
    'l': 'last_trade_id',
}

AGG_TRADE_COLUMNS = AGG_TRADE_COLUMNS_MAP


class AggTradeHandlerBase(Handler):
    COLUMNS_MAP = AGG_TRADE_COLUMNS_MAP
    COLUMNS = AGG_TRADE_COLUMNS


KLINE_COLUMNS_MAP = {
    **STREAM_TYPE_MAP,
    'E': 'event_time',
    't': 'open_time',
    'T': 'close_time',
    's': 'symbol',
    'i': 'interval',
    'f': 'first_trade_id',
    'L': 'last_trade_id',
    **STREAM_OHLC_MAP,
    'x': 'is_closed',
    'v': 'volume',
    'q': 'quote_volume',
    'V': 'taker_volume',
    'Q': 'taker_quote_volume',
    'n': 'total_trades'
}

KLINE_COLUMNS = KLINE_COLUMNS_MAP.keys()


class KlineHandlerBase(Handler):
    COLUMNS_MAP = KLINE_COLUMNS_MAP
    COLUMNS = KLINE_COLUMNS

    def _receive(self, payload):
        """The payload of kline has unnecessary hierarchy,
        so just flatten it.
        """

        k = payload['k']
        k['E'] = payload['E']

        return super()._receive(k)


MINI_TICKER_COLUMNS_MAP = {
    **STREAM_TYPE_MAP,
    'E': 'event_time',
    's': 'symbol',
    **STREAM_OHLC_MAP,
    'v': 'volume',
    'q': 'quote_volume',
}

MINI_TICKER_COLUMNS = MINI_TICKER_COLUMNS_MAP.keys()


class MiniTickerHandlerBase(Handler):
    COLUMNS_MAP = MINI_TICKER_COLUMNS_MAP
    COLUMNS = MINI_TICKER_COLUMNS


TICKER_COLUMNS_MAP = {
    **MINI_TICKER_COLUMNS_MAP,
    'p': 'price',
    'P': 'percent',
    'w': 'weighted_average_price',
    'x': 'first_trade_price',
    'Q': 'last_quantity',
    'b': 'best_bid_price',
    'B': 'best_bid_quantity',
    'O': 'stat_open_time',
    'C': 'stat_close_time',
    'F': 'first_trade_id',
    'L': 'last_trade_id',
    'n': 'total_trades'
}

TICKER_COLUMNS = TICKER_COLUMNS_MAP.keys()


class TickerHandlerBase(Handler):
    COLUMNS_MAP = TICKER_COLUMNS_MAP
    COLUMNS = TICKER_COLUMNS


class AllMarketMiniTickersHandlerBase(Handler):
    COLUMNS_MAP = MINI_TICKER_COLUMNS_MAP
    COLUMNS = MINI_TICKER_COLUMNS

    def _receive(self, payload):
        return super()._receive(
            payload, None)


class AllMarketTickersHandlerBase(Handler):
    COLUMNS_MAP = TICKER_COLUMNS_MAP
    COLUMNS = TICKER_COLUMNS

    def _receive(self, payload):
        return super()._receive(
            payload, None)
