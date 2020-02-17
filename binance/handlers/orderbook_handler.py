import asyncio

from binance.common.constants import STREAM_TYPE_MAP
from binance.common.sequenced_list import SequencedList
from binance.common.utils import normalize_symbol, wrap_coroutine

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
    def __init__(self, symbol):
        self.asks = SequencedList()
        self.bids = SequencedList()

        self._symbol = symbol
        self._client = None

        self._first_update_id = - 1
        self._last_update_id = - 1
        self._update_callbacks = []
        # The queue to save messages that are not continuous
        self._unsolved_queue = []

    def set_client(self, client):
        self._client = client

    def update(self, payload):
        return False

    def once_updated(self, callback):
        self._update_callbacks.append(callback)

METHOD_RECEIVE_RAW = 'receiveRaw'

class OrderBookHandlerBase(HandlerBase):
    COLUMNS_MAP = ORDER_BOOK_COLUMNS_MAP
    COLUMNS = ORDER_BOOK_COLUMNS

    def __init__(self):
        super().__init__()

        self._orderbooks = {}
        self._uninit_orderbooks = []
        self._has_raw_receive = getattr(self, METHOD_RECEIVE_RAW, None) != None

    def _receive(self, payload):
        info = super()._receive(payload)

        bids = create_depth_df(payload['b'])
        asks = create_depth_df(payload['a'])

        return info, [bids, asks]

    def orderbook(self, symbol):
        symbol = normalize_symbol(symbol)

        if symbol in self._orderbooks:
            return self._orderbooks[symbol]

        orderbook = OrderBook(symbol)

        if self._client:
            orderbook.set_client(self._client)
        else:
            self._uninit_orderbooks.append(orderbook)

        self._orderbooks[symbol] = orderbook

        return orderbook

    async def receiveDispatch(self, payload):
        tasks = []

        # Only dispatch raw payload if the handler has method `receiveRaw`
        if self._has_raw_receive:
            tasks.append(
                wrap_coroutine(self.receiveRaw(payload))
            )

        orderbook = self.orderbook(payload['s'])

        updated = orderbook.update(payload)

        if updated:
            # If the payload is updated, then just dispatch the payload
            tasks.append(
                wrap_coroutine(self.receive(payload))
            )
        else:
            # or delay the dispatch to orderbook callbacks
            orderbook.once_updated(self.receive)

        if len(tasks) == 0:
            return

        await asyncio.gather(*tasks)
