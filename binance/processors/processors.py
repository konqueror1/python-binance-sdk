import asyncio

from binance.handlers import *
from binance.common.constants import (
    SubType,
    KLINE_SUBTYPE_LIST, KEY_STREAM_TYPE, KEY_PAYLOAD
)

from .base import ProcessorBase

class ExceptionProcessor(ProcessorBase):
    HANDLER = HandlerExceptionHandlerBase

class KlineProcessor(ProcessorBase):
    HANDLER = KlineHandlerBase
    PAYLOAD_TYPE = 'kline'

    def is_subtype(self, t):
        return t in KLINE_SUBTYPE_LIST

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
