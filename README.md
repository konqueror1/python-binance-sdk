[![Build Status](https://travis-ci.org/kaelzhang/python-binance-sdk.svg?branch=master)](https://travis-ci.org/kaelzhang/python-binance-sdk)
[![Coverage](https://codecov.io/gh/kaelzhang/python-binance-sdk/branch/master/graph/badge.svg)](https://codecov.io/gh/kaelzhang/python-binance-sdk)

# binance-sdk

Unofficial Binance SDK for python 3.7+, which:

- Uses the new websocket stream which supports live pub/sub so that we can save websocket connections
- Supports `pandas.DataFrame`
- Based on python `async`/`await`
- Manages the order book for you (handled by `OrderBookHandlerBase`), so that you need not to worry about websocket reconnection and message losses.

## Install

```sh
pip install binance-sdk
```

## Usage

```py
import asyncio
from binance import Client

client = Client(api_key, api_secret)

async def main():
    print(await client.get_symbol_info('BTCUSDT'))

asyncio.run(main())
```

## Handling messages

Binance-sdk designs a handler-based APIs to handle all websocket messages, and you are able to not concern about websockets.

```py
from binance import TickerHandlerBase, RET_OK, SubType

# Start receiving websocket data,
#   and this will prevent the current process from exiting
client.start()

# Implement your own TickerHandler.
class TickerPrinter(TickerHandlerBase):
    # It could either be a sync or async(recommended) method
    async def receive(self, res):
        code, ticker_df = super(TickerPrinter, self).receive(res)
        if code != RET_OK:
            return ret_code, ticker_df

        # So something you want
        await remoteUpdateTicker(ticker_df)

client.set_handler(TickerPrinter())

# Subscribe to ticker change for symbol BTCUSDT
client.subscribe('BTCUSDT', [SubType.TICKER])

# Stop receiving websocket message and dispatching to handlers,
#   but the websocket connections are still open.
# We could `client.start()` to start receiving messages again
client.stop()

# Close all websocket connections
client.close()
```

### Subscribe to more symbol pairs and types

```py
client.subscribe(
    # We could subscribe more than one symbol pairs at a time
    [
        # Which is equivalent to `BNBUSDT`
        'BNB_USDT',
        'BNBBTC'
    ],
    [
        SubType.AGG_TRADE,
        SubType.ORDER_BOOK,
        SubType.KLINE_DAY
    ]
)
```

### Subscribe to user streams

```py
client.subscribe_user()
```

## License

[MIT](LICENSE)
