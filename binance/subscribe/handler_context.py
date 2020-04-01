import asyncio
import itertools

from binance.processors import PROCESSORS, ExceptionProcessor
from binance.common.constants import (
    RET_OK,
    RET_ERROR,
    SubType
)
from binance.common.exceptions import (
    InvalidSubParamsException,
    UnsupportedSubTypeException
)

from binance.common.utils import (
    make_list,
    wrap_coroutine
)


class HandlerContext:
    PROCESSORS = PROCESSORS

    def __init__(self, client):
        self._handler_table = {}
        self._processors = [Factory(client) for Factory in self.PROCESSORS]
        self._processor_cache = {}
        self._exception_processor = ExceptionProcessor(client)

    def set_handler(self, handler):
        if self._exception_processor.is_handler_type(handler):
            self._exception_processor.add_handler(handler)
            return RET_OK

        for processor in self._processors:
            if processor.is_handler_type(handler):
                processor.add_handler(handler)
                return RET_OK

        return RET_ERROR

    # client.subscribe(subtype_needs_no_param_or_has_default_param)
    # -> client.subscribe(SubType.ALL_MARKET_MINI_TICKERS)

    # client.subscribe(subtype, param)
    # -> client.subscribe(SubType.TICKER, 'BTCUSDT')

    # client.subscribe(subtypes, params)
    # -> client.subscribe(
    #   [SubType.TICKER, SubType.ORDER_BOOK],
    #   ['BTCUSDT', 'BNBUSDT']
    # )

    # client.subscribe((subtype, param), *subtype_param_pairs)
    # -> client.subscribe(
    #       (SubType.TICKER, 'BNBUSDT)
    # )
    async def subscribe_params(self, subscribe, *args):
        # Subs is a Tuple[tuple]
        subs = args if type(args[0]) is tuple else (args,)
        tasks = []

        for subtype_param in subs:
            length = len(subtype_param)
            prefix = None

            # subtype without params
            # ('allMarketMiniTickers',)
            if length == 1:
                args_iter = itertools.product(make_list(subtype_param[0]))
            # ('trade', 'BNBUSDT')
            # (['trade'], ['BNBUSDT'])
            elif length == 2:
                args_iter = itertools.product(
                    make_list(subtype_param[0]),
                    make_list(subtype_param[1])
                )

            # Only kline has three args for now
            elif length == 3 and subtype_param[0] == SubType.KLINE:
                prefix = SubType.KLINE
                args_iter = itertools.product(
                    make_list(subtype_param[1]),
                    make_list(subtype_param[2])
                )

            else:
                raise InvalidSubParamsException('please check the document')

            for partial_args in args_iter:
                tasks.append(
                    self._subscribe_param(
                        subscribe, *partial_args
                    ) if prefix is None else self._subscribe_param(
                        subscribe, prefix, *partial_args
                    )
                )

        return await asyncio.gather(*tasks)

    async def _subscribe_param(self, subscribe, *args):
        processor = self._get_processor(args[0])
        return await wrap_coroutine(processor.subscribe_param(subscribe, *args))

    def _get_processor(
        self,
        subtype: SubType
    ):
        processor = self._processor_cache.get(subtype)
        if processor:
            return processor

        for p in self._processors:
            if p.is_subtype(subtype):
                self._processor_cache[subtype] = p
                return p

        raise UnsupportedSubTypeException(subtype)

    async def _receive(self, msg):
        for processor in self._processors:
            is_payload, payload = processor.is_message_type(msg)

            if is_payload:
                await processor.dispatch(payload)

    async def receive(self, msg):
        try:
            await self._receive(msg)
        except Exception as e:
            await self._exception_processor.dispatch(e)
