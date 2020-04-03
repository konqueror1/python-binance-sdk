from binance.processors import (
    AllMarketMiniTickersProcessor
)


def test_mini_ticker_processor():
    processor = AllMarketMiniTickersProcessor(None)

    assert processor.subscribe_param(None, None) == '!miniTicker@arr@1000ms'
    assert processor.subscribe_param(
        None, None, 2000
    ) == '!miniTicker@arr@2000ms'
