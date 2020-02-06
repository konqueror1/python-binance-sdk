from binance.common.utils import make_list, err_msg
from binance.common.constants import \
    RET_ERROR, RET_OK, \
    SUBTYPE_MAP

from .streams import DataStream

def get_subtype_list_str():
    return '\n'.join([
        '  - %s (SubType.%s)' % (x, SUBTYPE_MAP[x]) for x in SUBTYPE_MAP
    ])

def check_subscribe_params(symbols, subtype_list):
    symbols = make_list(symbols)
    subtype_list = make_list(subtype_list)

    if len(symbols) == 0:
        return RET_ERROR, err_msg('symbols is null'), symbols, subtype_list

    if len(subtype_list) == 0:
        return RET_ERROR, err_msg('subtype_list is null'), symbols, subtype_list

    for t in subtype_list:
        if t not in SUBTYPE_MAP:
            subtypes = get_subtype_list_str()
            msg = err_msg('invalid subtype `%s`. available subtypes are one of:\n%s', t, subtypes)
            return RET_ERROR, msg, symbols, subtype_list

    return RET_OK, None, symbols, subtype_list

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

        return self

    async def _receive(self, msg):
        if self._receiving:
            await self._handler_ctx.receive(msg)

    def _get_data_stream(self):
        if not self._data_stream:
            self._data_stream = DataStream(
                self._receive,
                self._stream_host,
                self._stream_retry_policy,
                self._stream_timeout
            ).connect()

        return self._data_stream

    # subscribe to the stream for symbols
    async def subscribe(self, symbols, subtype_list):
        code, msg, symbols, subtype_list = check_subscribe_params(
            symbols, subtype_list)

        if code != RET_OK:
            # todo
            raise

        stream = self._get_data_stream()

        return await stream.subscribe(symbols, subtype_list)

    def unsubscribe(self, symbols, sub_type_list):
        return self

    # subscribe to user streams
    def subscribe_user(sef):
        return self

    def unsubscribe_user(self):
        return self

    def handler(self, *handlers):
        for handler in handlers:
            self._handler_ctx.set_handler(handler)

        return self
