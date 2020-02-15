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

## Basic Usage

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
            #   `ticker` will be a `DataFrame` with columns renamed
            # Or `ticker` is a raw dict
            ticker = super(TickerPrinter, self).receive(res)

            # Just print the ticker
            print(ticker)

    # Register the handler for `SubType.TICKER`
    client.handler(TickerPrinter())

    # Subscribe to ticker change for symbol BTCUSDT
    await client.subscribe(SubType.TICKER, 'BTCUSDT')

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

# Run the loop forever to keep receiving messages
loop.run_forever()

# It prints a pandas.DataFrame for each message

#    type        event_time     symbol   open            high            low            ...
# 0  24hrTicker  1581597461196  BTCUSDT  10328.26000000  10491.00000000  10080.00000000 ...

# ...(to be continued)
```

### Subscribe to more symbol pairs and types

```py
result = await client.subscribe(
    # We could also subscribe multiple types
    #   for both `BNBUSDT` and 'BNBBTC'
    [
        SubType.AGG_TRADE,
        SubType.ORDER_BOOK,
        SubType.KLINE_DAY
    ],
    # We could subscribe more than one symbol pairs at a time
    [
        # Which is equivalent to `BNBUSDT`
        'BNB_USDT',
        'BNBBTC'
    ]
)
```

And since we subscribe to **THREE** new types of messages, we need to set the handlers each of which should `isinstance()` of one of
- `binance.TradeHandlerBase`
- `binance.AggTradeHandlerBase`
- `binance.OrderBookHandlerBase`
- `binance.KlineHandlerBase`
- `binance.MiniTickerHandlerBase`
- `binance.TickerHandlerBase`
- `binance.AllMarketMiniTickersHandlerBase`
- `binance.AllMarketTickersHandlerBase`

```py
client.handler(MyTradeHandler(), MyOrderBookHandler(), MyKlineHandler())
```

### Subscribe to user streams

```py
# Before subscribe to user stream, you need to provide `api_secret` (and also `api_key`)
client.secret(api_secret)

# Or, you should provide `api_secret` when initialize the client
# ```
# client = Client(api_key, api_secret)
# ```

# binance-sdk will handle user listen key internally without your concern
await client.subscribe(SubType.USER)
```

# APIs

## Client

### await client.subscribe(subtype, *subtype_params) -> None
### await client.subscribe(*subscriptions) -> None

- **subtype** `str` subscription type, should be one of `SubType.*`s
- **subtype_params** `List` params for a certain `subtype`
- **subscriptions** `List[Tuple]` a pack of subscriptions each of which is a tuple of `subtype` and `*subtype_params`.

Subscribe to a stream or multiple streams. If no websocket connection is made up, `client.subscribe` will also create a websocket connection.

```py
await client.subscribe(SubType.TICKER, 'BNBUSDT')

# SubType.ALL_MARKET_MINI_TICKERS with default param
await client.subscribe(SubType.ALL_MARKET_MINI_TICKERS)

# SubType.ALL_MARKET_MINI_TICKERS with update interval 3000ms
await client.subscribe(SubType.ALL_MARKET_MINI_TICKERS, 3000)

# Subcribe to multiple types
await client.subscribe(
    (SubType.TICKER, 'BNBUSDT'),
    (SubType.ALL_MARKET_MINI_TICKERS,) # <-- PAY ATTENTION to the `,` here
)
```

Possible exceptions:
- `InvalidSubParamsException`
- `UnsupportedSubTypeException`
- `InvalidSubTypeParamException`
- `StreamAbandonedException`

### client.start() -> None

Start receiving streams

### client.stop() -> None

Stop receiving streams

### client.close() -> None

Close stream connection, clear all stream subscriptions and clear all handlers.

### client.handler(*handlers)

- **handlers** `List[HandlerExceptionHandler|TradeHandlerBase|...]`

Register message handlers for streams. If we've subscribed to a stream of a certain `subtype` with no corresponding handler provided, the messages of `subtype` will not be handled.

Except for `HandlerExceptionHandler`, handlers each of whose name ends with `Base` should be inherited before use.

Typically, we need to inherit the `def receive(self, payload)` method.

```py
class MyTradeHandler(TradeHandlerBase):
    async def receive(self, msg):
        # If pandas is installed, then `payload` is a `pandas.DataFrame`,
        #   otherwise is a dict.
        # If you don't want the `pandas.DataFrame`, use `msg` directly
        payload = super(MyTradeHandler, self).receive(msg)
        await saveTrade(payload)

client.handler(MyTradeHandler())
```

We could also register multiple handlers at one time

```py
client.handler(MyTradeHandler(), MyTickerHandler())
```

If we register an invalid handler, an `InvalidHandlerException` exception will be raised.

## SubType

In this section, we will note the parameters for each `subtypes`

### `SubType`s with a param `symbol`

- `SubType.KLINE_*`
- `SubType.TRADE`
- `SubType.AGG_TRADE`
- `SubType.MINI_TICKER`
- `SubType.TICKER`
- `SubType.ORDER_BOOK`

### `SubType`s with an optional param `updateInterval=1000` (ms)

- `SubType.ALL_MARKET_MINI_TICKERS`
- `SubType.ALL_MARKET_TICKERS`

### `Subtype` with no param

- `SubType.USER`

## License

[MIT](LICENSE)
