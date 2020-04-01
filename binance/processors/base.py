import asyncio
import inspect
from typing import (
    Optional
)

from binance.common.exceptions import (
    InvalidSubTypeParamException
)
from binance.common.utils import normalize_symbol
from binance.common.constants import (
    SubType,
    ATOM,
    KEY_PAYLOAD,
    KEY_PAYLOAD_TYPE
)
from binance.handlers.base import Handler


class Processor:
    # The handler class
    HANDLER: Handler

    # The payload['e'] of message
    PAYLOAD_TYPE = ATOM

    # subtype used by client.subscribe
    SUB_TYPE: Optional[SubType] = None

    def __init__(self, client):
        self._client = client

        self._handlers = set()

        if self.PAYLOAD_TYPE == ATOM and self.SUB_TYPE is not None:
            self.PAYLOAD_TYPE = self.SUB_TYPE.value

    def subscribe_param(self, subscribe, t, *args):
        if len(args) == 0:
            raise InvalidSubTypeParamException(
                t, 'symbol', 'string expected but not specified')

        symbol = args[0]

        if type(symbol) is not str:
            raise InvalidSubTypeParamException(
                t, 'symbol', 'string expected but got `%s`' % symbol)

        return f'{normalize_symbol(symbol)}@{t}'

    def is_handler_type(
        self,
        handler: Handler
    ) -> bool:
        return isinstance(handler, self.HANDLER)

    def is_message_type(self, msg):
        payload = msg.get(KEY_PAYLOAD)

        if payload is not None and \
                type(payload) is dict and \
                payload.get(KEY_PAYLOAD_TYPE) == self.PAYLOAD_TYPE:
            return True, payload

        return False, None

    def is_subtype(
        self,
        t: SubType
    ) -> bool:
        return t == self.SUB_TYPE

    def add_handler(
        self,
        handler: Handler
    ) -> None:
        if handler not in self._handlers:
            # set the client to handler
            handler.set_client(self._client)

            self._handlers.add(handler)

    async def dispatch(self, payload) -> None:
        coro = []

        for handler in self._handlers:
            ret = handler.receiveDispatch(payload)
            if inspect.iscoroutine(ret):
                coro.append(ret)

        if len(coro) > 0:
            await asyncio.gather(*coro)
