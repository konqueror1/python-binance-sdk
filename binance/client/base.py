import asyncio
import hashlib
import hmac
import time
from operator import itemgetter

from typing import (
    List,
    Dict,
    Awaitable,
    Optional,
    Any
)

from aiohttp import (
    ClientSession,
    ClientResponse
)

from binance.common.exceptions import (
    APIKeyNotDefinedException,
    APISecretNotDefinedException,
    StatusException,
    InvalidResponseException
)

from binance.common.constants import (
    HEADER_API_KEY,
    SecurityType,
    RequestMethod,
    APIResponse
)

# pylint: disable=no-member


def sort_params(data: dict) -> List[str]:
    """
    Convert params to list with signature as last element
    """
    has_signature = False
    params = []

    for key, value in data.items():
        if key == 'signature':
            has_signature = True
        else:
            params.append((key, str(value)))

    # sort parameters by key
    params.sort(key=itemgetter(0))

    if has_signature:
        params.append(('signature', data['signature']))

    return params


KEY_REQUEST_PARAMS = 'request_params'
KEY_FORCE_PARAMS = 'force_params'


def get_headers(
    api_key: Optional[str]
) -> Dict[str, str]:
    headers = {
        'Accept': 'application/json',
        'User-Agent': 'binance-sdk'
    }

    if api_key is not None:
        headers[HEADER_API_KEY] = api_key

    return headers


class ClientBase:
    _api_key: Optional[str]
    _api_secret: Optional[str]
    _request_params: Optional[dict]

    def _init_api_session(
        self,
        api_key: Optional[str]
    ) -> ClientSession:
        loop = asyncio.get_event_loop()

        session = ClientSession(
            loop=loop,
            headers=get_headers(api_key)
        )
        return session

    def _get_request_kwargs(
        self,
        method: RequestMethod,
        need_signed: bool,
        **data
    ) -> Dict[str, Any]:
        # Usually, `data` is the data param for aiohttp

        kwargs: Dict[str, Any] = dict(
            # set default requests timeout
            # TODO: no hard coding
            timeout=10
        )

        # add global requests params for aiohttp
        if self._request_params is not None:
            kwargs.update(self._request_params)

        # find any requests params passed and apply them
        if KEY_REQUEST_PARAMS in data:
            # merge requests params into kwargs
            kwargs.update(data[KEY_REQUEST_PARAMS])
            del data[KEY_REQUEST_PARAMS]

        force_params = False
        if KEY_FORCE_PARAMS in data:
            force_params = True
            del data[KEY_FORCE_PARAMS]

        if need_signed:
            # generate signature
            data['timestamp'] = int(time.time() * 1000)
            data['signature'] = self._generate_signature(data)

        sorted_data = sort_params(data)

        param_key = 'params' \
            if force_params or method == RequestMethod.GET else 'data'

        kwargs[param_key] = sorted_data

        return kwargs

    def _generate_signature(
        self,
        data: dict
    ) -> str:
        ordered_data = sort_params(data)

        query_string = '&'.join([
            f'{key}={value}'
            for key, value in ordered_data
        ])

        m = hmac.new(
            self._api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256)

        return m.hexdigest()

    async def _handle_response(
        self,
        response: ClientResponse
    ) -> APIResponse:
        if not str(response.status).startswith('2'):
            raise StatusException(response, await response.text())
        try:
            return await response.json()
        except ValueError:
            raise InvalidResponseException(response, await response.text())

    # self._request('get', uri, symbol='BTCUSDT')
    async def _request(
        self,
        method: RequestMethod,
        uri: str,
        security_type: SecurityType = SecurityType.NONE,
        **kwargs
    ) -> APIResponse:
        need_api_key, need_signed = security_type.value

        if need_api_key:
            if self._api_key is None:
                raise APIKeyNotDefinedException(uri)

            api_key = self._api_key
        else:
            api_key = None

        if need_signed and self._api_secret is None:
            raise APISecretNotDefinedException(uri)

        req_kwargs = self._get_request_kwargs(
            method, need_signed, **kwargs)

        async with self._init_api_session(api_key) as session:
            async with getattr(
                session, method.value
            )(uri, **req_kwargs) as response:
                return await self._handle_response(response)

    def get(self, uri, **kwargs) -> Awaitable[APIResponse]:
        """Sends a GET request.

        For details, see `client.post(uri, **kwargs)`
        """
        return self._request(RequestMethod.GET, uri, **kwargs)

    def post(self, uri, **kwargs) -> Awaitable[APIResponse]:
        """Sends a POST request.

        Args:
            uri (str): The absolute url to be requested.
            security_type (:obj:`SecurityType`, optional): The security type of the API of uri. Defaults to `SecurityType.NONE` which means the endpoint can be accessed freely.
            requests_params (:obj:`dict`, optional): Other params passed into `aiohttp::ClientSession::post()`.
            force_params (:obj:`bool`, optional): `True` to make ``**kwargs`` as querystring after the ``uri``. Defaults to `False`
            **kwargs: Arbitrary keyword arguments. For POST/PUT/DELETE requests, `kwargs` will be the request body if ``force_params`` is not `True` otherwise the querystring of the request url. For GET requests, `kwargs` will always be converted to querystring of the url.

        Returns:
            object: The server response JSON.

        Raises:
            StatusException: If the response status is not `2xx`.
            InvalidResponseException: If the response is not a valid JSON.
            APIKeyNotDefinedException: If the API endpoint requires a valid api key, but the api key is not defined for the client.
            APISecretNotDefinedException: If the API endpoint requires a valid signature, but the api secret is not defined for the client.
        """
        return self._request(RequestMethod.POST, uri, **kwargs)

    def put(self, uri, **kwargs) -> Awaitable[APIResponse]:
        """Sends a PUT request.

        For details, see `client.post(uri, **kwargs)`
        """
        return self._request(RequestMethod.PUT, uri, **kwargs)

    def delete(self, uri, **kwargs) -> Awaitable[APIResponse]:
        """Sends a DELETE request.

        For details, see `client.post(uri, **kwargs)`
        """
        return self._request(RequestMethod.DELETE, uri, **kwargs)
