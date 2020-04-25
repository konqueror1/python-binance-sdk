import pytest
import asyncio

from binance import Stream

from .common import (
    PORT,
    SocketServer
)


@pytest.mark.asyncio
async def test_stream_timeout_disconnect_reconnect():
    class Handler:
        def __init__(self):
            self.reset()

        def reset(self):
            self.f = asyncio.Future()

        def receive(self, msg):
            if not self.f.done():
                self.f.set_result(msg)

        async def received(self):
            return await self.f

    handler = Handler()

    async def on_message(msg):
        print('receive msg', msg)
        handler.receive(msg)

    should_raise = True

    def error_on_connected():
        if should_raise:
            raise RuntimeError('this is a warning for testing, not a bug')

    def retry_policy(fails):
        return False, 0.05

    server = SocketServer()

    await server.run()
    print('\nserver started')

    uri = 'ws://localhost:%s/stream' % PORT

    print('connecting', uri)
    stream = Stream(
        uri,
        on_message=on_message,
        on_connected=error_on_connected,
        retry_policy=retry_policy,
        timeout=0.1
    ).connect()

    # During the 500ms, there might be a lot of disconnection
    await asyncio.sleep(0.5)

    print('start server')
    server.start()

    await asyncio.sleep(0.5)
    server.no_timeout()

    msg = await handler.received()

    assert msg['ok']

    print('before server shutdown')
    await server.shutdown()
    print('server shutdown')

    handler.reset()

    print('restart server')
    await server.run()
    server.start()

    msg = await handler.received()

    assert msg['ok']

    print('before stream close')
    await stream.close()
    print('stream closed')
    await server.shutdown()
    print('server shutdown')
