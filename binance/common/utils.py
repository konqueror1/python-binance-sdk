import json
import inspect
from typing import (
    Any
)

from .constants import ERROR_PREFIX


def make_list(subject: Any) -> list:
    return subject if isinstance(subject, list) else [subject]


def err_msg(string, *args) -> str:
    return ERROR_PREFIX + string % args


def json_stringify(obj) -> str:
    return json.dumps(obj, separators=(',', ':'))


def normalize_symbol(symbol: str, upper: bool = False) -> str:
    symbol = symbol.replace('_', '')
    return symbol.upper() if upper else symbol.lower()


async def wrap_coroutine(ret):
    if inspect.iscoroutine(ret):
        return await ret
    else:
        return ret
