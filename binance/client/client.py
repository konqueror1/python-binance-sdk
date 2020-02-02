from .client_base import ClientBase
from .client_getters import ClientGetters

class Client(ClientBase, ClientGetters):
    @classmethod
    async def create(cls, api_key='', api_secret='', requests_params=None):
        self = cls(api_key, api_secret, requests_params)
        await self.ping()
        return self
