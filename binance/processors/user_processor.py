import asyncio

from binance.common.constants import SubType

from .base import ProcessorBase

class UserProcessor(ProcessorBase):
    # HANDLER = UserHandlerBase
    SUB_TYPE = SubType.USER

    KEEP_ALIVE_INTERVAL = 60 * 30

    def __init__(self, *args):
        super(UserProcessor, self).__init__(*args)

        self._listen_key = None
        self._keep_alive_task = None

    async def subscribe_param(self, subscribe, t):
        if subscribe == False:
            key = self._listen_key
            await self._close_stream()
            self._listen_key = None
            return key

        key = await self._client.get_user_listen_key()

        self._listen_key = key
        self._start_keep_alive()

        return key

    async def _keep_alive(self):
        # Send a keepalive requests every 30 minutes
        while True:
            await asyncio.sleep(self.KEEP_ALIVE_INTERVAL)
            if self._listen_key:
                await self._client.keepalive_listen_key(self._listen_key)

    def _start_keep_alive(self):
        self._stop_keep_alive()
        self._keep_alive_task = asyncio.create_task(self._keep_alive())

    def _stop_keep_alive(self):
        if self._keep_alive_task:
            self._keep_alive_task.cancel()
            self._keep_alive_task = None

    async def _close_stream(self):
        self._stop_keep_alive()
        await self._client.close_listen_key(self._listen_key)
