from threading import Thread
from time import sleep

from binance.common.utils import make_list, err_msg
from binance.common.constants import \
    RET_ERROR, RET_OK, \
    SUBTYPE_MAP

def check_subcribe_params(symbols, subtype_list):
    symbols = make_list(symbols)
    subtype_list = make_list(symbols)

    if len(symbols) == 0:
        return RET_ERROR, err_msg('symbols is null'), symbols, subtype_list

    if len(subtype_list) == 0:
        return RET_ERROR, err_msg('subtype_list is null'), symbols, subtype_list

    for t in sub_type_list:
        if t not in SUBTYPE_MAP:
            subtypes = '\n'.join(['  - ' + x for x in SUBTYPE_MAP])
            msg = err_msg('invalid subtype `%s`. available subtypes are one of:\n')
            return RET_ERROR, msg, symbols, subtype_list

    return RET_OK, None, symbols, subtype_list

class SubscriptionManager(object):
    def start(self):
        self._receiving = True

        if self._hanging:
            return

        self._hanging = True
        self._hang()

    def stop(self):
        self._receiving = False

    def close(self):
        self._hanging = False

    # subscribe to the stream for symbols
    def subscribe(self, symbols, subtype_list):
        code, msg, symbols, subtype_list = check_subcribe_params(
            symbols, subtype_list)

        if code != RET_OK:
            return code, msg

        return RET_OK, None

    def unsubscribe(self, symbols, sub_type_list):
        pass

    # subscribe to user streams
    def subscribe_user(sef):
        pass

    def unsubscribe_user(self):
        pass

    def set_handler(self, handler):
        self._handler_ctx.set_handler(handler)

    def _hang_loop(self):
        while self._hang_signal:
            sleep(1)
        self._hanging = False

    def _hang(self):
        with self._hang_lock:
            thread = Tread(target=self._hang_loop)
            thread.start()
