[![Build Status](https://travis-ci.org/kaelzhang/python-binance-sdk.svg?branch=master)](https://travis-ci.org/kaelzhang/python-binance-sdk)
[![Coverage](https://codecov.io/gh/kaelzhang/python-binance-sdk/branch/master/graph/badge.svg)](https://codecov.io/gh/kaelzhang/python-binance-sdk)

# binance-sdk

Unofficial Binance SDK for python 3.7+

- Using `pandas.DataFrame`

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
from binance import TickerHandlerBase, RET_OK

# Start receiving websocket data
client.start()

class TickerPrinter(TickerHandlerBase):
    def receive(self, res):
        code, ticker_df = super(TickerPrinter, self).receive(res)
        if code != RET_OK:
            return ret_code, ticker_df

        print(ticker_df)

client.set_handler(TickerPrinter())

async def close_after_5_minutes():
    await asyncio.sleep(5 * 60)
    client.close()

asyncio.run(close_after_5_minutes())

# It will print the ticker dataframe during 5 minutes
```

## License

[MIT](LICENSE)
