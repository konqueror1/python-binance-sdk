from typing import (
    Union,
    Callable,
    Awaitable,
    Optional
)


APIResponse = Union[dict, list]

Timeout = Union[int, float]

Payload = Union[dict, list]

DictPayload = dict

ListPayload = dict

EventCallback = Callable[..., Optional[Awaitable[None]]]

WrappedEventCallback = Callable[..., Awaitable[None]]
