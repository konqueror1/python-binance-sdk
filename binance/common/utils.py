import json
import inspect

from .constants import ERROR_PREFIX


# TODO: make it simpler
def make_list(l):
    ret = []
    if not l:
        return ret

    tmp = l if isinstance(l, list) else [l]
    [ret.append(x) for x in tmp if x not in ret]
    return ret


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
