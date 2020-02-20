[![Build Status](https://travis-ci.org/kaelzhang/python-binance-sdk.svg?branch=master)](https://travis-ci.org/kaelzhang/python-binance-sdk)
[![Coverage](https://codecov.io/gh/kaelzhang/python-binance-sdk/branch/master/graph/badge.svg)](https://codecov.io/gh/kaelzhang/python-binance-sdk)

# binance-sdk

Unofficial Binance SDK for python 3.7+, which:

- [x] Uses Binance's new websocket stream which supports live pub/sub so that we only need **ONE** websocket connection.
- [x] Has optional `pandas.DataFrame` support. If `pandas` is installed, columns of all stream data frames are renamed for readability.
- [x] Based on python `async`/`await`
- [x] Manages the order book for you (handled by `OrderBookHandlerBase`), so that you need not to worry about websocket reconnection and message losses. For details, see the section [`OrderBookHandlerBase`](#orderbookhandlerbase)

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
            ticker = super().receive(res)

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

## Client(api_key, **kwargs)

Create a binance client

- **api_key** `str=None` binance api key
- **kwargs**
  - **api_secret** `str=None` binance api secret
  - **requests_params** `dict=None` global requests params
  - **stream_retry_policy** `Callable[[int], (bool, int, bool)]` retry policy for websocket stream. For details, see [RetryPolicy](#retrypolicy)
  - **stream_timeout** `int=5` seconds util the stream reach an timeout error

### client.secret(api_secret) -> self

Define or change api secret, especially when we have not define api secret in `Client` constructor.

`api_secret` is not always required for using binance-sdk.

### await client.get(uri, signed=False, **kwargs)
### await client.post(uri, signed=False, **kwargs)
### await client.put(uri, signed=False, **kwargs)
### await client.delete(uri, signed=False, **kwargs)

- **uri** `str` the request url
- **signed** `bool=False` whether the client should sign the requests by using `api_secret`. If `signed` is `True`, `api_secret` must be provided, or there will be an `APISecretNotDefinedException` error

Send a GET/POST/PUT/DELETE HTTPs request.

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

### client.start() -> self

Start receiving streams

### client.stop() -> self

Stop receiving streams

### await client.close(code=4999) -> None

- **code** `int=4999` the custom close code for websocket. It should be in the [range 4000 - 4999](https://tools.ietf.org/html/rfc6455#section-7.4.2)

Close stream connection, clear all stream subscriptions and clear all handlers.

### client.handler(*handlers) -> self

- **handlers** `List[HandlerExceptionHandler|TradeHandlerBase|...]`

Register message handlers for streams. If we've subscribed to a stream of a certain `subtype` with no corresponding handler provided, the messages of `subtype` will not be handled.

Except for `HandlerExceptionHandler`, handlers each of whose name ends with `Base` should be inherited before use.

Typically, we need to override the `def receive(self, payload)` method.

```py
class MyTradeHandler(TradeHandlerBase):
    async def receive(self, msg):
        # If pandas is installed, then `payload` is a `pandas.DataFrame`,
        #   otherwise is a dict.
        payload = super().receive(msg)

        # If you don't want the `pandas.DataFrame`, use `msg` directly

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

## RetryPolicy

Retry policy is used by binance-sdk to determine what to do next after the client fails to do some certain thing.

```py
abandon, delay, reset = stream_retry_policy(retries)

# `retries` is the counter number of
#   how many times has the stream retried to reconnect.
# If the stream is disconnected just now for the first time, `retries` will be `0`

# If abandon is `True`, then the client will give up reconnecting.
# Otherwise:
# - The client will asyncio.sleep `delay` seconds before reconnecting.
# - If reset is `True`, the client will reset the retry counter to `0`
```

## OrderBookHandlerBase(**kwargs)

- **kwargs**
  - **limit?** `int=100` the limit of the depth snapshot
  - **retry_policy?** `Callable=`

By default, binance-sdk maintains the orderbook for you according to the rules of [the official documentation](https://github.com/binance-exchange/binance-official-api-docs/blob/master/web-socket-streams.md#how-to-manage-a-local-order-book-correctly).

Specifically, `OrderBookHandlerBase` does the job.

We could get the managed `OrderBook` object by method `handler.orderbook(symbol)`.

```py
async def main():
    client = Client('api_key')

    # Unlike other handlers, we usually do not need to inherit `OrderBookHandlerBase`,
    #   unless we need to receive the raw payload of 'depthUpdate' message
    handler = OrderBookHandlerBase()

    client.handler(handler)
    await client.subscribe(SubType.ORDER_BOOK, 'BTCUSDT')

    # Get the reference of OrderBook object for 'BTCUSDT'
    orderbook = handler.orderbook('BTCUSDT')

    while True:
        # If the `retry_policy` never abandon a retry,
        #   the 'try' block could be emitted
        try:
            await orderbook.updated()
        except Exception as e:
            print('exception occurred')
        else:
            await doSomethingWith(orderbook.asks, orderbook.bids)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

loop.run_forever()
```

## OrderBook(symbol, **kwargs)

- **symbol** `str` the symbol name
- **kwargs**
  - **limit?** `int=100` limit of the orderbook
  - **client** `Client=None` the instance of `binance.Client`
  - **retry_policy?** `Callable[[int], (bool, int, bool)]` retry policy for depth snapshot which has the same mechanism as `Client::stream_retry_policy`

`OrderBook` is another public class that we could import from binance-sdk and you could also construct your own `OrderBook` instance.

```py
async def main():
    # PAY attention that `orderbook` should be run in an event loop
    orderbook = OrderBook('BTCUSDT', client=client)

    await orderbook.updated()

    print(orderbook.asks)
```

### orderbook.set_client(client) -> None

- **client** `Client` the instance of `binance.Client`

Set the client. If `client` is not specified in the constructor, then executing this method will make the orderbook to fetch the snapshot for the first time.

### orderbook.set_limit(limit) -> None

- **limit** `int`

Set depth limit which is used by [binance reset api](https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#order-book).

### orderbook.set_retry_policy(retry_policy) -> None

- **retry_policy** `Callable`

Set retry policy of the certain orderbook

### property `orderbook.ready` -> bool

There is a property getter in `orderbook` to detect whether the asks and bids are updated in the orderbook.

If there is a network malfunction of the stream which causing the gap between two depth update messages, `orderbook` will fetch a new snapshot from the server, and during that time and before we merge the snapshot, `orderbook.ready` is `False`.

### property `orderbook.asks` -> list
### property `orderbook.bids` -> list

Get asks and bids in ascending order.

### orderbook.update(payload) -> bool

- **payload** `dict` the data payload of the `depthUpdate` stream message

Returns `True` if the payload is valid and is updated to the orderbook, otherwise `False`

If the return value is `False`, the orderbook will automatically start fetching the snapshot

### await orderbook.fetch() -> None

Manually fetch the snapshot.

For most scenarios, you need **NOT** to call this method because once
there is an invalid payload, the orderbook will fetch the snapshot itself.

### await orderbook.updated() -> None

Wait for the next update of the orderbook.

We could also await `orderbook.updated()` to make sure the orderbook is ready.

If the orderbook fails to fetch depth snapshot for so many times which means the fetching is abanboned by the `retry_policy`, an `aiohttp` exception will be raised.

#### Listen to the updates of `orderbook`

```py
async def start_listening_updates(orderbook):
    # This is an infinite loop
    while True:
        await orderbook.updated()
        # do something

def start():
    return asyncio.create_task(start_listening_updates(orderbook))

task = start()

# If we want to stop listening
task.cancel()
```

## License

[MIT](LICENSE)
