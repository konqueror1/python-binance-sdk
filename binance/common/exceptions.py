# coding=utf-8

import json
from typing import (
    Any,
    Optional
)

from aiohttp import ClientResponse

from .utils import err_msg
from .constants import SubType


class UserStreamNotSubscribedException(Exception):
    def __str__(self) -> str:
        return err_msg('user stream is not subscribed')


class StreamDisconnectedException(Exception):
    def __init__(
        self,
        uri: str
    ) -> None:
        self.uri = uri

    def __str__(self) -> str:
        return err_msg(
            'stream "%s" is never connected or is abandoned after too many retries according to the `retry_policy`, run `stream.connect()`', self.uri)  # noqa:E501


class APIKeyNotDefinedException(Exception):
    def __init__(
        self,
        url: str
    ) -> None:
        self.url = url

    def __str__(self) -> str:
        return err_msg(
            'api_key is required for requesting "%s"', self.url)


class APISecretNotDefinedException(Exception):
    def __init__(
        self,
        url: str
    ) -> None:
        self.url = url

    def __str__(self) -> str:
        return err_msg(
            'api_secret is required for requesting "%s"', self.url)


class StatusException(Exception):
    def __init__(
        self,
        response: ClientResponse,
        text: str
    ) -> None:
        self.code = 0
        status = response.status

        if not str(status).startswith('5'):
            try:
                json_res = json.loads(text)
            except ValueError:
                self.message = f'Invalid JSON error message from Binance: {text}'  # noqa:E501
            else:
                self.code = json_res['code']
                self.message = json_res['msg']

        self.status = status
        self.response = response
        self.request = getattr(response, 'request', None)

    def __str__(self) -> str:  # pragma: no cover
        return err_msg('response error for "%s", status %s, code %s: %s',
                       self.response.url, self.status, self.code, self.message)


class InvalidResponseException(Exception):
    def __init__(
        self,
        response: ClientResponse,
        text: str
    ) -> None:
        self.response = response
        self.response_text = text

    def __str__(self) -> str:
        return err_msg('invalid response for "%s": %s',
                       self.response.url, self.response_text)


class InvalidSubParamsException(Exception):
    def __init__(
        self,
        message: str
    ) -> None:
        self.message = message

    def __str__(self) -> str:
        return err_msg('invalid subscribe params: %s', self.message)


class UnsupportedSubTypeException(Exception):
    def __init__(
        self,
        subtype: Any
    ) -> None:
        self.subtype = subtype

    def __str__(self) -> str:
        return err_msg('subtype "%s" is not supported', self.subtype)


class InvalidSubTypeParamException(Exception):
    def __init__(
        self,
        subtype: SubType,
        param_name: str,
        reason: str
    ) -> None:
        self.subtype = subtype
        self.param_name = param_name
        self.reason = reason

    def __str__(self) -> str:
        return err_msg('invalid param `%s` for subtype "%s", %s',
                       self.param_name, self.subtype, self.reason)


class InvalidHandlerException(Exception):
    def __init__(
        self,
        handler: Any
    ) -> None:
        self.handler = handler

    def __str__(self) -> str:
        return err_msg('invalid handler `%s`', self.handler)


class ReuseHandlerException(Exception):
    def __init__(
        self,
        handler: Any
    ) -> None:
        self.handler = handler

    def __str__(self) -> str:
        return err_msg(
            'handler `%s` should not be used in more than one clients',
            self.handler
        )


class OrderBookFetchAbandonedException(Exception):
    def __init__(
        self,
        symbol: str,
        reason: str,
        exception: Optional[Exception] = None
    ) -> None:
        self.symbol = symbol
        self.reason = reason
        self.exception = exception

    def __str__(self) -> str:
        return err_msg(
            'orderbook for `%s` failed to fetch snapshot and fetching is abandoned by retry policy, reason: %s',
            self.symbol,
            self.reason
        )
