from typing import (
    List,
    Tuple,
    Optional
)

from binance.common.constants import DEFAULT_STREAM_CLOSE_CODE
from binance.common.exceptions import InvalidHandlerException

from .stream import Stream
from .handler_context import HandlerContext

# pylint: disable=no-member


class SubscriptionManager:
    _data_stream: Optional[Stream]

    def start(self):
        """Starts receiving messages.

        By calling this method, the client will not actually start the stream connection.

        Returns:
            self
        """

        self._receiving = True
        return self

    def stop(self):
        """Stops receiving messages.

        By calling this method, the client only ignores all incomming stream message, and will not close the stream connection.

        Returns:
            self
        """

        self._receiving = False
        return self

    async def close(
        self,
        code: int = DEFAULT_STREAM_CLOSE_CODE
    ) -> None:
        """Closes stream connection, clear all stream subscriptions and clear all handlers.

        Args:
            code (:obj:`int`, optional): the close code for python library websockets. Defaults to 4999, and it should be in the range 4000 - 4999
        """

        self._receiving = False

        if self._data_stream:
            await self._data_stream.close(code)
            self._data_stream = None

        self._handler_ctx = None

    async def _receive(self, msg) -> None:
        if self._receiving:
            await self._handler_ctx.receive(msg)

    def _get_handler_ctx(self) -> HandlerContext:
        if not self._handler_ctx:
            self._handler_ctx = HandlerContext(self)

        return self._handler_ctx

    def _get_data_stream(self) -> Stream:
        if self._data_stream is None:
            self._data_stream = Stream(
                self._stream_host + '/stream',  # type: ignore
                self._receive,
                **self._stream_kwargs  # type: ignore
            )
            self._data_stream.connect()

        return self._data_stream

    # subscribe to the stream for symbols
    async def _subscribe(
        self,
        subscribe: bool,
        args: Tuple[str]
    ):
        params = await self._get_handler_ctx().subscribe_params(
            subscribe, *args)

        stream = self._get_data_stream()

        if subscribe:
            return await stream.subscribe(params)
        else:
            return await stream.unsubscribe(params)

    async def subscribe(self, *args):
        return await self._subscribe(True, args)

    async def unsubscribe(self, *args):
        return await self._subscribe(False, args)

    async def list_subscriptions(self) -> List[str]:
        return await self._get_data_stream().list_subscriptions()

    def handler(self, *handlers):
        """Sets the callback processing object to be used to handle websocket messages.

        Args:
            *handlers (HandlerBase):

        Returns:
            self
        """

        ctx = self._get_handler_ctx()

        for handler in handlers:
            if not ctx.set_handler(handler):
                raise InvalidHandlerException(handler)

        return self
