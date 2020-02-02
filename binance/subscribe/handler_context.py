from .handlers import *
from binance.common.constants import RET_OK, RET_ERROR

__all__ = [
    'TradeHandlerContext',
    'KlineHandlerContext'
]

class HandlerContextBase(object):
    def __init__(self):
        self._handler_table = {}

    def set_handler(self, handler):
        """
        set the callback processing object to be used by the receiving thread after receiving the data.User should set
        their own callback object setting in order to achieve event driven.
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

class TradeHandlerContext(HandlerContextBase):
    HANDLER_MAP = {
        'aggTrade': AggTradeHandlerBase,
        'depthUpdate': DepthHandlerBase,
        '24hrMiniTicker': TickerHandlerBase
    }

class KlineHandlerContext(HandlerContextBase):
    HANDLER_MAP = {
        'kline': KlineHandlerBase
    }
