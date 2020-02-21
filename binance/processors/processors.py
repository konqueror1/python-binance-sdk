import asyncio

from binance.handlers import *
from binance.common.constants import (
    SubType,
    KLINE_TYPE_PREFIX, KLINE_INTERVAL_VALUE_LIST,
    KEY_STREAM_TYPE, KEY_PAYLOAD
)
from binance.common.exceptions import InvalidSubTypeParamException
from binance.common.utils import normalize_symbol

from .base import ProcessorBase

class ExceptionProcessor(ProcessorBase):
    HANDLER = HandlerExceptionHandlerBase

class KlineProcessor(ProcessorBase):
    HANDLER = KlineHandlerBase
    SUB_TYPE = SubType.KLINE

    def subscribe_param(self, subscribe, t, *args):
        length = len(args)

        if length == 2:
            symbol, interval = args
        else:
            raise InvalidSubTypeParamException(
                t, 'interval', 'string expected but not specified')

        if type(symbol) is not str:
            raise InvalidSubTypeParamException(
                t, 'symbol', 'string expected but got `%s`' % symbol)

        if interval not in KLINE_INTERVAL_VALUE_LIST:
            raise InvalidSubTypeParamException(
                t, 'interval', '`KlineInterval` enum expected but got `%s`' % symbol)

        return normalize_symbol(symbol) + '@' + KLINE_TYPE_PREFIX + interval

class TradeProcessor(ProcessorBase):
    HANDLER = TradeHandlerBase
    SUB_TYPE = SubType.TRADE

class AggTradeProcessor(ProcessorBase):
    HANDLER = AggTradeHandlerBase
    SUB_TYPE = SubType.AGG_TRADE

class OrderBookProcessor(ProcessorBase):
    HANDLER = OrderBookHandlerBase
    SUB_TYPE = SubType.ORDER_BOOK
    PAYLOAD_TYPE = 'depthUpdate'

class MiniTickerProcessor(ProcessorBase):
    HANDLER = MiniTickerHandlerBase
    SUB_TYPE = SubType.MINI_TICKER
    PAYLOAD_TYPE = '24hrMiniTicker'

class TickerProcessor(ProcessorBase):
    HANDLER = TickerHandlerBase
    SUB_TYPE = SubType.TICKER
    PAYLOAD_TYPE = '24hrTicker'

class AllMarketMiniTickersProcessor(ProcessorBase):
    HANDLER = AllMarketMiniTickersHandlerBase
    SUB_TYPE = SubType.ALL_MARKET_MINI_TICKERS
    STREAM_TYPE_PREFIX = '!miniTicker@arr'

    def is_message_type(self, msg):
        stream_type = msg.get(KEY_STREAM_TYPE)
        if stream_type == None or \
            stream_type.startswith(self.STREAM_TYPE_PREFIX) == False:
            return False, None

        return True, msg.get(KEY_PAYLOAD)

    def subscribe_param(self, subscribe, t, *args):
        if len(args) == 0:
            interval = 1000
        else:
            interval = args[0]

        return self.STREAM_TYPE_PREFIX + '@%sms' % interval

class AllMarketTickersProcessor(AllMarketMiniTickersProcessor):
    HANDLER = AllMarketTickersHandlerBase
    SUB_TYPE = SubType.ALL_MARKET_TICKERS
    STREAM_TYPE_PREFIX = '!ticker@arr'
