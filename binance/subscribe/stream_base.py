import json
from abc import ABC, abstractmethod
import logging
import asyncio
import warnings
from typing import (
    Optional,
    Callable,
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
    format_msg
)
from binance.common.exceptions import StreamDisconnectedException
from binance.common.constants import (
    DEFAULT_RETRY_POLICY,
    DEFAULT_STREAM_TIMEOUT,
    DEFAULT_STREAM_CLOSE_CODE,
    STREAM_KEY_ID,
    STREAM_KEY_RESULT
)


logger = logging.getLogger(__name__)


class StreamBase(ABC):
    _socket: Optional[WebSocketClientProtocol]

    def __init__(
        self,
        uri: str,
        on_message: Callable,
        # We redundant the default value here,
        #   because `binance.Stream` is also a public class
        retry_policy: RetryPolicy = DEFAULT_RETRY_POLICY,
        timeout: Optional[float] = DEFAULT_STREAM_TIMEOUT,
    ) -> None:
        self._on_message = on_message
        self._retry_policy = retry_policy
        self._timeout = timeout

        self._socket = None
        self._conn_task = None

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

        try:
            # Exceptions raised by user function should not intercept
            # websocket connection,
            # so we must catch them
            await self._on_message(msg)
        except Exception as e:
            warnings.warn(
                format_msg("""`on_message` raises:
%s
And you should fix this""", e),
                RuntimeWarning
            )

    def _before_connect(self) -> None:
        self._open_future = asyncio.Future()

    async def _receive(self) -> None:
        try:
            msg = await asyncio.wait_for(
                self._socket.recv(), timeout=self._timeout)
        except asyncio.TimeoutError:
            await self._socket.ping()
            return
        except asyncio.CancelledError:
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

            try:
                await self._connected()
            except Exception as e:
                logger.error(
                    format_msg(
                        'fails to invoke connected handler: %s',
                        e
                    )
                )

            try:
                # Do not receive messages if the stream is closing
                while not self._closing:
                    await self._receive()

            except (
                ConnectionClosed,
                # Binance stream never close unless errored
                ConnectionClosedOK,
                ConnectionClosedError
            ) as e:
                # We don't know whether `ws.ConnectionClosed(close_code)` or
                # `asyncio.CancelledError` comes first
                if self._closing:
                    # The socket is closed by `await self.close()`
                    return

                # Raise, so aioretry will reconnecting
                raise e

            except asyncio.CancelledError:
                return

    async def _reconnect(self, exception: Exception, fails: int) -> None:
        logger.error(
            format_msg(
                'socket error %s: %s, reconnecting',
                exception,
                fails
            )
        )

        self._before_connect()

    @abstractmethod
    async def _connected(self) -> None:
        """Event hanndler which is invoked whenever the socket is connected
        """
        ...  # pragma: no-cover

    @abstractmethod
    def _after_close(self) -> None:
        ...  # pragma: no-cover

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
        except Exception as e:
            logger.error(
                format_msg('close tasks error: %s', e)
            )

        self._socket = None
        self._closing = False

        self._after_close()

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

        Then the result of `self.sennd()` is `None` (null)
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
