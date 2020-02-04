from .handlers import *
from binance.common.constants import RET_OK, RET_ERROR

__all__ = [
    'StreamHandlerContext',
    'UserStreamHandlerContext'
]

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
        for stream_type in self._handler_table:
            if isinstance(handler, self.HANDLER_MAP[stream_type]):
                self._handler_table[stream_type] = handler
                return RET_OK

        if set_flag is False:
            return RET_ERROR

    async def receive(self, response):
        """receive response callback function"""
        pass

class StreamHandlerContext(HandlerContextBase):
    HANDLER_MAP = {
        'aggTrade': AggTradeHandlerBase,
        'depthUpdate': DepthHandlerBase,
        '24hrMiniTicker': TickerHandlerBase
        'kline': KlineHandlerBase
    }

class UserStreamHandlerContext(HandlerContextBase):
    pass
