from binance.handlers.handlers import (
    HandlerExceptionHandlerBase,
    KlineHandlerBase,
    TradeHandlerBase,
    AggTradeHandlerBase,
    MiniTickerHandlerBase,
    TickerHandlerBase,
    AllMarketMiniTickersHandlerBase,
    AllMarketTickersHandlerBase
)

from binance.handlers.orderbook_handler import OrderBookHandlerBase

from binance.common.constants import (
    SubType,
    KlineInterval,
    KLINE_TYPE_PREFIX,
    KEY_STREAM_TYPE,
    KEY_PAYLOAD
)
from binance.common.exceptions import InvalidSubTypeParamException
from binance.common.utils import normalize_symbol

from .base import Processor


class ExceptionProcessor(Processor):
    HANDLER = HandlerExceptionHandlerBase


class KlineProcessor(Processor):
    HANDLER = KlineHandlerBase
    SUB_TYPE = SubType.KLINE

    def subscribe_param(self, _, t, *args) -> str:
        symbol = self._get_param_symbol(t, args)

        length = len(args)

        if length == 2:
            interval = args[1]
        else:
            raise InvalidSubTypeParamException(
                t, 'interval', '`KlineInterval` enum expected but not specified')

        if not isinstance(interval, KlineInterval):
            raise InvalidSubTypeParamException(
                t, 'interval', '`KlineInterval` enum expected but got `%s`' % symbol)

        return f'{normalize_symbol(symbol)}@{KLINE_TYPE_PREFIX}{interval}'


class TradeProcessor(Processor):
    HANDLER = TradeHandlerBase
    SUB_TYPE = SubType.TRADE


class AggTradeProcessor(Processor):
    HANDLER = AggTradeHandlerBase
    SUB_TYPE = SubType.AGG_TRADE


class OrderBookProcessor(Processor):
    HANDLER = OrderBookHandlerBase
    SUB_TYPE = SubType.ORDER_BOOK
    PAYLOAD_TYPE = 'depthUpdate'


class MiniTickerProcessor(Processor):
    HANDLER = MiniTickerHandlerBase
    SUB_TYPE = SubType.MINI_TICKER
    PAYLOAD_TYPE = '24hrMiniTicker'


class TickerProcessor(Processor):
    HANDLER = TickerHandlerBase
    SUB_TYPE = SubType.TICKER
    PAYLOAD_TYPE = '24hrTicker'


class AllMarketMiniTickersProcessor(Processor):
    HANDLER = AllMarketMiniTickersHandlerBase
    SUB_TYPE = SubType.ALL_MARKET_MINI_TICKERS
    STREAM_TYPE_PREFIX = '!miniTicker@arr'

    def is_message_type(self, msg):
        stream_type = msg.get(KEY_STREAM_TYPE)

        if stream_type is None or \
                not stream_type.startswith(self.STREAM_TYPE_PREFIX):
            return False, None

        return True, msg.get(KEY_PAYLOAD)

    def subscribe_param(self, _, t, *args) -> str:
        if len(args) == 0:
            interval = 1000
        else:
            interval = args[0]

        return f'{self.STREAM_TYPE_PREFIX}@{interval}ms'


class AllMarketTickersProcessor(AllMarketMiniTickersProcessor):
    HANDLER = AllMarketTickersHandlerBase
    SUB_TYPE = SubType.ALL_MARKET_TICKERS
    STREAM_TYPE_PREFIX = '!ticker@arr'
