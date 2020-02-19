from binance.common.constants import RET_OK, DEFAULT_STREAM_CLOSE_CODE
from binance.common.exceptions import InvalidHandlerException

from .stream import Stream
from .handler_context import HandlerContext

class SubscriptionManager(object):
    def start(self):
        self._receiving = True
        return self

    def stop(self):
        self._receiving = False
        return self

    async def close(self, code=DEFAULT_STREAM_CLOSE_CODE):
        self._receiving = False

        if self._data_stream:
            await self._data_stream.close(code)
            self._data_stream = None

        self._handler_ctx = None

    async def _receive(self, msg):
        if self._receiving:
            await self._handler_ctx.receive(msg)

    def _get_handler_ctx(self):
        if not self._handler_ctx:
            self._handler_ctx = HandlerContext(self)

        return self._handler_ctx

    def _get_data_stream(self):
        if not self._data_stream:
            self._data_stream = Stream(
                self._stream_host + '/stream',
                self._receive,
                **self._stream_kwargs
            ).connect()

        return self._data_stream

    # subscribe to the stream for symbols
    async def _subscribe(self, subscribe, args):
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

    async def list_subscriptions(self):
        return await self._get_data_stream().list_subscriptions()

    def handler(self, *handlers):
        """
        set the callback processing object to be used to handle websocket messages
        :param handler:the object in callback handler base
        :return: RET_ERROR or RET_OK
        """

        ctx = self._get_handler_ctx()

        for handler in handlers:
            ret = ctx.set_handler(handler)

            if ret != RET_OK:
                raise InvalidHandlerException(handler)

        return self
