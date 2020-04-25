from aioretry import RetryPolicy

from binance.common.constants import (
    STREAM_TYPE_MAP,
    DEFAULT_DEPTH_LIMIT,
    DEFAULT_RETRY_POLICY
)

from binance.common.utils import (
    normalize_symbol,
    wrap_coroutine
)

from binance.common.types import DictPayload

from .base import (
    Handler,
    pd
)

from .orderbook import (
    OrderBook,
    KEY_FIRST_UPDATE_ID,
    KEY_LAST_UPDATE_ID,
    KEY_BIDS,
    KEY_ASKS
)

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


METHOD_NAME_RECEIVE = 'receive'


class OrderBookHandlerBase(Handler):
    COLUMNS_MAP = ORDER_BOOK_COLUMNS_MAP
    COLUMNS = ORDER_BOOK_COLUMNS

    def __init__(
        self,
        limit: int = DEFAULT_DEPTH_LIMIT,
        retry_policy: RetryPolicy = DEFAULT_RETRY_POLICY
    ) -> None:
        super().__init__()

        self._limit = limit
        self._retry_policy = retry_policy

        self._orderbooks = {}

        self._uninit_orderbooks = []

        # If the current class has no `receive` method,
        #   the raw payload will not be dispatched to self.receive
        self._has_receive = hasattr(self.__class__, METHOD_NAME_RECEIVE)

    def _receive(
        self,
        payload: DictPayload
    ):
        info = super()._receive(payload)

        bids = create_depth_df(payload[KEY_BIDS])
        asks = create_depth_df(payload[KEY_ASKS])

        return info, [bids, asks]

    def orderbook(
        self,
        symbol: str
    ) -> OrderBook:
        """Gets the orderbook for a certain symbol. If you get a certain orderbook, don't forget to subscribe to the orderbook stream of `symbol`::

            await client.subscribe(SubType.ORDER_BOOK, 'BTCUSDT')

        Args:
            symbol (str): The symbol name.

        Returns:
            OrderBook: The orderbook.
        """
        symbol = normalize_symbol(symbol)

        if symbol in self._orderbooks:
            return self._orderbooks[symbol]

        orderbook = OrderBook(symbol,
                              limit=self._limit,
                              retry_policy=self._retry_policy
                              )

        if self._client:
            orderbook.set_client(self._client)
        else:
            self._uninit_orderbooks.append(orderbook)

        self._orderbooks[symbol] = orderbook

        return orderbook

    def set_client(
        self,
        client
    ) -> None:
        """Sets the client for the orderbook. Most usually, you should not call this method directly. This method is invoked by `OrderBookHandlerBase` internally.

        Args:
            client (Client): the client instance of binance sdk
        """
        super().set_client(client)

        if len(self._uninit_orderbooks) == 0:
            return

        for orderbook in self._uninit_orderbooks:
            orderbook.set_client(client)

        self._uninit_orderbooks.clear()

    async def receiveDispatch(self, payload) -> None:
        """Receives a `depthUpdate` stream message. Most usually, you should not call this method directly. This method is invoked by `OrderBookHandlerBase` internally.

        Args:
            payload: the message payload of the stream
        """
        self.orderbook(payload[KEY_SYMBOL]).update(payload)

        if self._has_receive:
            await wrap_coroutine(self.receive(payload))
