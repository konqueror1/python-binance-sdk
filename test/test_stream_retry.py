import pytest
import asyncio

from aiohttp import web, WSMsgType

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

    async def _handle(self, ws):
        while True:
            if not self._started:
                await ws.close()

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
    f = asyncio.Future()

    async def on_message(msg):
        if not f.done():
            f.set_result(msg)

    def retry_policy(retries):
        return False, 0.05, False

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
    server.start()

    await asyncio.sleep(0.5)
    server.no_timeout()

    msg = await f

    assert msg['ok']

    await stream.close()
    print('stream closed')

    await server.shutdown()
    print('server shutdown')
