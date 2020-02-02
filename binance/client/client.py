from .client_base import ClientBase
from .client_getters import ClientGetters
from binance.subscribe.manager import SubscriptionManager

class Client(ClientBase, ClientGetters, SubscriptionManager):
    @classmethod
    async def create(cls, api_key='', api_secret='', requests_params=None):
        self = cls(api_key, api_secret, requests_params)
        await self._get('ping')
        return self
