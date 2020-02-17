import asyncio

from binance.common.sequenced_list import SequencedList

KEY_FIRST_UPDATE_ID = 'U'
KEY_LAST_UPDATE_ID = 'u'

KEY_REST_LAST_UPDATE_ID = 'lastUpdateId'
KEY_REST_BIDS = 'bids'
KEY_REST_ASKS = 'asks'

KEY_BIDS = 'b'
KEY_ASKS = 'a'

class OrderBook(object):
    def __init__(self, symbol, limit):
        self.asks = SequencedList()
        self.bids = SequencedList()

        self._symbol = symbol
        self._limit = limit
        self._client = None

        self._last_update_id = 0
        # The queue to save messages that are not continuous
        self._unsolved_queue = []

        # Whether we are still fetching the depth snapshot
        self._fetching = True

    # Whether the orderbook is updated
    @property
    def updated(self):
        return not self._fetching

    def set_client(self, client):
        self._client = client

    async def _fetch(self):
        snapshot = await self._client.get_order_book(
            symbol=self._symbol,
            limit=self._limit
        )

        self.asks.clear()
        self.bids.clear()

        self._merge(
            snapshot[KEY_REST_LAST_UPDATE_ID],
            snapshot[KEY_REST_ASKS],
            snapshot[KEY_REST_BIDS]
        )

        self._fetching = False

        if len(self._unsolved_queue) == 0:
            return

        counter = 0
        for payload in self._unsolved_queue:
            updated = self.update(payload, False)

            if not updated:
                del self._unsolved_queue[:counter]
                self._start_fetching()
                return

            counter += 1

        self._unsolved_queue.clear()


    def _start_fetching(self):
        self._fetching = True
        asyncio.create_task(self._fetch())

    def _merge(self, last_update_id, asks, bids):
        self._last_update_id = last_update_id
        self.asks.merge(asks)
        self.bids.merge(bids)

    # Returns whether the payload is updated
    def update(self, payload, fetch_if_gap=True):
        if self._fetching:
            # If fetching is not completed, we should not merge orderbook
            self._unsolved_queue.append(payload)
            return False

        first = payload[KEY_FIRST_UPDATE_ID]
        last = payload[KEY_LAST_UPDATE_ID]
        current_last = self._last_update_id

        if last <= current_last:
            # abandon the payload
            return True

        if first <= self._last_update_id + 1:
            # It is ok
            self._merge(last, payload[KEY_ASKS], payload[KEY_BIDS])
            return True

        # else: Gap found

        if fetch_if_gap:
            self._unsolved_queue.append(payload)
            self._start_fetching()

        return False
