from binance.common.utils import make_list, err_msg
from binance.common.constants import \
    RET_ERROR, RET_OK, \
    SUBTYPE_MAP
from binance.common.exceptions import InvalidSubParamsException

from .streams import Stream
from .handler_context import HandlerContext

# def get_subtype_list_str():
#     return '\n'.join([
#         '  - %s (SubType.%s)' % (x, SUBTYPE_MAP[x]) for x in SUBTYPE_MAP
#     ])

# def check_subscribe_params(symbols, subtype_list):
#     symbols = make_list(symbols)
#     subtype_list = make_list(subtype_list)

#     if len(symbols) == 0:
#         return RET_ERROR, err_msg('symbols is null'), symbols, subtype_list

#     if len(subtype_list) == 0:
#         return RET_ERROR, err_msg('subtype_list is null'), symbols, subtype_list

#     for t in subtype_list:
#         if t not in SUBTYPE_MAP:
#             subtypes = get_subtype_list_str()
#             msg = err_msg('invalid subtype `%s`. available subtypes are one of:\n%s', t, subtypes)
#             return RET_ERROR, msg, symbols, subtype_list

#     return RET_OK, None, symbols, subtype_list

class SubscriptionManager(object):
    def start(self):
        self._receiving = True
        return self

    def stop(self):
        self._receiving = False

        return self

    def close(self):
        if self._data_stream:
            self._data_stream.close()
            self._data_stream = None

        self._handler_ctx = None

        return self

    async def _receive(self, msg):
        if self._receiving:
            try:
                await self._handler_ctx.receive(msg)
            except Exception as e:
                print(e)

    def _get_handler_ctx(self):
        if not self._handler_ctx:
            self._handler_ctx = HandlerContext(self)

        return self._handler_ctx

    def _get_data_stream(self):
        if not self._data_stream:
            self._data_stream = Stream(
                self._receive,
                self._stream_host,
                self._stream_retry_policy,
                self._stream_timeout
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
        ctx = self._get_handler_ctx()

        for handler in handlers:
            ctx.set_handler(handler)

        return self
