from .stream_base import StreamBase
from binance.common.utils import normalize_symbol

class DataStream(StreamBase):
    async def subscribe(self, symbols, subtype_list):
        params = []

        for s in symbols:
            for t in subtype_list:
                params.append(normalize_symbol(s) + '@' + t)

        return await self.send({
            'method': 'SUBSCRIBE',
            'params': params
        })

    async def list_subscriptions(self):
        return await self.send({
            'method': 'LIST_SUBSCRIPTIONS'
        })
