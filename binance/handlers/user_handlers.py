from .handlers import Handler


__all__ = (
    'AccountInfoHandlerBase',
    'AccountPositionHandlerBase',
    'BalanceUpdateHandlerBase',
    'OrderUpdateHandlerBase',
    'OrderListStatusHandlerBase'
)


class SimpleHandler(Handler):
    def receive(self, msg):
        return msg


class AccountInfoHandlerBase(SimpleHandler):
    pass


class AccountPositionHandlerBase(SimpleHandler):
    pass


class BalanceUpdateHandlerBase(SimpleHandler):
    pass


class OrderUpdateHandlerBase(SimpleHandler):
    pass


class OrderListStatusHandlerBase(SimpleHandler):
    pass
