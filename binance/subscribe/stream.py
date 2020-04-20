from typing import (
    List,
    Iterable
)

from .stream_base import StreamBase


class Stream(StreamBase):
    def __init__(self, *arg, **kwargs) -> None:
        super().__init__(*arg, **kwargs)

        self._subscribed = set()

    async def subscribe(
        self,
        params: Iterable[str]
    ):
        ret = await self.send({
            'method': 'SUBSCRIBE',
            'params': params
        })

        for param in params:
            self._subscribed.add(param)

        return ret

    async def unsubscribe(
        self,
        params: Iterable[str]
    ):
        ret = await self.send({
            'method': 'UNSUBSCRIBE',
            'params': params
        })

        for param in params:
            self._subscribed.discard(param)

        return ret

    async def _connected(self) -> None:
        if len(self._subscribed) > 0:
            await self.subscribe(list(self._subscribed))

    def _after_close(self) -> None:
        self._subscribed.clear()

    async def list_subscriptions(self) -> List[str]:
        return await self.send({
            'method': 'LIST_SUBSCRIPTIONS'
        })
