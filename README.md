[![Build Status](https://travis-ci.org/kaelzhang/python-binance-sdk.svg?branch=master)](https://travis-ci.org/kaelzhang/python-binance-sdk)
[![Coverage](https://codecov.io/gh/kaelzhang/python-binance-sdk/branch/master/graph/badge.svg)](https://codecov.io/gh/kaelzhang/python-binance-sdk)

# binance-sdk

Unofficial Binance SDK for python 3.7+, which:

- Uses Binance's new websocket stream which supports live pub/sub so that we could save websocket connections
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

client = Client(api_key)

async def main():
    print(await client.get_symbol_info('BTCUSDT'))

asyncio.run(main())
```

## Handling messages

Binance-sdk designs a handler-based APIs to handle all websocket messages, and you are able to not concern about websockets.

```py
from binance import Client, TickerHandlerBase, RET_OK, SubType

client = Client()

async def main():
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

    client.handler(TickerPrinter())

    # Subscribe to ticker change for symbol BTCUSDT
    await client.subscribe('BTCUSDT', SubType.TICKER)

    # Stop receiving websocket message and dispatching to handlers,
    #   but the websocket connections are still open.
    # We could `client.start()` to start receiving messages again
    client.stop()

    # Close all websocket connections
    client.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

# Run the loop forever so continuously receiving messages
loop.run_forever()
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
    # We could also subscribe multiple types
    #   for both `BNBUSDT` and 'BNBBTC'
    [
        SubType.AGG_TRADE,
        SubType.ORDER_BOOK,
        SubType.KLINE_DAY
    ]
)
```

And since we subscribe to **THREE** new types of messages, we need to set the handlers each of which should  `isinstance()` of one of
- `binance.AggTradeHandlerBase`
- `binance.OrderBookHandlerBase`
- `binance.KlineHandlerBase`
- `binance.TickerHandlerBase`

```py
client.handler(MyTradeHandler(), MyOrderBookHandler(), MyKlineHandler())
```

### Subscribe to user streams

```py
client.subscribe_user()
```

## License

[MIT](LICENSE)
