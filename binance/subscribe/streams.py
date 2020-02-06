from .stream_base import StreamBase
from binance.common.utils import normalize_symbol

class DataStream(StreamBase):
    def __init__(self,
        on_message, host, retry_policy, timeout):
        super(DataStream, self).__init__(
            on_message, host, retry_policy, timeout)

        self._subscribed = set()

    async def subscribe(self, symbols, subtype_list):
        params = []

        for s in symbols:
            for t in subtype_list:
                target = normalize_symbol(s) + '@' + t
                params.append(target)
                self._subscribed.add(target)

        return await self._subscribe(params)

    async def _before_reconnect(self):
        await self._subscribe(list(self._subscribed))

    def _after_close(self):
        self._subscribed.clear()

    def _subscribe(self, params):
        return self.send({
            'method': 'SUBSCRIBE',
            'params': params
        })

    async def list_subscriptions(self):
        return await self.send({
            'method': 'LIST_SUBSCRIPTIONS'
        })
