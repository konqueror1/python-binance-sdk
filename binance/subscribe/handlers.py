__all__ = [
    'QuoteHandlerBase',
    'OrderBookHandlerBase',
    'CurrentKlineHandlerBase',
    'TickerHandlerBase'
]

class HandlerBase(object):
    def receive(self, res):
        """receive response callback function"""
        return 0, None

class QuoteHandlerBase(HandlerBase):
    pass

class OrderBookHandlerBase(HandlerBase):
    pass

class CurrentKlineHandlerBase(HandlerBase):
    pass

class TickerHandlerBase(HandlerBase):
    pass
