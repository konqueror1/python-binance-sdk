[![Build Status](https://travis-ci.org/kaelzhang/python-binance-sdk.svg?branch=master)](https://travis-ci.org/kaelzhang/python-binance-sdk)
[![Coverage](https://codecov.io/gh/kaelzhang/python-binance-sdk/branch/master/graph/badge.svg)](https://codecov.io/gh/kaelzhang/python-binance-sdk)

# binance-sdk

Unofficial Binance SDK for python 3.7+, which:

- [x] Uses Binance's new websocket stream which supports live pub/sub so that we only need **ONE** websocket connection.
- [x] Has optional `pandas.DataFrame` support. If `pandas` is installed, columns of all stream data frames are renamed for readability.
- [x] Based on python `async`/`await`
- [ ] Manages the order book for you (handled by `OrderBookHandlerBase`), so that you need not to worry about websocket reconnection and message losses.

## Install

```sh
# Without pandas support
pip install binance-sdk
```

or

```sh
# With pandas support
pip install binance-sdk[pandas]
```

## Usage

```py
import asyncio
from binance import Client

client = Client(api_key)

async def main():
    print(await client.get_symbol_info('BTCUSDT'))

asyncio.run(main())
```

## Handling messages

Binance-sdk provides handler-based APIs to handle all websocket messages, and you are able to not worry about websockets.

```py
from binance import Client, TickerHandlerBase, SubType

client = Client()

async def main():
    # Start receiving websocket data
    client.start()

    # Implement your own TickerHandler.
    class TickerPrinter(TickerHandlerBase):
        # It could either be a sync or async(recommended) method
        async def receive(self, res):
            # If binance-sdk is installed with pandas support, then
            #   `ticker` will be a dataFrame with columns renamed
            # Or `ticker` is a raw dict
            ticker = super(TickerPrinter, self).receive(res)

            # Just print the ticker
            print(ticker)

    # Register the handler for `SubType.TICKER`
    client.handler(TickerPrinter())

    # Subscribe to ticker change for symbol BTCUSDT
    await client.subscribe('BTCUSDT', SubType.TICKER)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

# Run the loop forever to keep receiving messages
loop.run_forever()
```

### Subscribe to more symbol pairs and types

```py
result = await client.subscribe(
    # We could subscribe more than one symbol pairs at a time
    [
        # Which is equivalent to `BNBUSDT`
        'BNB_USDT',
        'BNBBTC'
    ],
    # We could also subscribe multiple types
    #   for both `BNBUSDT` and 'BNBBTC'
    [
        SubType.AGG_TRADE,
        SubType.ORDER_BOOK,
        SubType.KLINE_DAY
    ]
)
```

And since we subscribe to **THREE** new types of messages, we need to set the handlers each of which should `isinstance()` of one of
- `binance.TradeHandlerBase`
- `binance.AggTradeHandlerBase`
- `binance.OrderBookHandlerBase`
- `binance.KlineHandlerBase`
- `binance.TickerHandlerBase`
- `binance.MiniTickerHandlerBase`

```py
client.handler(MyTradeHandler(), MyOrderBookHandler(), MyKlineHandler())
```

### Subscribe to user streams

```py
client.subscribe_user()
```

## License

[MIT](LICENSE)
