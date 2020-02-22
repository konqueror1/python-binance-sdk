# MIT License

# Copyright (c) 2017 sammchardy

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import aiohttp
import asyncio
import hashlib
import hmac
import time
from operator import itemgetter

from binance.common.exceptions import (
    APIKeyNotDefinedException,
    APISecretNotDefinedException,
    StatusException,
    InvalidResponseException
)

from binance.common.constants import (
    HEADER_API_KEY,
    SecurityType
)

def sort_params(data):
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

KEY_REQUEST_PARAMS = 'requests_params'
KEY_FORCE_PARAMS = 'force_params'

class ClientBase:
    def _init_api_session(self, need_api_key):
        loop = asyncio.get_event_loop()
        headers = self._get_headers(need_api_key)

        session = aiohttp.ClientSession(
            loop=loop,
            headers=headers
        )
        return session

    def _get_headers(self, need_api_key):
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'binance-sdk'
        }

        if need_api_key:
            headers[HEADER_API_KEY] = self._api_key

        return headers

    def _get_request_kwargs(self, method, need_signed, **data):
        # Usually, `data` is the data param for aiohttp

        kwargs = dict(
            # set default requests timeout
            # TODO: no hard coding
            timeout = 10
        )

        # add global requests params for aiohttp
        if self._requests_params:
            kwargs.update(self._requests_params)

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

        kwargs[
            'params' if force_params or method == 'get' else 'data'
        ] = sorted_data

        return kwargs

    def _generate_signature(self, data):
        ordered_data = sort_params(data)
        query_string = '&'.join(["{}={}".format(d[0], d[1]) for d in ordered_data])

        m = hmac.new(
            self._api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256)

        return m.hexdigest()

    async def _handle_response(self, response):
        if not str(response.status).startswith('2'):
            raise StatusException(response, await response.text())
        try:
            return await response.json()
        except ValueError:
            raise InvalidResponseException(response, await response.text())

    # self._request('get', uri, symbol='BTCUSDT')
    async def _request(self,
        method,
        uri,
        security_type=SecurityType.NONE,
        **kwargs
    ):
        need_api_key, need_signed = security_type

        if need_api_key and not self._api_key:
            raise APIKeyNotDefinedException(uri)

        if need_signed and not self._api_secret:
            raise APISecretNotDefinedException(uri)

        req_kwargs = self._get_request_kwargs(
            method, need_signed, **kwargs)

        async with self._init_api_session(need_api_key) as session:
            async with getattr(session, method)(uri, **req_kwargs) as response:
                return await self._handle_response(response)

    async def get(self, uri, **kwargs):
        return await self._request('get', uri, **kwargs)

    async def post(self, uri, **kwargs):
        return await self._request('post', uri, **kwargs)

    async def put(self, uri, **kwargs):
        return await self._request('put', uri, **kwargs)

    async def delete(self, uri, **kwargs):
        return await self._request('delete', uri, **kwargs)
