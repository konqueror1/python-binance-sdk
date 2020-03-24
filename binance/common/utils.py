import json
import inspect

from .constants import ERROR_PREFIX


def make_list(subject):
    if not subject:
        return []

    return subject if isinstance(subject, list) else [subject]


def err_msg(string, *args):
    return ERROR_PREFIX + string % args


def json_stringify(obj):
    return json.dumps(obj, separators=(',', ':'))


def normalize_symbol(symbol, upper=False):
    symbol = symbol.replace('_', '')
    return symbol.upper() if upper else symbol.lower()


async def wrap_coroutine(ret):
    if inspect.iscoroutine(ret):
        return await ret
    else:
        return ret
