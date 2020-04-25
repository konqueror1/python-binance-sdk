import json
import logging
import asyncio
from typing import (
    Optional,
    Any
)

from websockets import (
    connect,
    WebSocketClientProtocol
)
from websockets.exceptions import (
    ConnectionClosed,
    ConnectionClosedOK,
    ConnectionClosedError
)

from aioretry import (
    RetryPolicy,
    retry
)

from binance.common.utils import (
    json_stringify,
    format_msg,
    repr_exception,
    wrap_event_callback
)

from binance.common.exceptions import StreamDisconnectedException
from binance.common.constants import (
    DEFAULT_RETRY_POLICY,
    DEFAULT_STREAM_TIMEOUT,
    DEFAULT_STREAM_CLOSE_CODE,
    STREAM_KEY_ID,
    STREAM_KEY_RESULT
)

from binance.common.types import (
    EventCallback,
    Timeout
)


logger = logging.getLogger(__name__)

ON_MESSAGE = 'on_message'
ON_CONNECTED = 'on_connected'


class Stream:
    """Class to handle Binance streams

    Args:
        uri (str): stream uri
        on_message (Callback): either sync or async callable to receive stream message
        on_connected (:obj:`Callable`, optional): invoked when the socket is connected
        retry_policy (RetryPolicy): see document
        timeout (float): timeout in seconds to receive the next websocket message
    """

    _socket: Optional[WebSocketClientProtocol]

    def __init__(
        self,
        uri: str,
        on_message: EventCallback,
        on_connected: Optional[EventCallback] = None,
        # We redundant the default value here,
        #   because `binance.Stream` is also a public class
        retry_policy: RetryPolicy = DEFAULT_RETRY_POLICY,
        timeout: Timeout = DEFAULT_STREAM_TIMEOUT,
    ) -> None:
        self._on_message = wrap_event_callback(on_message, ON_MESSAGE, True)
        self._on_connected = wrap_event_callback(
            on_connected,
            ON_CONNECTED,
            False
        )

        self._retry_policy = retry_policy
        self._timeout = timeout

        self._socket = None
        self._conn_task = None
        self._connected_task = None

        # message_id
        self._message_id = 0
        self._message_futures = {}

        self._open_future = None
        self._closing = False

        self._uri = uri

    def _set_socket(self, socket) -> None:
        if self._open_future:
            self._open_future.set_result(socket)
            self._open_future = None

        self._socket = socket

    def connect(self):
        self._before_connect()

        self._conn_task = asyncio.create_task(self._connect())
        return self

    async def _emit(
        self,
        event_name: str,
        *args
    ) -> None:
        event_callback = getattr(self, f'_{event_name}', None)

        if event_callback is None:
            return

        return await event_callback(*args)

    async def _handle_message(self, msg) -> None:
        # > The id used in the JSON payloads is an unsigned INT used as
        # > an identifier to uniquely identify the messages going back and forth
        if STREAM_KEY_ID in msg \
                and msg[STREAM_KEY_ID] in self._message_futures:
            message_id = msg[STREAM_KEY_ID]
            future = self._message_futures[message_id]
            future.set_result(msg[STREAM_KEY_RESULT])

            del self._message_futures[message_id]
            return

        await self._emit(ON_MESSAGE, msg)

    def _before_connect(self) -> None:
        self._open_future = asyncio.Future()

    async def _receive(self) -> None:
        try:
            msg = await asyncio.wait_for(
                self._socket.recv(), timeout=self._timeout)
        except asyncio.TimeoutError:
            await self._socket.ping()
            return

        # Other exceptions for socket.recv():
        # - ConnectionClosed
        # - ConnectionClosedOK
        # - ConnectionClosedError
        # which should be handled by self._connect()

        else:
            try:
                parsed = json.loads(msg)
            except ValueError as e:
                logger.error(
                    format_msg(
                        'stream message "%s" is an invalid JSON: reason: %s',
                        msg,
                        e
                    )
                )

                return
            else:
                await self._handle_message(parsed)

    @retry(
        retry_policy='_retry_policy',
        after_failure='_reconnect'
    )
    async def _connect(self) -> None:
        async with connect(self._uri) as socket:
            self._set_socket(socket)

            self._connected_task = asyncio.create_task(
                self._emit(ON_CONNECTED)
            )

            try:
                # Do not receive messages if the stream is closing
                while not self._closing:
                    await self._receive()

            except (
                ConnectionClosed,
                # Binance stream never close unless errored
                ConnectionClosedOK,
                ConnectionClosedError,
                # task cancel
                asyncio.CancelledError
            ) as e:
                if self._closing:
                    # The socket is closed by `await self.close()`
                    return

                # Raise, so aioretry will reconnecting
                raise e

    async def _reconnect(self, exception: Exception, fails: int) -> None:
        logger.error(
            format_msg(
                'socket error %s, reconnecting %s...',
                repr_exception(exception),
                fails
            )
        )

        if self._connected_task is not None:
            self._connected_task.cancel()

            try:
                await self._connected_task
            except Exception:
                pass

        self._before_connect()

    async def close(
        self,
        code: int = DEFAULT_STREAM_CLOSE_CODE
    ) -> None:
        """Close the current socket connection

        Args:
            code (:obj:`int`, optional): socket close code, defaults to 4999
        """

        if not self._conn_task:
            raise StreamDisconnectedException(self._uri)

        # A lot of incomming messages might prevent
        #   the socket from gracefully shutting down,
        #    which leads `websockets` to fail connection
        #    and result in a 1006 close code (ConnectionClosedError).
        # In that situation, we can not properly figure out whether the socket
        #   is closed by socket.close() or network connection error.
        # So just set up a flag to do the trick
        self._closing = True

        tasks = [self._conn_task]

        if self._socket:
            tasks.append(
                # make socket.close run in background
                asyncio.create_task(self._socket.close(code))
            )

        self._conn_task.cancel()

        try:
            # Make sure:
            # - conn_task is cancelled
            # - socket is closed
            await asyncio.wait(tasks)
        # except asyncio.CancelledError:
        #     # It is ok for it is us that cancel the task
        #     pass
        except Exception as e:
            logger.error(
                format_msg('close tasks error: %s', e)
            )

        self._socket = None
        self._closing = False

    async def send(
        self,
        msg: dict
    ) -> Any:
        """Send a request to Binance stream
        and handle the asynchronous socket response

        Request::

            {
                "method": "SUBSCRIBE",
                "params": [
                    "btcusdt@aggTrade",
                    "btcusdt@depth"
                ],
                "id": 1
            }

        Response::

            {
                "result": null,
                "id": 1
            }

        Then the result of `self.send()` is `None` (null)
        """

        socket = self._socket

        if not socket:
            if self._open_future:
                socket = await self._open_future
            else:
                raise StreamDisconnectedException(self._uri)

        future = asyncio.Future()

        message_id = self._message_id
        self._message_id += 1

        msg[STREAM_KEY_ID] = message_id
        self._message_futures[message_id] = future

        await socket.send(json_stringify(msg))
        return await future
