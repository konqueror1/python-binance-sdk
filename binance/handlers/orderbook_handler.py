from binance.common.constants import STREAM_TYPE_MAP
from binance.common.sequenced_list import SequencedList

from .base import HandlerBase, pd

ORDER_BOOK_COLUMNS_MAP = {
    **STREAM_TYPE_MAP,
    'E': 'event_time',
    's': 'symbol',
    'U': 'first_update_id',
    'u': 'last_update_id'
}

ORDER_BOOK_COLUMNS = ORDER_BOOK_COLUMNS_MAP.keys()

def create_depth_df(l):
    return pd.DataFrame([
        {'price': x[0], 'quantity': x[1]} for x in l
    ])

class OrderBook(object):
    def __init__(self):
        self._asks = SequencedList()
        self._bids = SequencedList()

METHOD_NAME = 'receiveRaw'

class OrderBookHandlerBase(HandlerBase):
    COLUMNS_MAP = ORDER_BOOK_COLUMNS_MAP
    COLUMNS = ORDER_BOOK_COLUMNS

    def _receive(self, res):
        info = super()._receive(res)

        bids = create_depth_df(res['b'])
        asks = create_depth_df(res['a'])

        return info, [bids, asks]

    async def receiveDispatch(self, payload):
        return
