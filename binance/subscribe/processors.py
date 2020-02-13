import asyncio

from .handlers import *
from binance.common.constants import SubType, KLINE_SUBTYPE_LIST, \
    KEY_PAYLOAD, KEY_TYPE, ATOM

from binance.common.utils import normalize_symbol
from binance.common.exceptions import InvalidSubTypeParamException

class ProcessorBase(object):
    # The handler class
    HANDLER = None

    # The payload['e'] of message
    PAYLOAD_TYPE = ATOM

    # subtype used by client.subscribe
    SUB_TYPE = None

    def __init__(self):
        self._handlers = set()
        # self._client = client
        self.PAYLOAD_TYPE = self.PAYLOAD_TYPE \
            if self.PAYLOAD_TYPE != ATOM else self.SUB_TYPE

    def subscribe_param(self, t, *args):
        if len(args) == 0:
            raise InvalidSubTypeParamException(
                t, 'symbol', 'string expected but not specified')

        symbol = args[0]

        if type(symbol) is not str:
            raise InvalidSubTypeParamException(
                t, 'symbol', 'string expected but got `%s`' % symbol)

        return normalize_symbol(symbol) + '@' + t

    def is_handler_type(self, handler):
        return isinstance(handler, self.HANDLER)

    def is_message_type(self, msg):
        payload = msg.get(KEY_PAYLOAD)

        if payload != None and payload.get(KEY_TYPE) == self.PAYLOAD_TYPE:
            return True, payload

        return False, None

    def is_subtype(self, t):
        return t == self.SUB_TYPE

    def add_handler(self, handler):
        self._handlers.add(handler)

    async def dispatch(self, payload):
        coro = []

        for handler in self._handlers:
            if asyncio.iscoroutinefunction(handler.receive):
                coro.append(handler.receive(payload))
            else:
                handler.receive(payload)

        if len(coro) > 0:
            await asyncio.gather(*coro)

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

# class AllMarketMiniTickerProcessor(object):
#     HANDLER = AllMarketMiniTickerHandlerBase
#     SubType = SubType.ALL_MARKET_MINI_TICKERS

#     def key(self, t, ):

PROCESSORS = [
    KlineProcessor,
    TradeProcessor,
    AggTradeProcessor,
    OrderBookProcessor,
    MiniTickerProcessor,
    TickerProcessor
]
