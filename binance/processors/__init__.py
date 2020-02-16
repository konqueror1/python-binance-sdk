from .processors import *
from .user_processor import UserProcessor

__all__ = [
    'PROCESSORS',
    'ExceptionProcessor'
]

PROCESSORS = [
    KlineProcessor,
    TradeProcessor,
    AggTradeProcessor,
    OrderBookProcessor,
    MiniTickerProcessor,
    TickerProcessor,
    AllMarketMiniTickersProcessor,
    AllMarketTickersProcessor,
    UserProcessor
]
