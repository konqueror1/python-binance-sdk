import asyncio
import json
import websockets as ws

from binance.common.utils import json_stringify
from binance.common.exceptions import \
    BinanceSocketAbandonedException

KEY_ID = 'id'
KEY_RESULT = 'result'

# TODO: handle error code
KEY_CODE = 'code'

class StreamBase(object):
    def __init__(self,
        on_message,
        host,
        retry_policy,
        timeout
    ):
        self._on_message = on_message
        self._stream_host = host
        self._retry_policy = retry_policy
        self._timeout = timeout

        self._socket = None
        self._conn = None
        self._retries = 0

        # message_id
        self._message_id = 0
        self._message_futures = {}

        self._open_future = None

        self._url = self._get_stream_url()

    def _get_stream_url(self):
        return self._stream_host + '/stream'

    def connect(self):
        self._before_connect()

        self._conn = asyncio.create_task(self._connect())
        return self

    async def _handle_message(self, msg):
        # > The id used in the JSON payloads is an unsigned INT used as
        # > an identifier to uniquely identify the messages going back and forth
        if KEY_ID in msg and msg[KEY_ID] in self._message_futures:
            message_id = msg[KEY_ID]
            future = self._message_futures[message_id]
            future.set_result(msg[KEY_RESULT])

            del self._message_futures[message_id]
            return

        await self._on_message(msg)

    def _before_connect(self):
        if self._open_future:
            return

        self._open_future = asyncio.Future()

    def _set_socket(self, socket):
        if self._open_future:
            self._open_future.set_result(socket)
            self._open_future = None

        self._socket = socket

    async def _receive(self):
        try:
            msg = await asyncio.wait_for(
                self._socket.recv(), timeout=self._timeout)
        except asyncio.TimeoutError:
            await self.ping()
        except asyncio.CancelledError:
            await self.ping()
        else:
            try:
                parsed = json.loads(msg)
            except ValueError:
                pass
            else:
                await self._handle_message(parsed)

    async def _connect(self):
        async with ws.connect(self._url) as socket:
            self._set_socket(socket)
            self._retries = 0

            try:
                while True:
                    await self._receive()
            except ws.ConnectionClosed as e:
                await self._reconnect()
            except Exception as e:
                await self._reconnect()

    async def _reconnect(self):
        self._before_connect()

        self.cancel()
        retries = self._retries
        self._retries += 1
        abandon, delay, reset = self._retry_policy(retries)

        if abandon:
            self._open_future = None
            return

        if reset:
            self._retries = 0

        if delay:
            await asyncio.sleep(delay)

        await self._connect()

    async def _ping(self):
        if self._socket:
            await self._socket.ping()

    def cancel(self):
        self._conn.cancel()
        self._socket = None

    async def send(self, msg):
        socket = self._socket

        if not socket:
            if self._open_future:
                socket = await self._open_future
            else:
                raise BinanceSocketAbandonedException(self._url)

        future = asyncio.Future()

        message_id = self._message_id
        self._message_id += 1

        msg[KEY_ID] = message_id
        self._message_futures[message_id] = future

        await socket.send(json_stringify(msg))
        return await future
