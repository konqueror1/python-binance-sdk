import asyncio

from binance.common.constants import STREAM_TYPE_MAP, DEFAULT_DEPTH_LIMIT
from binance.common.utils import normalize_symbol, wrap_coroutine

from .base import HandlerBase, pd
from .orderbook import OrderBook, \
    KEY_FIRST_UPDATE_ID, KEY_LAST_UPDATE_ID, KEY_BIDS, KEY_ASKS

KEY_SYMBOL = 's'

ORDER_BOOK_COLUMNS_MAP = {
    **STREAM_TYPE_MAP,
    'E': 'event_time',
    KEY_SYMBOL: 'symbol',
    KEY_FIRST_UPDATE_ID: 'first_update_id',
    KEY_LAST_UPDATE_ID: 'last_update_id'
}

ORDER_BOOK_COLUMNS = ORDER_BOOK_COLUMNS_MAP.keys()

def create_depth_df(l):
    return pd.DataFrame([
        {'price': x[0], 'quantity': x[1]} for x in l
    ])

class OrderBookHandlerBase(HandlerBase):
    COLUMNS_MAP = ORDER_BOOK_COLUMNS_MAP
    COLUMNS = ORDER_BOOK_COLUMNS

    def __init__(self, limit=DEFAULT_DEPTH_LIMIT):
        super().__init__()

        self._limit = limit
        self._orderbooks = {}

        self._uninit_orderbooks = []

    def _receive(self, payload):
        info = super()._receive(payload)

        bids = create_depth_df(payload[KEY_BIDS])
        asks = create_depth_df(payload[KEY_ASKS])

        return info, [bids, asks]

    def orderbook(self, symbol):
        symbol = normalize_symbol(symbol)

        if symbol in self._orderbooks:
            return self._orderbooks[symbol]

        orderbook = OrderBook(symbol, limit=self._limit)

        if self._client:
            orderbook.set_client(self._client)
        else:
            self._uninit_orderbooks.append(orderbook)

        self._orderbooks[symbol] = orderbook

        return orderbook

    def set_client(self, client):
        super().set_client(client)

        if len(self._uninit_orderbooks) == 0:
            return

        for orderbook in self._uninit_orderbooks:
            orderbook.set_client(client)

        self._uninit_orderbooks.clear()

    async def receiveDispatch(self, payload):
        self.orderbook(payload[KEY_SYMBOL]).update(payload)
        await wrap_coroutine(self.receive(payload))
