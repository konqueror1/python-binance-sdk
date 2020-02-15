# coding=utf-8

import json

from .utils import err_msg

class StreamAbandonedException(Exception):
    def __init__(self, uri):
        self.uri = uri

    def __str__(self):
        return err_msg(
            'websocket "%s" is abandoned after too many retries', self.url)

class APIKeyNotDefinedException(Exception):
    def __init__(self, url):
        self.url = url

    def __str__(self):
        return err_msg(
            'api_key is required for requesting "%s"', self.url)

class APISecretNotDefinedException(Exception):
    def __init__(self, url):
        self.url = url

    def __str__(self):
        return err_msg(
            'api_secret is required for requesting "%s"', self.url)

class StatusException(Exception):
    def __init__(self, response, text):
        self.code = 0
        status = response.status

        if not str(status).startswith('5'):
            try:
                json_res = json.loads(text)
            except ValueError:
                self.message = 'Invalid JSON error message from Binance: {}'.format(response.text)
            else:
                self.code = json_res['code']
                self.message = json_res['msg']

        self.status = status
        self.response = response
        self.request = getattr(response, 'request', None)

    def __str__(self):  # pragma: no cover
        return err_msg('response error for "%s", status %s, code %s: %s',
            self.response.url, self.status, self.code, self.message)

class WithdrawException(Exception):
    def __init__(self, message):
        if message == u'参数异常':
            message = 'Withdraw to this address through the website first'
        self.message = message

    def __str__(self):
        return err_msg('failed to withdraw: %s', self.message)


class InvalidResponseException(Exception):
    def __init__(self, response, text):
        self.response = response
        self.response_text = text

    def __str__(self):
        return err_msg('invalid response for "%s": %s',
            self.response.url, self.response_text)

class InvalidSubParamsException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return err_msg('invalid subscribe params: %s', self.message)

class UnsupportedSubTypeException(Exception):
    def __init__(self, subtype):
        self.subtype = subtype

    def __str__(self):
        return err_msg('subtype "%s" is not supported', self.subtype)

class InvalidSubTypeParamException(Exception):
    def __init__(self, subtype, param_name, reason):
        self.subtype = subtype
        self.param_name = param_name
        self.reason = reason

    def __str__(self):
        return err_msg('invalid param `%s` for subtype "%s", %s',
            self.param_name, self.subtype, self.reason)

class InvalidHandlerException(Exception):
    def __init__(self, handler):
        self.handler = handler

    def __str__(self):
        return err_msg('invalid handler `%s`', self.handler)
