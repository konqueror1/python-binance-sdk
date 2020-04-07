from .processors import (
    KlineProcessor,
    TradeProcessor,
    AggTradeProcessor,
    OrderBookProcessor,
    MiniTickerProcessor,
    TickerProcessor,
    AllMarketMiniTickersProcessor,
    AllMarketTickersProcessor,
    ExceptionProcessor
)

from .user_processor import UserProcessor


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
