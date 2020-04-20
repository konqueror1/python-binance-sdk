import pytest
import asyncio

from aiohttp import web

from binance import Stream

PORT = 9081


class Server:
    def __init__(self):
        self._started = False
        app = web.Application()
        app.add_routes([
            web.get('/stream', self._handler)
        ])

        self._app = app

        self._runner = web.AppRunner(app)

        self._delay = 0.2

    def start(self):
        self._started = True
        return self

    def no_timeout(self):
        self._delay = 0.05
        return self

    def stop(self):
        self._started = False
        return self

    async def run(self):
        await self._runner.setup()
        site = web.TCPSite(self._runner, 'localhost', PORT)
        await site.start()

    async def shutdown(self):
        self.stop()
        await self._runner.cleanup()

    async def _handle(self, ws) -> None:
        if not self._started:
            await ws.close()
            return

        while self._started:
            if self._delay:
                await asyncio.sleep(self._delay)

            await ws.send_str('{"ok":true}')

    async def _handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        await self._handle(ws)

        return ws


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

    def retry_policy(fails):
        return False, 0.05

    server = Server()

    await server.run()
    print('\nserver started')

    uri = 'ws://localhost:%s/stream' % PORT

    print('connecting', uri)
    stream = Stream(
        uri,
        on_message,
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
