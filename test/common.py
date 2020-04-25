import asyncio

from aiohttp import web

from binance.common.utils import json_stringify

MAX_PRINT = 150


def print_json(name, d):
    s = json_stringify(d)

    length = len(s)
    if length > MAX_PRINT:
        print(name, s[:MAX_PRINT], 'and %s more' % (length - MAX_PRINT))
    else:
        print(name, s)


PORT = 9081


class SocketServer:
    def __init__(self):
        self._started = False
        app = web.Application()
        app.add_routes([
            web.get('/stream', self._handler)
        ])

        self._app = app

        self._runner = web.AppRunner(app)

        self._delay = 0.2
        self._valid_json = True

    def start(self):
        self._started = True
        return self

    def no_timeout(self):
        self._delay = 0.05
        return self

    def invalid_json(self):
        self._valid_json = False
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
            await ws.close(code=1006)
            return

        while self._started:
            if self._delay:
                await asyncio.sleep(self._delay)

            if self._valid_json:
                await ws.send_str('{"ok":true}')
            else:
                await ws.send_str('{"ok":true')

    async def _handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        await self._handle(ws)

        return ws
