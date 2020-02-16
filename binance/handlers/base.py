import importlib

pd = None

class HandlerBase(object):
    def __init__(self):
        self._client = None

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
