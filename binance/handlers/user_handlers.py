from .handlers import Handler


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
