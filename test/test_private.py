import asyncio
import pytest

from binance import (
    Client,
    SubType,
    UserStreamNotSubscribedException
)
from binance.processors.user_processor import UserProcessor

from .common import print_json


UserProcessor.KEEP_ALIVE_INTERVAL = .1


try:
    from .private_no_track import (
        API_KEY,
        API_SECRET
    )

    has_private_config = True
except ModuleNotFoundError:
    has_private_config = False


@pytest.mark.asyncio
async def test_user_stream():
    if not has_private_config:
        return

    client = Client(API_KEY, API_SECRET)

    with pytest.raises(
        UserStreamNotSubscribedException,
        match='not subscribed'
    ):
        await client.unsubscribe(SubType.USER)

    await client.subscribe(SubType.USER)
    await asyncio.sleep(.2)

    await client.unsubscribe(SubType.USER)

    await client.close()


@pytest.mark.asyncio
async def test_user_trades():
    if not has_private_config:
        return

    client = Client(API_KEY, API_SECRET)

    res = await client.get_trades(symbol='BTCUSDT')

    print_json('get_trades:', res)
