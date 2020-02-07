import asyncio

from .handlers import *
from binance.common.constants import RET_OK, RET_ERROR

KEY_PAYLOAD = 'data'
KEY_TYPE = 'e'

class HandlerContextBase(object):
    def __init__(self):
        self._handler_table = {}

    def set_handler(self, handler):
        """
        set the callback processing object to be used to handle websocket messages
        :param handler:the object in callback handler base
        :return: RET_ERROR or RET_OK
        """
        set_flag = False
        for stream_type in self.HANDLER_MAP:
            if isinstance(handler, self.HANDLER_MAP[stream_type]):
                self._handler_table[stream_type] = handler
                return RET_OK

        if set_flag is False:
            return RET_ERROR

    # TODO: more flexible filter
    async def receive(self, msg):
        """receive response callback function"""
        if KEY_PAYLOAD not in msg:
            return

        payload = msg[KEY_PAYLOAD]

        if KEY_TYPE not in payload:
            return

        payload_type = payload[KEY_TYPE]

        if payload_type not in self._handler_table:
            return

        handler = self._handler_table[payload_type]

        if asyncio.iscoroutinefunction(handler.receive):
            await handler.receive(payload)
        else:
            handler.receive(payload)

class HandlerContext(HandlerContextBase):
    HANDLER_MAP = {
        'trade': TradeHandlerBase,
        'aggTrade': AggTradeHandlerBase,
        'depthUpdate': OrderBookHandlerBase,
        '24hrMiniTicker': MiniTickerHandlerBase,
        '24hrTicker': TickerHandlerBase,
        'kline': KlineHandlerBase
    }

# class UserStreamHandlerContext(HandlerContextBase):
#     pass
