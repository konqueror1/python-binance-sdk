import json
import inspect
import warnings
from typing import (
    Any,
    Optional
)

from .constants import MSG_PREFIX
from .types import (
    EventCallback,
    WrappedEventCallback
)


def make_list(subject: Any) -> list:
    return subject if isinstance(subject, list) else [subject]


def format_msg(string, *args) -> str:
    return MSG_PREFIX + string % args


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


def wrap_event_callback(
    fn: Optional[EventCallback],
    event_name: str,
    required: bool
) -> Optional[WrappedEventCallback]:
    if fn is None:
        if required:
            raise ValueError(
                format_msg('event callback `%s` is required', event_name)
            )

        return

    async def callback(*args):
        try:
            await wrap_coroutine(fn(*args))
        except Exception as e:
            # This is a bug which is blamed to the user and
            # should be fixed.
            # So use warnings.
            warnings.warn(
                format_msg("""`%s` raises:
%s
And you should fix this""", event_name, e),
                RuntimeWarning
            )

    return callback
