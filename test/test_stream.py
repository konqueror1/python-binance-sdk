import pytest
import asyncio

from binance import Stream
from binance.common.constants import STREAM_HOST

@pytest.mark.asyncio
async def test_binance_stream():
    f = asyncio.Future()

    async def on_message(msg):
        f.set_result(msg)

    stream = Stream(
        STREAM_HOST + '/stream',
        on_message
    ).connect()

    await stream.subscribe(['btcusdt@ticker'])

    msg = await f
    print(msg)
    stream.close()
