from abc import ABC, abstractmethod
import pandas as pd

__all__ = [
    'AggTradeHandlerBase',
    'OrderBookHandlerBase',
    'KlineHandlerBase',
    'TickerHandlerBase',
    'MiniTickerHandlerBase'
]

class HandlerBase(ABC):
    @abstractmethod
    def receive(self, res):
        pass

class AggTradeHandlerBase(HandlerBase):
    pass

class OrderBookHandlerBase(HandlerBase):
    pass

class KlineHandlerBase(HandlerBase):
    pass

TICKER_COLUMNS_MAP = {
    'E': 'time',
    's': 'symbol',
    'p': 'price',
    'P': 'percent',
    'w': 'weighted_average_price',
    'x': 'first_trade_price',
    'Q': 'last_quantity',
    'b': 'best_bid_price',
    'B': 'best_bid_quantity',
    'o': 'open',
    'h': 'high',
    'l': 'low',
    'c': 'close',
    'v': 'volume',
    'q': 'quote_volume',
    'O': 'stat_open_time',
    'C': 'stat_close_time',
    'F': 'first_trade_id',
    'L': 'last_trade_id',
    'n': 'total_trades'
}

TICKER_COLUMNS = TICKER_COLUMNS_MAP.keys()

class TickerHandlerBase(HandlerBase):
    def receive(self, res):
        return pd.DataFrame(
            res, columns=TICKER_COLUMNS, index=[0]
        ).rename(columns=TICKER_COLUMNS_MAP)

class MiniTickerHandlerBase(HandlerBase):
    pass

# class UserHandlerBase(object):
#     pass
