import asyncio

from .handlers import *
from binance.common.constants import SubType, KLINE_SUBTYPE_LIST, \
    KEY_PAYLOAD, KEY_PAYLOAD_TYPE, KEY_STREAM_TYPE, ATOM

from binance.common.utils import normalize_symbol
from binance.common.exceptions import InvalidSubTypeParamException

class ProcessorBase(object):
    # The handler class
    HANDLER = None

    # The payload['e'] of message
    PAYLOAD_TYPE = ATOM

    # subtype used by client.subscribe
    SUB_TYPE = None

    def __init__(self, client):
        self._client = client

        self._handlers = set()
        self.PAYLOAD_TYPE = self.PAYLOAD_TYPE \
            if self.PAYLOAD_TYPE != ATOM else self.SUB_TYPE

    def subscribe_param(self, subscribe, t, *args):
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

        if payload != None and \
            getattr(payload, KEY_PAYLOAD_TYPE, None) == self.PAYLOAD_TYPE:
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

# class UserProcessor(ProcessorBase):
#     HANDLER = UserHandlerBase
#     SUB_TYPE = SubType.USER

#     KEEP_ALIVE_INTERVAL = 60 * 30

#     def __init__(self, *args):
#         super(UserProcessor, self).__init__(self, *args)

#         self._listen_key = None
#         self._keep_alive_task = None

#     async def subscribe_param(self, subscribe, t):
#         if subscribe == False:
#             key = self._listen_key
#             self._listen_key = None
#             return key

#         key = await self._client.get_user_listen_key()

#         self._listen_key = key
#         self._start_keep_alive()

#         return key

#     async def _keep_alive(self):
#         while True:
#             await asyncio.sleep(self.KEEP_ALIVE_INTERVAL)
#             if self._listen_key:
#                 await self._client.keepalive_listen_key(self._listen_key)

#     def _start_keep_alive(self):
#         self._stop_keep_alive()
#         self._keep_alive_task = asyncio.create_task(self._keep_alive())

#     def _stop_keep_alive(self):
#         if self._keep_alive_task:
#             self._keep_alive_task.cancel()
#             self._keep_alive_task = None

#     async def close_stream(self):
#         self._stop_keep_alive()
#         await self._client.close_listen_key(self._listen_key)

PROCESSORS = [
    KlineProcessor,
    TradeProcessor,
    AggTradeProcessor,
    OrderBookProcessor,
    MiniTickerProcessor,
    TickerProcessor,
    AllMarketMiniTickersProcessor,
    AllMarketTickersProcessor,
    # UserProcessor
]
