from .stream_base import StreamBase
from binance.common.utils import normalize_symbol

class Stream(StreamBase):
    def __init__(self,
        uri, on_message, retry_policy, timeout):
        super(Stream, self).__init__(
            uri, on_message, retry_policy, timeout)

        self._subscribed = set()

    async def subscribe(self, params):
        ret = await self.send({
            'method': 'SUBSCRIBE',
            'params': params
        })

        for param in params:
            self._subscribed.add(param)

        return ret

    async def unsubscribe(self, params):
        ret = await self.send({
            'method': 'UNSUBSCRIBE',
            'params': params
        })

        for param in params:
            self._subscribed.discard(param)

        return ret

    async def _before_reconnect(self):
        if len(self._subscribed) > 0:
            await self.subscribe(list(self._subscribed))

    def _after_close(self):
        self._subscribed.clear()

    async def list_subscriptions(self):
        return await self.send({
            'method': 'LIST_SUBSCRIPTIONS'
        })
