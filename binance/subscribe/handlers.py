__all__ = [
    'AggTradeHandlerBase',
    'OrderBookHandlerBase',
    'KlineHandlerBase',
    'TickerHandlerBase',
    'MiniTickerHandlerBase'
]

class HandlerBase(object):
    def receive(self, res):
        """receive response callback function"""
        return 0, None

class AggTradeHandlerBase(HandlerBase):
    pass

class OrderBookHandlerBase(HandlerBase):
    pass

class KlineHandlerBase(HandlerBase):
    pass

class TickerHandlerBase(HandlerBase):
    pass

class MiniTickerHandlerBase(HandlerBase):
    pass

# class UserHandlerBase(object):
#     pass
