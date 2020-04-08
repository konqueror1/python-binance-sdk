import asyncio
from typing import (
    Optional
)

from binance.common.constants import (
    SubType,
    KEY_PAYLOAD,
    KEY_PAYLOAD_TYPE
)

from binance.common.exceptions import UserStreamNotSubscribedException

from binance.handlers.user_handlers import (
    AccountInfoHandlerBase,
    AccountPositionHandlerBase,
    BalanceUpdateHandlerBase,
    OrderUpdateHandlerBase,
    OrderListStatusHandlerBase
)

from binance.handlers.base import Handler

from .base import Processor


class UserProcessor(Processor):
    _listen_key: Optional[str]

    SUB_TYPE = SubType.USER

    KEEP_ALIVE_INTERVAL = 60 * 30

    PAYLOAD_TYPES = (
        'outboundAccountInfo',
        'outboundAccountPosition',
        'balanceUpdate',
        'executionReport',
        'listStatus'
    )

    HANDLERS = (
        AccountInfoHandlerBase,
        AccountPositionHandlerBase,
        BalanceUpdateHandlerBase,
        OrderUpdateHandlerBase,
        OrderListStatusHandlerBase
    )

    def __init__(self, *args) -> None:
        super().__init__(*args)

        self._listen_key = None
        self._keep_alive_task = None

        self._handlers = {}

    async def subscribe_param(
        self,
        subscribe: bool,
        t: SubType
    ) -> str:
        if not subscribe:
            key = self._listen_key

            if key is None:
                raise UserStreamNotSubscribedException()

            await self._close_stream()
            self._listen_key = None

            return key

        key = await self._client.get_listen_key()

        self._listen_key = key
        self._start_keep_alive()

        return key

    async def _keep_alive(self) -> None:
        # Send a keepalive requests every 30 minutes
        while True:
            await asyncio.sleep(self.KEEP_ALIVE_INTERVAL)
            if self._listen_key is not None:
                await self._client.keepalive_listen_key(self._listen_key)

    def _start_keep_alive(self) -> None:
        self._stop_keep_alive()
        self._keep_alive_task = asyncio.create_task(self._keep_alive())

    def _stop_keep_alive(self) -> None:
        if self._keep_alive_task:
            self._keep_alive_task.cancel()
            self._keep_alive_task = None

    async def _close_stream(self) -> None:
        self._stop_keep_alive()
        await self._client.close_listen_key(self._listen_key)

    def is_message_type(self, msg):
        payload = msg.get(KEY_PAYLOAD)

        if payload is not None and \
                type(payload) is dict and \
                payload.get(KEY_PAYLOAD_TYPE) in self.PAYLOAD_TYPES:
            return True, payload

        return False, None

    def supports_handler(
        self,
        handler: Handler
    ) -> bool:
        return isinstance(handler, self.HANDLERS)

    def add_handler(
        self,
        handler: Handler
    ) -> None:
        for i, HandlerBase in enumerate(self.HANDLERS):
            if isinstance(handler, HandlerBase):
                payload_type = self.PAYLOAD_TYPES[i]

                self._add_handler(payload_type, handler)

    def _add_handler(
        self,
        payload_type,
        handler
    ) -> None:
        handlers = self._handlers.get(payload_type)

        if handlers is None:
            handlers = set()
            self._handlers[payload_type] = handlers

        if handler not in handlers:
            # set the client to handler
            handler.set_client(self._client)

            handlers.add(handler)

    async def dispatch(self, payload) -> None:
        payload_type = payload.get(KEY_PAYLOAD_TYPE)
        handlers = self._handlers.get(payload_type)

        if handlers is None:
            return

        await self._dispatch(payload, handlers)
