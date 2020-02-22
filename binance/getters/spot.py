import asyncio
import time

from binance.common.utils import interval_to_milliseconds, convert_ts_str
from binance.common.constants import (
    PUBLIC_API_VERSION, WITHDRAW_API_VERSION, PRIVATE_API_VERSION
)

# SIDE_BUY = 'BUY'
# SIDE_SELL = 'SELL'

# ORDER_TYPE_LIMIT = 'LIMIT'
# ORDER_TYPE_MARKET = 'MARKET'

# TIME_IN_FORCE_GTC = 'GTC'  # Good till cancelled
# TIME_IN_FORCE_IOC = 'IOC'  # Immediate or cancel
# TIME_IN_FORCE_FOK = 'FOK'  # Fill or kill

# For accessing the data returned by Client.aggregate_trades().
# AGG_ID = 'a'

# APIS = [
#     dict(
#         name='ping',
#         path='ping'
#     ),
#     dict(
#         name=''
#     )
# ]

class SpotGetters(object):
    def _api_uri(self, path, version=PUBLIC_API_VERSION):
        return self._api_host + '/api/' + version + '/' + path

    def _private_api_uri(self, path, version=PRIVATE_API_VERSION):
        return self._api_uri(path, version)

    def _withdraw_api_uri(self, path, version=WITHDRAW_API_VERSION):
        return self._api_host + '/wapi/' + version + '/' + path

    def _website_uri(self, path):
        return self._website_host + '/' + path

    # General Endpoints

    async def ping(self):
        return await self.get(self._api_uri('ping'))

    async def get_server_time(self):
        return await self.get(self._api_uri('time'))

    # Exchange Endpoints

    async def get_exchange_info(self):
        return await self.get(self._api_uri('exchangeInfo'))

    async def get_symbol_info(self, symbol):
        res = await self.get_exchange_info()

        for item in res['symbols']:
            if item['symbol'] == symbol.upper():
                return item

        return None

    # Market Data Endpoints

    async def get_orderbook(self, **params):
        return await self.get(self._api_uri('depth'), data=params)

    async def get_recent_trades(self, **params):
        return await self.get(self._api_uri('trades'), data=params)

    async def get_historical_trades(self, **params):
        return await self.get(self._api_uri('historicalTrades'), data=params)

    async def get_aggregate_trades(self, **params):
        return await self.get(self._api_uri('aggTrades'), data=params)

    async def get_klines(self, **params):
        return await self.get(self._api_uri('klines'), data=params)

    # async def get_all_tickers(self):
    #     return await self.get(self._api_uri('ticker/allPrices'))

    # async def get_orderbook_tickers(self):
    #     return await self.get(self._api_uri('ticker/allBookTickers'))



    # async def aggregate_trade_iter(self, symbol, start_str=None, last_id=None):
    #     if start_str is not None and last_id is not None:
    #         raise ValueError(
    #             'start_time and last_id may not be simultaneously specified.')

    #     # If there's no last_id, get one.
    #     if last_id is None:
    #         # Without a last_id, we actually need the first trade.  Normally,
    #         # we'd get rid of it. See the next loop.
    #         if start_str is None:
    #             trades = await self.get_aggregate_trades(symbol=symbol, fromId=0)
    #         else:
    #             # The difference between startTime and endTime should be less
    #             # or equal than an hour and the result set should contain at
    #             # least one trade.
    #             start_ts = convert_ts_str(start_str)
    #             # If the resulting set is empty (i.e. no trades in that interval)
    #             # then we just move forward hour by hour until we find at least one
    #             # trade or reach present moment
    #             while True:
    #                 end_ts = start_ts + (60 * 60 * 1000)
    #                 trades = await self.get_aggregate_trades(
    #                     symbol=symbol,
    #                     startTime=start_ts,
    #                     endTime=end_ts)
    #                 if len(trades) > 0:
    #                     break
    #                 # If we reach present moment and find no trades then there is
    #                 # nothing to iterate, so we're done
    #                 if end_ts > int(time.time() * 1000):
    #                     return
    #                 start_ts = end_ts
    #         for t in trades:
    #             yield t
    #         last_id = trades[-1][AGG_ID]

    #     while True:
    #         # There is no need to wait between queries, to avoid hitting the
    #         # rate limit. We're using blocking IO, and as long as we're the
    #         # only thread running calls like this, Binance will automatically
    #         # add the right delay time on their end, forcing us to wait for
    #         # data. That really simplifies this function's job. Binance is
    #         # fucking awesome.
    #         trades = await self.get_aggregate_trades(symbol=symbol, fromId=last_id)
    #         # fromId=n returns a set starting with id n, but we already have
    #         # that one. So get rid of the first item in the result set.
    #         trades = trades[1:]
    #         if len(trades) == 0:
    #             return
    #         for t in trades:
    #             yield t
    #         last_id = trades[-1][AGG_ID]

    # async def _get_earliest_valid_timestamp(self, symbol, interval):
    #     kline = await self.get_klines(
    #         symbol=symbol,
    #         interval=interval,
    #         limit=1,
    #         startTime=0,
    #         endTime=int(time.time() * 1000)
    #     )
    #     return kline[0][0]

    # async def get_historical_klines(self, symbol, interval, start_str, end_str=None, limit=500):
    #     # init our list
    #     output_data = []

    #     # convert interval to useful value in seconds
    #     timeframe = interval_to_milliseconds(interval)

    #     # convert our date strings to milliseconds
    #     start_ts = convert_ts_str(start_str)

    #     # establish first available start timestamp
    #     first_valid_ts = await self._get_earliest_valid_timestamp(symbol, interval)
    #     start_ts = max(start_ts, first_valid_ts)

    #     # if an end time was passed convert it
    #     end_ts = convert_ts_str(end_str)

    #     idx = 0
    #     while True:
    #         # fetch the klines from start_ts up to max 500 entries or the end_ts if set
    #         temp_data = await self.get_klines(
    #             symbol=symbol,
    #             interval=interval,
    #             limit=limit,
    #             startTime=start_ts,
    #             endTime=end_ts
    #         )

    #         # handle the case where exactly the limit amount of data was returned last loop
    #         if not len(temp_data):
    #             break

    #         # append this loops data to our output data
    #         output_data += temp_data

    #         # set our start timestamp using the last value in the array
    #         start_ts = temp_data[-1][0]

    #         idx += 1
    #         # check if we received less than the required limit and exit the loop
    #         if len(temp_data) < limit:
    #             # exit the while loop
    #             break

    #         # increment next call by our timeframe
    #         start_ts += timeframe

    #         # sleep after every 3rd call to be kind to the API
    #         if idx % 3 == 0:
    #             await asyncio.sleep(1)

    #     return output_data

    # async def get_historical_klines_generator(self, symbol, interval, start_str, end_str=None, limit=500):
    #     # convert interval to useful value in seconds
    #     timeframe = interval_to_milliseconds(interval)

    #     # convert our date strings to milliseconds
    #     start_ts = convert_ts_str(start_str)

    #     # establish first available start timestamp
    #     first_valid_ts = await self._get_earliest_valid_timestamp(symbol, interval)
    #     start_ts = max(start_ts, first_valid_ts)

    #     # if an end time was passed convert it
    #     end_ts = convert_ts_str(end_str)

    #     idx = 0
    #     while True:
    #         # fetch the klines from start_ts up to max 500 entries or the end_ts if set
    #         output_data = await self.get_klines(
    #             symbol=symbol,
    #             interval=interval,
    #             limit=limit,
    #             startTime=start_ts,
    #             endTime=end_ts
    #         )

    #         # handle the case where exactly the limit amount of data was returned last loop
    #         if not len(output_data):
    #             break

    #         # yield data
    #         for o in output_data:
    #             yield o

    #         # set our start timestamp using the last value in the array
    #         start_ts = output_data[-1][0]

    #         idx += 1
    #         # check if we received less than the required limit and exit the loop
    #         if len(output_data) < limit:
    #             # exit the while loop
    #             break

    #         # increment next call by our timeframe
    #         start_ts += timeframe

    #         # sleep after every 3rd call to be kind to the API
    #         if idx % 3 == 0:
    #             await asyncio.sleep(1)

    # async def get_ticker(self, **params):
    #     return await self.get(self._api_uri('ticker/24hr'), data=params)

    # async def get_symbol_ticker(self, **params):
    #     return await self.get(
    #         self._private_api_uri('ticker/price'), data=params)

    # async def get_orderbook_ticker(self, **params):
    #     return await self.get(
    #         self._private_api_uri('ticker/bookTicker'), data=params)

    # # Account Endpoints

    # async def create_order(self, **params):
    #     return await self.post(
    #         self._private_api_uri('order'), True, data=params)

    # async def order_limit(self, timeInForce=TIME_IN_FORCE_GTC, **params):
    #     params.update({
    #         'type': ORDER_TYPE_LIMIT,
    #         'timeInForce': timeInForce
    #     })
    #     return await self.create_order(**params)

    # async def order_limit_buy(self, timeInForce=TIME_IN_FORCE_GTC, **params):
    #     params.update({
    #         'side': SIDE_BUY,
    #     })
    #     return await self.order_limit(timeInForce=timeInForce, **params)

    # async def order_limit_sell(self, timeInForce=TIME_IN_FORCE_GTC, **params):
    #     params.update({
    #         'side': SIDE_SELL
    #     })
    #     return await self.order_limit(timeInForce=timeInForce, **params)

    # async def order_market(self, **params):
    #     params.update({
    #         'type': ORDER_TYPE_MARKET
    #     })
    #     return await self.create_order(**params)

    # async def order_market_buy(self, **params):
    #     params.update({
    #         'side': SIDE_BUY
    #     })
    #     return await self.order_market(**params)

    # async def order_market_sell(self, **params):
    #     params.update({
    #         'side': SIDE_SELL
    #     })
    #     return await self.order_market(**params)

    # async def create_test_order(self, **params):
    #     return await self.post(
    #         self._private_api_uri('order/test'), True, data=params)

    # async def get_order(self, **params):
    #     return await self.get(self._private_api_uri('order'), True, data=params)

    # async def get_all_orders(self, **params):
    #     return await self.get(
    #         self._private_api_uri('allOrders'), True, data=params)

    # async def cancel_order(self, **params):
    #     return await self.delete(
    #         self._private_api_uri('order'), True, data=params)

    # async def get_open_orders(self, **params):
    #     return await self.get(
    #         self._private_api_uri('openOrders'), True, data=params)

    # # User Stream Endpoints
    # async def get_account(self, **params):
    #     return await self.get(
    #         self._private_api_uri('account'), True, data=params)

    # async def get_asset_balance(self, asset, **params):
    #     res = await self.get_account(**params)
    #     # find asset balance in list of balances
    #     if "balances" in res:
    #         for bal in res['balances']:
    #             if bal['asset'].lower() == asset.lower():
    #                 return bal
    #     return None

    # async def get_my_trades(self, **params):
    #     return await self.get(
    #         self._private_api_uri('myTrades'), True, data=params)

    # async def get_system_status(self):
    #     return await self.get(self._withdraw_api_uri('systemStatus.html'))

    # async def get_account_status(self, **params):
    #     return await self.get(
    #         self._withdraw_api_uri('accountStatus.html'), True, data=params)

    # # Withdraw Endpoints

    # async def withdraw(self, **params):
    #     # force a name for the withdrawal if one not set
    #     if 'asset' in params and 'name' not in params:
    #         params['name'] = params['asset']
    #     return await self.post(
    #         self._withdraw_api_uri('withdraw.html'), True, data=params)

    # async def get_deposit_history(self, **params):
    #     return await self.get(
    #         self._withdraw_api_uri('depositHistory.html'), True, data=params)

    # async def get_withdraw_history(self, **params):
    #     return await self.get(
    #         self._withdraw_api_uri('withdrawHistory.html'), True, data=params)

    # async def get_deposit_address(self, **params):
    #     return await self.get(
    #         self._withdraw_api_uri('depositAddress.html'), True, data=params)

    # async def get_withdraw_fee(self, **params):
    #     return await self.get(
    #         self._withdraw_api_uri('withdrawFee.html'), True, data=params)

    # # User Stream Endpoints

    # async def get_user_listen_key(self):
    #     res = await self.post(self._api_uri('userDataStream'), False, data={})
    #     return res['listenKey']

    # async def keepalive_listen_key(self, listenKey):
    #     params = {
    #         'listenKey': listenKey
    #     }
    #     return await self.put(
    #         self._api_uri('userDataStream'), False, data=params)

    # async def close_listen_key(self, listenKey):
    #     params = {
    #         'listenKey': listenKey
    #     }
    #     return await self.delete(
    #         self._api_uri('userDataStream'), False, data=params)
