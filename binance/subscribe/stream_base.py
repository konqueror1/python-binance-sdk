import asyncio
import json
import websockets as ws
from abc import ABC, abstractmethod

from binance.common.utils import json_stringify
from binance.common.exceptions import StreamAbandonedException
from binance.common.constants import \
    DEFAULT_RETRY_POLICY, DEFAULT_STREAM_TIMEOUT, DEFAULT_STREAM_CLOSE_CODE

KEY_ID = 'id'
KEY_RESULT = 'result'

# TODO: handle error code
# KEY_CODE = 'code'

INVALID_WS_CLOSE_CODE = - 1

class StreamBase(ABC):
    def __init__(self,
        uri,
        on_message,
        # We redundant the default value here,
        #   because `binance.Stream` is also a public class
        retry_policy=DEFAULT_RETRY_POLICY,
        timeout=DEFAULT_STREAM_TIMEOUT,
    ):
        self._on_message = on_message
        self._retry_policy = retry_policy
        self._timeout = timeout

        # `websockets` close code is never - 1
        self._close_code = INVALID_WS_CLOSE_CODE

        self._socket = None
        self._conn_task = None
        self._retries = 0

        # message_id
        self._message_id = 0
        self._message_futures = {}

        self._open_future = None

        self._uri = uri

    def connect(self):
        self._before_connect()

        self._conn_task = asyncio.create_task(self._connect())
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
            await self._socket.ping()
        except asyncio.CancelledError:
            await self._socket.ping()
        else:
            try:
                parsed = json.loads(msg)
            except ValueError:
                pass
            else:
                await self._handle_message(parsed)

    async def _connect(self):
        async with ws.connect(self._uri) as socket:
            self._set_socket(socket)
            self._retries = 0

            try:
                while True:
                    await self._receive()
            except ws.ConnectionClosed as e:
                if e.code == self._close_code:
                    # The socket is closed by `await self.close()`
                    return

                await self._reconnect()
            except Exception as e:
                await self._reconnect()

    async def _reconnect(self):
        self._before_connect()

        # If the retries == 0, we will reconnect immediately
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

        await self._before_reconnect()
        await self._connect()

    @abstractmethod
    async def _before_reconnect(self):
        pass

    @abstractmethod
    def _after_close(self):
        pass

    async def close(self, code=DEFAULT_STREAM_CLOSE_CODE):
        self._close_code = code

        if self._socket:
            await self._socket.close(self._close_code)

        self._conn_task.cancel()
        self._close_code = INVALID_WS_CLOSE_CODE

    async def send(self, msg):
        socket = self._socket

        if not socket:
            if self._open_future:
                socket = await self._open_future
            else:
                raise StreamAbandonedException(self._uri)

        future = asyncio.Future()

        message_id = self._message_id
        self._message_id += 1

        msg[KEY_ID] = message_id
        self._message_futures[message_id] = future

        await socket.send(json_stringify(msg))
        return await future
