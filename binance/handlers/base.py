import importlib

from binance.common.exceptions import ReuseHandlerException

pd = None

class HandlerBase(object):
    def __init__(self):
        self._client = None

    def set_client(self, client):
        if self._client:
            # If a handler used in more than one client,
            #   there will be conflicts
            raise ReuseHandlerException(self)

        self._client = client

    def _receive(self, res, index=[0]):
        return pd.DataFrame(
            res, columns=self.COLUMNS, index=index
        ).rename(columns=self.COLUMNS_MAP)

    # The real method to receive payload which dispatched from processor
    def receiveDispatch(self, payload):
        return self.receive(payload)

try:
    pd = importlib.import_module('pandas')
    HandlerBase.receive = lambda self, res: self._receive(res)

except ModuleNotFoundError:
    # If pandas is not installed
    HandlerBase.receive = lambda self, res: res
except Exception as e:
    raise e
