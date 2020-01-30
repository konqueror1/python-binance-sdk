import aiohttp
import asyncio
import requests

from binance.common.helpers import interval_to_milliseconds, convert_ts_str
from .exceptions import BinanceAPIException, BinanceRequestException, BinanceWithdrawException
from .base import BaseClient

class Client(BaseClient):

    @classmethod
    async def create(cls, api_key='', api_secret='', requests_params=None):
        self = cls(api_key, api_secret, requests_params)
        await self.ping()
        return self

    def _init_session(self):
        loop = asyncio.get_event_loop()
        session = aiohttp.ClientSession(
            loop=loop,
            headers=self._get_headers()
        )
        return session

    async def _request(self, method, uri, signed, force_params=False, **kwargs):
        kwargs = self._get_request_kwargs(method, signed, force_params, **kwargs)
        print(method, uri, signed, kwargs)
        async with self._init_session() as session:
            async with getattr(session, method)(uri, **kwargs) as response:
                return await self._handle_response(response)

    async def _handle_response(self, response):
        """Internal helper for handling API responses from the Binance server.
        Raises the appropriate exceptions when necessary; otherwise, returns the
        response.
        """
        if not str(response.status).startswith('2'):
            raise BinanceAPIException(response, response.status, await response.text())
        try:
            return await response.json()
        except ValueError:
            txt = await response.text()
            raise BinanceRequestException('Invalid Response: {}'.format(txt))

    async def _request_api(self, method, path, signed=False, version=BaseClient.PUBLIC_API_VERSION, **kwargs):
        uri = self._create_api_uri(path, signed, version)
        return await self._request(method, uri, signed, **kwargs)

    async def _request_withdraw_api(self, method, path, signed=False, **kwargs):
        uri = self._create_withdraw_api_uri(path)
        return await self._request(method, uri, signed, True, **kwargs)

    async def _request_website(self, method, path, signed=False, **kwargs):
        uri = self._create_website_uri(path)
        return await self._request(method, uri, signed, **kwargs)

    async def _get(self, path, signed=False, version=BaseClient.PUBLIC_API_VERSION, **kwargs):
        return await self._request_api('get', path, signed, version, **kwargs)

    async def _post(self, path, signed=False, version=BaseClient.PUBLIC_API_VERSION, **kwargs):
        return await self._request_api('post', path, signed, version, **kwargs)

    async def _put(self, path, signed=False, version=BaseClient.PUBLIC_API_VERSION, **kwargs):
        return await self._request_api('put', path, signed, version, **kwargs)

    async def _delete(self, path, signed=False, version=BaseClient.PUBLIC_API_VERSION, **kwargs):
        return await self._request_api('delete', path, signed, version, **kwargs)

    # Exchange Endpoints

    async def get_products(self):
        products = await self._request_website('get', 'exchange/public/product')
        return products

    async def get_exchange_info(self):
        return await self._get('exchangeInfo')

    async def get_symbol_info(self, symbol):
        res = await self.get_exchange_info()

        for item in res['symbols']:
            if item['symbol'] == symbol.upper():
                return item

        return None

    # General Endpoints

    async def ping(self):
        return await self._get('ping')

    async def get_server_time(self):
        return await self._get('time')

    # Market Data Endpoints

    async def get_all_tickers(self):
        return await self._get('ticker/allPrices')

    async def get_orderbook_tickers(self):
        return await self._get('ticker/allBookTickers')

    async def get_order_book(self, **params):
        return await self._get('depth', data=params)

    async def get_recent_trades(self, **params):
        return await self._get('trades', data=params)

    async def get_historical_trades(self, **params):
        return await self._get('historicalTrades', data=params)

    async def get_aggregate_trades(self, **params):
        return await self._get('aggTrades', data=params)

    async def aggregate_trade_iter(self, symbol, start_str=None, last_id=None):
        if start_str is not None and last_id is not None:
            raise ValueError(
                'start_time and last_id may not be simultaneously specified.')

        # If there's no last_id, get one.
        if last_id is None:
            # Without a last_id, we actually need the first trade.  Normally,
            # we'd get rid of it. See the next loop.
            if start_str is None:
                trades = await self.get_aggregate_trades(symbol=symbol, fromId=0)
            else:
                # The difference between startTime and endTime should be less
                # or equal than an hour and the result set should contain at
                # least one trade.
                start_ts = convert_ts_str(start_str)
                # If the resulting set is empty (i.e. no trades in that interval)
                # then we just move forward hour by hour until we find at least one
                # trade or reach present moment
                while True:
                    end_ts = start_ts + (60 * 60 * 1000)
                    trades = await self.get_aggregate_trades(
                        symbol=symbol,
                        startTime=start_ts,
                        endTime=end_ts)
                    if len(trades) > 0:
                        break
                    # If we reach present moment and find no trades then there is
                    # nothing to iterate, so we're done
                    if end_ts > int(time.time() * 1000):
                        return
                    start_ts = end_ts
            for t in trades:
                yield t
            last_id = trades[-1][self.AGG_ID]

        while True:
            # There is no need to wait between queries, to avoid hitting the
            # rate limit. We're using blocking IO, and as long as we're the
            # only thread running calls like this, Binance will automatically
            # add the right delay time on their end, forcing us to wait for
            # data. That really simplifies this function's job. Binance is
            # fucking awesome.
            trades = await self.get_aggregate_trades(symbol=symbol, fromId=last_id)
            # fromId=n returns a set starting with id n, but we already have
            # that one. So get rid of the first item in the result set.
            trades = trades[1:]
            if len(trades) == 0:
                return
            for t in trades:
                yield t
            last_id = trades[-1][self.AGG_ID]

    async def get_klines(self, **params):
        return await self._get('klines', data=params)

    async def _get_earliest_valid_timestamp(self, symbol, interval):
        kline = await self.get_klines(
            symbol=symbol,
            interval=interval,
            limit=1,
            startTime=0,
            endTime=int(time.time() * 1000)
        )
        return kline[0][0]

    async def get_historical_klines(self, symbol, interval, start_str, end_str=None, limit=500):
        # init our list
        output_data = []

        # convert interval to useful value in seconds
        timeframe = interval_to_milliseconds(interval)

        # convert our date strings to milliseconds
        start_ts = convert_ts_str(start_str)

        # establish first available start timestamp
        first_valid_ts = await self._get_earliest_valid_timestamp(symbol, interval)
        start_ts = max(start_ts, first_valid_ts)

        # if an end time was passed convert it
        end_ts = convert_ts_str(end_str)

        idx = 0
        while True:
            # fetch the klines from start_ts up to max 500 entries or the end_ts if set
            temp_data = await self.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit,
                startTime=start_ts,
                endTime=end_ts
            )

            # handle the case where exactly the limit amount of data was returned last loop
            if not len(temp_data):
                break

            # append this loops data to our output data
            output_data += temp_data

            # set our start timestamp using the last value in the array
            start_ts = temp_data[-1][0]

            idx += 1
            # check if we received less than the required limit and exit the loop
            if len(temp_data) < limit:
                # exit the while loop
                break

            # increment next call by our timeframe
            start_ts += timeframe

            # sleep after every 3rd call to be kind to the API
            if idx % 3 == 0:
                await asyncio.sleep(1)

        return output_data

    async def get_historical_klines_generator(self, symbol, interval, start_str, end_str=None, limit=500):
        # convert interval to useful value in seconds
        timeframe = interval_to_milliseconds(interval)

        # convert our date strings to milliseconds
        start_ts = convert_ts_str(start_str)

        # establish first available start timestamp
        first_valid_ts = await self._get_earliest_valid_timestamp(symbol, interval)
        start_ts = max(start_ts, first_valid_ts)

        # if an end time was passed convert it
        end_ts = convert_ts_str(end_str)

        idx = 0
        while True:
            # fetch the klines from start_ts up to max 500 entries or the end_ts if set
            output_data = await self.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit,
                startTime=start_ts,
                endTime=end_ts
            )

            # handle the case where exactly the limit amount of data was returned last loop
            if not len(output_data):
                break

            # yield data
            for o in output_data:
                yield o

            # set our start timestamp using the last value in the array
            start_ts = output_data[-1][0]

            idx += 1
            # check if we received less than the required limit and exit the loop
            if len(output_data) < limit:
                # exit the while loop
                break

            # increment next call by our timeframe
            start_ts += timeframe

            # sleep after every 3rd call to be kind to the API
            if idx % 3 == 0:
                await asyncio.sleep(1)

    async def get_ticker(self, **params):
        return await self._get('ticker/24hr', data=params)

    async def get_symbol_ticker(self, **params):
        return await self._get('ticker/price', data=params, version=self.PRIVATE_API_VERSION)

    async def get_orderbook_ticker(self, **params):
        return await self._get('ticker/bookTicker', data=params, version=self.PRIVATE_API_VERSION)

    # Account Endpoints

    async def create_order(self, **params):
        return await self._post('order', True, data=params)

    async def order_limit(self, timeInForce=BaseClient.TIME_IN_FORCE_GTC, **params):
        params.update({
            'type': self.ORDER_TYPE_LIMIT,
            'timeInForce': timeInForce
        })
        return await self.create_order(**params)

    async def order_limit_buy(self, timeInForce=BaseClient.TIME_IN_FORCE_GTC, **params):
        params.update({
            'side': self.SIDE_BUY,
        })
        return await self.order_limit(timeInForce=timeInForce, **params)

    async def order_limit_sell(self, timeInForce=BaseClient.TIME_IN_FORCE_GTC, **params):
        params.update({
            'side': self.SIDE_SELL
        })
        return await self.order_limit(timeInForce=timeInForce, **params)

    async def order_market(self, **params):
        params.update({
            'type': self.ORDER_TYPE_MARKET
        })
        return await self.create_order(**params)

    async def order_market_buy(self, **params):
        params.update({
            'side': self.SIDE_BUY
        })
        return await self.order_market(**params)

    async def order_market_sell(self, **params):
        params.update({
            'side': self.SIDE_SELL
        })
        return await self.order_market(**params)

    async def create_test_order(self, **params):
        return await self._post('order/test', True, data=params)

    async def get_order(self, **params):
        return await self._get('order', True, data=params)

    async def get_all_orders(self, **params):
        return await self._get('allOrders', True, data=params)

    async def cancel_order(self, **params):
        return await self._delete('order', True, data=params)

    async def get_open_orders(self, **params):
        return await self._get('openOrders', True, data=params)

    # User Stream Endpoints
    async def get_account(self, **params):
        return await self._get('account', True, data=params)

    async def get_asset_balance(self, asset, **params):
        res = await self.get_account(**params)
        # find asset balance in list of balances
        if "balances" in res:
            for bal in res['balances']:
                if bal['asset'].lower() == asset.lower():
                    return bal
        return None

    async def get_my_trades(self, **params):
        return await self._get('myTrades', True, data=params)

    async def get_system_status(self):
        return await self._request_withdraw_api('get', 'systemStatus.html')

    async def get_account_status(self, **params):
        res = await self._request_withdraw_api('get', 'accountStatus.html', True, data=params)
        if not res['success']:
            raise BinanceWithdrawException(res['msg'])
        return res

    # Withdraw Endpoints

    async def withdraw(self, **params):
        # force a name for the withdrawal if one not set
        if 'asset' in params and 'name' not in params:
            params['name'] = params['asset']
        res = await self._request_withdraw_api('post', 'withdraw.html', True, data=params)
        if not res['success']:
            raise BinanceWithdrawException(res['msg'])
        return res

    async def get_deposit_history(self, **params):
        return await self._request_withdraw_api('get', 'depositHistory.html', True, data=params)

    async def get_withdraw_history(self, **params):
        return await self._request_withdraw_api('get', 'withdrawHistory.html', True, data=params)

    async def get_deposit_address(self, **params):
        return await self._request_withdraw_api('get', 'depositAddress.html', True, data=params)

    async def get_withdraw_fee(self, **params):
        return await self._request_withdraw_api('get', 'withdrawFee.html', True, data=params)

    # User Stream Endpoints

    async def stream_get_listen_key(self):
        res = await self._post('userDataStream', False, data={})
        return res['listenKey']

    async def stream_keepalive(self, listenKey):
        params = {
            'listenKey': listenKey
        }
        return await self._put('userDataStream', False, data=params)

    async def stream_close(self, listenKey):
        params = {
            'listenKey': listenKey
        }
        return await self._delete('userDataStream', False, data=params)
