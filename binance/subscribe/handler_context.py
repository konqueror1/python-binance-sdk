import asyncio

from .processors import PROCESSORS
from binance.common.constants import RET_OK, RET_ERROR

KEY_PAYLOAD = 'data'
KEY_TYPE = 'e'

class HandlerContext(object):
    PROCESSORS = PROCESSORS

    def __init__(self):
        self._handler_table = {}
        self._processors = [Factory() for Factory in self.PROCESSORS]

    def set_handler(self, handler):
        """
        set the callback processing object to be used to handle websocket messages
        :param handler:the object in callback handler base
        :return: RET_ERROR or RET_OK
        """
        set_flag = False
        for processor in self._processors:
            if processor.isHandlerType(handler):
                processor.add_handler(handler)
                return RET_OK

        if set_flag is False:
            return RET_ERROR

    # client.subscribe(SubType.Ticker, )
    def subscribe_params(self, *args):
        subs = args if type(args[0]) is tuple else (args)

    async def receive(self, msg):
        """receive response callback function"""
        for processor in self._processors:
            is_payload, payload = processor.isMessageType(msg)
            if is_payload:
                return await processor.dispatch(payload)

# class UserStreamHandlerContext(HandlerContextBase):
#     pass
