import asyncio

from .processors import PROCESSORS, ProcessorBase
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
            if processor.is_handler_type(handler):
                processor.add_handler(handler)
                return RET_OK

        if set_flag is False:
            return RET_ERROR

    # client.subscribe(subtype_needs_no_param_or_has_default_param)
    # client.subscribe(subtype, param)
    # client.subscribe(subtypes, params)
    # client.subscribe((subtype, param), *subtype_param_pairs)
    async def subscribe_params(self, *args):
        subs = args if type(args[0]) is tuple else (args)

        for subtype_param in subs:
            pass

    def register_processor(self, processor):
        if isinstance(processor, ProcessorBase):
            self._processors.append(processor)

    async def receive(self, msg):
        """receive response callback function"""
        for processor in self._processors:
            is_payload, payload = processor.is_message_type(msg)
            if is_payload:
                return await processor.dispatch(payload)

# class UserStreamHandlerContext(HandlerContextBase):
#     pass
