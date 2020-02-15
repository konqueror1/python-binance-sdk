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

from binance.common.exceptions import \
    APIKeyNotDefinedException, APISecretNotDefinedException, \
    StatusException, InvalidResponseException

def order_params(data):
    """Convert params to list with signature as last element

    :param data:
    :return:

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

class ClientBase(object):
    def _init_api_session(self):
        loop = asyncio.get_event_loop()
        session = aiohttp.ClientSession(
            loop=loop,
            headers=self._get_headers()
        )
        return session

    def _get_headers(self):
        return {
            'Accept': 'application/json',
            'User-Agent': 'binance-sdk',
            'X-MBX-APIKEY': self._api_key
        }

    def _get_request_kwargs(self, method, signed, force_params=False, **kwargs):
        # set default requests timeout
        kwargs['timeout'] = 10

        # add our global requests params
        if self._requests_params:
            kwargs.update(self._requests_params)

        data = kwargs.get('data', None)
        if data and isinstance(data, dict):
            kwargs['data'] = data

            # find any requests params passed and apply them
            if 'requests_params' in kwargs['data']:
                # merge requests params into kwargs
                kwargs.update(kwargs['data']['requests_params'])
                del(kwargs['data']['requests_params'])

        if signed:
            # generate signature
            kwargs['data']['timestamp'] = int(time.time() * 1000)
            kwargs['data']['signature'] = self._generate_signature(kwargs['data'])

        # sort get and post params to match signature order
        if data:
            # sort post params
            kwargs['data'] = order_params(kwargs['data'])

        # if get request assign data array to params value for requests lib
        if data and (method == 'get' or force_params):
            kwargs['params'] = kwargs['data']
            del(kwargs['data'])

        return kwargs

    def _generate_signature(self, data):
        ordered_data = order_params(data)
        query_string = '&'.join(["{}={}".format(d[0], d[1]) for d in ordered_data])

        m = hmac.new(
            self._api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256)

        return m.hexdigest()

    async def _handle_response(self, response):
        """Internal helper for handling API responses from the Binance server.
        Raises the appropriate exceptions when necessary; otherwise, returns the
        response.
        """
        if not str(response.status).startswith('2'):
            raise StatusException(response, await response.text())
        try:
            return await response.json()
        except ValueError:
            raise InvalidResponseException(response, await response.text())

    async def request(self, method, uri, signed, force_params=False, **kwargs):
        if not self._api_key:
            raise APIKeyNotDefinedException(uri)

        if signed and not self._api_secret:
            raise APISecretNotDefinedException(uri)

        kwargs = self._get_request_kwargs(
            method, signed, force_params, **kwargs)

        async with self._init_api_session() as session:
            async with getattr(session, method)(uri, **kwargs) as response:
                return await self._handle_response(response)

    async def get(self, uri, signed=False, **kwargs):
        return await self.request('get', uri, signed, **kwargs)

    async def post(self, uri, signed=False, **kwargs):
        return await self.request('post', uri, signed, **kwargs)

    async def put(self, uri, signed=False, **kwargs):
        return await self.request('put', uri, signed, **kwargs)

    async def delete(self, uri, signed=False, **kwargs):
        return await self.request('delete', uri, signed, **kwargs)
