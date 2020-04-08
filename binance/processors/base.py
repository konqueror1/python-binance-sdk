import asyncio
import inspect
from typing import (
    Optional,
    Set,
    Awaitable
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
    HANDLER: type

    # The payload['e'] of message
    PAYLOAD_TYPE = ATOM

    # subtype used by client.subscribe
    SUB_TYPE: Optional[SubType] = None

    def __init__(self, client):
        self._client = client

        self._handlers = set()

        if self.PAYLOAD_TYPE == ATOM and self.SUB_TYPE is not None:
            self.PAYLOAD_TYPE = self.SUB_TYPE.value

    def supports_subtype(
        self,
        t: SubType
    ) -> bool:
        return t == self.SUB_TYPE

    # -----------------------------------------------

    def _get_param_symbol(self, t, args):
        if len(args) == 0:
            raise InvalidSubTypeParamException(
                t, 'symbol', 'string expected but not specified')

        symbol = args[0]

        if type(symbol) is not str:
            raise InvalidSubTypeParamException(
                t, 'symbol', 'string expected but got `%s`' % symbol)

        return symbol

    def subscribe_param(
        self,
        subscribe: bool,
        t: SubType,
        *args
    ) -> str:
        symbol = self._get_param_symbol(t, args)

        return f'{normalize_symbol(symbol)}@{t}'

    def supports_handler(
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

    def add_handler(
        self,
        handler: Handler
    ) -> None:
        if handler not in self._handlers:
            # set the client to handler
            handler.set_client(self._client)

            self._handlers.add(handler)

    def dispatch(
        self,
        payload
    ) -> Awaitable[None]:
        return self._dispatch(payload, self._handlers)

    async def _dispatch(
        self,
        payload,
        handlers: Set[Handler]
    ):
        coro = []

        for handler in handlers:
            ret = handler.receiveDispatch(payload)
            if inspect.iscoroutine(ret):
                coro.append(ret)

        if len(coro) > 0:
            await asyncio.gather(*coro)
