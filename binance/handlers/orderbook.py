import asyncio

from binance.common.sequenced_list import SequencedList
from binance.common.constants import DEFAULT_DEPTH_LIMIT, DEFAULT_RETRY_POLICY
from binance.common.utils import wrap_coroutine, normalize_symbol

KEY_FIRST_UPDATE_ID = 'U'
KEY_LAST_UPDATE_ID = 'u'

KEY_REST_LAST_UPDATE_ID = 'lastUpdateId'
KEY_REST_BIDS = 'bids'
KEY_REST_ASKS = 'asks'

KEY_BIDS = 'b'
KEY_ASKS = 'a'

class OrderBook(object):
    # We redundant define the default value of limit,
    #   because OrderBook is also a public class
    def __init__(self, symbol,
        limit=DEFAULT_DEPTH_LIMIT,
        client=None,
        retry_policy=DEFAULT_RETRY_POLICY
    ):
        self.asks = SequencedList()
        self.bids = SequencedList()

        self._symbol = normalize_symbol(symbol, True)
        self._limit = limit
        self._client = None
        self._retry_policy = retry_policy

        self._last_update_id = 0
        # The queue to save messages that are not continuous
        self._unsolved_queue = []
        self._onchange_callbacks = None
        self._updated_future = asyncio.Future()

        # Whether we are still fetching the depth snapshot
        self._fetching = False

        self.set_client(client)

    # Whether the orderbook is updated
    @property
    def ready(self):
        return not self._fetching and self._last_update_id != 0

    async def updated(self):
        await self._updated_future

    def set_client(self, client):
        if not client:
            return

        self._client = client

        if not self.ready:
            self._start_fetching()

    def _emit_updated(self):
        self._updated_future.set_result(None)
        self._updated_future = asyncio.Future()

    # Returns `bool` whether the depth is updated
    async def fetch(self):
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

        if len(self._unsolved_queue) == 0:
            return True

        counter = 0
        for payload in self._unsolved_queue:
            updated = self._update(payload)

            if not updated:
                del self._unsolved_queue[:counter]
                return False

            counter += 1

        self._unsolved_queue.clear()
        return True

    async def _fetch(self, retries=0):
        updated = False

        try:
            updated = await self.fetch()
        except Exception as e:
            # TODO: logger
            # print(e, type(e))
            pass

        if updated:
            # success
            self._fetching = False
            self._emit_updated()
            return
        # else: fails to update

        abandon, delay, reset = self._retry_policy(retries)

        if abandon:
            self._fetching = False
            return

        retries = 0 if reset else retries + 1

        if delay:
            await asyncio.delay(delay)

        # We re-fetch until succeeded
        await self._fetch(retries)

    def _start_fetching(self):
        if not self._fetching:
            self._fetching = True
            asyncio.create_task(self._fetch())

    def _merge(self, last_update_id, asks, bids):
        self._last_update_id = last_update_id
        self.asks.merge(asks)
        self.bids.merge(bids)

    def update(self, payload):
        if self._fetching:
            # If fetching is not completed, we should not merge orderbook,
            # We put the payload into the queue and will **try** to merge the
            #   payload into orderbook
            self._unsolved_queue.append(payload)
            return False

        updated = self._update(payload)

        if not updated:
            self._start_fetching()

        return updated

    # Returns whether the payload is updated
    def _update(self, payload):
        first = payload[KEY_FIRST_UPDATE_ID]
        last = payload[KEY_LAST_UPDATE_ID]
        current_last = self._last_update_id

        if last <= current_last:
            # abandon the payload
            return True

        if first <= self._last_update_id + 1:
            # It is ok
            self._merge(last, payload[KEY_ASKS], payload[KEY_BIDS])
            self._emit_updated()
            return True

        return False
