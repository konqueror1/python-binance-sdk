from typing import List

from binance.common.exceptions import ReuseHandlerException
from binance.common.types import Payload


class Handler:
    """The handler class to receive stream messages.

    Most usually, except `OrderBookHandlerBase`, we need to override the `receive()` method::

        class MyTickerHandler(TickerHandlerBase):
            def receive(self, msg):
                print('ticker', msg)
    """

    COLUMNS = None
    COLUMNS_MAP = None

    def _receive(self, *args):
        ...  # pragma: no cover

    def receive(self, msg):
        ...  # pragma: no cover

    def __init__(self) -> None:
        self._client = None

    def set_client(self, client) -> None:
        if self._client:
            # If a handler used in more than one client,
            #   there will be conflicts
            raise ReuseHandlerException(self)

        self._client = client

    # The real method to receive payload which dispatched from processor
    def receiveDispatch(self, payload):
        return self.receive(payload)


try:
    import pandas as pd

    def _receive(
        self,
        payload: Payload,
        index: List[int] = [0]
    ) -> pd.DataFrame:
        return pd.DataFrame(
            payload, columns=self.COLUMNS, index=index
        ).rename(columns=self.COLUMNS_MAP)

    Handler._receive = _receive
    Handler.receive = lambda self, msg: self._receive(msg)

    Handler.receive.__doc__ = """Receives a single message from the stream.

    This method is usually invoked by subclass::

        class MyTickerHandler(TickerHandlerBase):
            def receive(msg):
                # df is a pandas.DataFrame
                df = super().receive(msg)
                print(df)

    Args:
        msg (list or dict): The stream message

    Returns:
        pandas.DataFrame: the DataFrame converted from `msg` with columns renamed.
    """

except ModuleNotFoundError:  # pragma: no cover
    # If pandas is not installed
    Handler.receive = lambda self, payload: payload

    Handler.receive.__doc__ = """Most usually, you do not need to call this method.
    """
