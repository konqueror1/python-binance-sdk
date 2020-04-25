import pytest
import asyncio

from binance import (
    Stream,
    StreamDisconnectedException,
    StreamSubscribeException
)

from binance.common.constants import STREAM_HOST

from .common import (
    PORT,
    SocketServer
)


async def run_stream():
    f = asyncio.Future()

    async def on_message(msg):
        f.set_result(msg)

    stream = Stream(
        STREAM_HOST + '/stream',
        on_message
    )

    stream.connect()

    params = ['btcusdt@ticker']

    print('\nsubscribed', await stream.send({
        'method': 'SUBSCRIBE',
        'params': params
    }))

    assert await stream.send({
        'method': 'LIST_SUBSCRIPTIONS'
    }) == params

    msg = await f

    assert msg['stream'] == 'btcusdt@ticker'

    with pytest.raises(
        StreamSubscribeException,
        match='fails to subscribe'
    ):
        await stream.send({
            'method': 'SUBSCRIBE',
            'params': []
        })

    print('before close')
    await stream.close()


@pytest.mark.asyncio
async def test_binance_stream():
    await run_stream()


def on_message():
    pass


@pytest.mark.asyncio
async def test_stream_never_connect():
    with pytest.raises(StreamDisconnectedException, match='never connected'):
        await Stream(
            STREAM_HOST + '/stream',
            on_message
        ).send({})


@pytest.mark.asyncio
async def test_stream_close_before_connect():
    with pytest.raises(StreamDisconnectedException, match='never connected'):
        await Stream(
            STREAM_HOST + '/stream',
            on_message
        ).close()


def test_stream_invalid_on_message():
    with pytest.raises(
        ValueError,
        match='event callback `on_message` is required'
    ):
        Stream('fake url', None)  # type: ignore


@pytest.mark.asyncio
async def test_json_error():
    server = SocketServer()
    await server.invalid_json().start().run()

    uri = 'ws://localhost:%s/stream' % PORT

    print('connecting', uri)
    stream = Stream(
        uri,
        on_message
    ).connect()

    await asyncio.sleep(1)

    await stream.close()
    await server.shutdown()
