from typing import Awaitable
from binance.common.constants import (
    REST_API_VERSION,
    SecurityType,
    RequestMethod
)

PREFIX_WAPI = '/wapi/'
PREFIX_SAPI = '/sapi/'

# Ref:
# https://github.com/binance-exchange/binance-official-api-docs/blob/master/wapi-api.md
APIS = [

    # General Endpoints

    # see rest.py
    dict(
        name='withdraw',
        path='withdraw',
        method=RequestMethod.POST,
        security_type=SecurityType.TRADE
    ),

    dict(
        name='get_deposit_history',
        path='depositHistory'
    ),

    dict(
        name='get_withdraw_history',
        path='withdrawHistory'
    ),

    dict(
        name='get_deposit_address',
        path='depositAddress'
    ),

    dict(
        name='get_account_status',
        path='accountStatus'
    ),

    dict(
        name='get_system_status',
        path='systemStatus',
        params=False,
        security_type=SecurityType.NONE
    ),

    dict(
        name='get_account_api_trading_status',
        path='apiTradingStatus'
    ),

    dict(
        name='get_dust_log',
        path='userAssetDribbletLog'
    ),

    dict(
        name='get_trade_fee',
        path='tradeFee'
    ),

    dict(
        name='get_asset_detail',
        path='assetDetail'
    ),

    dict(
        name='get_sub_accounts',
        path='sub-account/list'
    ),

    dict(
        name='get_sub_account_transfer_history',
        path='sub-account/transfer/history'
    ),

    dict(
        name='sub_account_transfer',
        path='sub-account/transfer',
        method=RequestMethod.POST,
        security_type=SecurityType.TRADE
    ),

    dict(
        name='get_sub_account_assets',
        path='sub-account/assets'
    ),

    dict(
        name='dust_transfer',
        path='asset/dust',
        prefix=PREFIX_SAPI,
        method=RequestMethod.POST,
        security_type=SecurityType.TRADE
    ),

    dict(
        name='get_assert_dividend_record',
        path='asset/assetDividend',
        prefix=PREFIX_SAPI
    )
]


def define_getter(
    Target,
    name,
    path,
    prefix=PREFIX_WAPI,
    params=True,
    version=REST_API_VERSION,
    method=RequestMethod.GET,
    security_type=SecurityType.USER_DATA
) -> None:
    def getter(self, **kwargs) -> Awaitable:
        uri = self._wapi_uri(path, version, prefix)
        ka = kwargs if params else {}

        return self._request(
            method,
            uri,
            security_type,
            **ka
        )

    origin = getattr(Target, name)

    # Migrate the docstring to the new getter
    getter.__doc__ = origin.__doc__

    setattr(Target, name, getter)

# pylint: disable=no-member


class WapiAPIGetters:
    _api_host: str

    def _wapi_uri(self, path, version, prefix=PREFIX_WAPI) -> str:
        return self._api_host + prefix + version + '/' + path + '.html'

    def withdraw(self, **kwargs) -> Awaitable:
        """Submits a withdraw request.

        Weight: 1

        Args:
            asset (str):
            network (:obj:`str`, optional):
            address (str):
            addressTag (:obj:`str`, optional): Secondary address identifier for coins like XRP,XMR etc.
            amount (float):
            name (:obj:`str`, optional): Description of the address
            recvWindow (:obj:`long`, optional):
            timestamp (long):

        Returns:
            dict: For example::

                {
                    'msg': 'success',
                    'success': True,
                    'id': '7213fea8e94b4a5593d507237e5a555b'
                }

        """
        ...  # pragma: no cover

    def get_deposit_history(self, **kwargs) -> Awaitable:
        """Fetches deposit history.

        Weight: 1

        Args:
            asset (:obj:`str`, optional):
            status (:obj:`int`, optional): Defaults to 0. (0: pending, 6: credited but cannot withdraw, 1: success)
            startTime (:obj:`long`, optional):
            endTime (:obj:`long`, optional):
            recvWindow (:obj:`long`, optional):
            timestamp (long):

        Returns:
            dict: For example::

                {
                    'withdrawList': [
                        {
                            'id': '7213fea8e94b4a5593d507237e5a555b',
                            'amount': 0.99,
                            'transactionFee': 0.01,
                            'address': '0x6915f16f8791d0a1cc2bf47c13a6b2a92000504b',
                            'asset': 'ETH',
                            'txId': '0xdf33b22bdb2b28b1f75ccd201a4a4m6e7g83jy5fc5d5a9d1340961598cfcb0a1',
                            'applyTime': 1508198532000,
                            'status': 4
                        },
                        {
                            'id': '7213fea8e94b4a5534ggsd237e5a555b',
                            'amount': 999.9999,
                            'transactionFee': 0.0001,
                            'address': '463tWEBn5XZJSxLU34r6g7h8jtxuNcDbjLSjkn3XAXHCbLrTTErJrBWYgHJQyrCwkNgYvyV3z8zctJLPCZy24jvb3NiTcTJ',
                            'addressTag': '342341222',
                            'txId': 'b3c6219639c8ae3f9cf010cdc24fw7f7yt8j1e063f9b4bd1a05cb44c4b6e2509',
                            'asset': 'XMR',
                            'applyTime': 1508198532000,
                            'status': 4
                        }
                    ],
                    'success': True
                }
        """
        ...  # pragma: no cover

    def get_withdraw_history(self, **kwargs) -> Awaitable:
        """Fetches withdraw history.

        Args:
            asset (:obj:`str`, optional):
            status (:obj:`int`, optional): Defaults to 0. (0: Email Sent, 1: Cancelled, 2: Awaiting Approval, 3: Rejected, 4: Processing, 5: Failure, 6: Completed)
            startTime (:obj:`long`, optional):
            endTime (:obj:`long`, optional):
            recvWindow (:obj:`long`, optional):
            timestamp (long):

        Returns:
            dict: For example::

                {
                    'withdrawList': [
                        {
                            'id': '7213fea8e94b4a5593d507237e5a555b',
                            'amount': 0.99,
                            'transactionFee': 0.01,
                            'address': '0x6915f16f8791d0a1cc2bf47c13a6b2a92000504b',
                            'asset': 'ETH',
                            'txId': '0xdf33b22bdb2b28b1f75ccd201a4a4m6e7g83jy5fc5d5a9d1340961598cfcb0a1',
                            'applyTime': 1508198532000,
                            'status': 4
                        },
                        {
                            'id': '7213fea8e94b4a5534ggsd237e5a555b',
                            'amount': 999.9999,
                            'transactionFee': 0.0001,
                            'address': '463tWEBn5XZJSxLU34r6g7h8jtxuNcDbjLSjkn3XAXHCbLrTTErJrBWYgHJQyrCwkNgYvyV3z8zctJLPCZy24jvb3NiTcTJ',
                            'addressTag': '342341222',
                            'txId': 'b3c6219639c8ae3f9cf010cdc24fw7f7yt8j1e063f9b4bd1a05cb44c4b6e2509',
                            'asset': 'XMR',
                            'applyTime': 1508198532000,
                            'status': 4
                        }
                    ],
                    'success': True
                }
        """
        ...  # pragma: no cover

    def get_deposit_address(self, **kwargs) -> Awaitable:
        """Fetches deposit address.

        Weight: 1

        Args:
            asset (str):
            status (:obj:`bool`, optional):
            recvWindow (:obj:`long`, optional):
            timestamp (long):

        Returns:
            dict: For example::

                {
                    'address': '0x6915f16f8791d0a1cc2bf47c13a6b2a92000504b',
                    'success': True,
                    'addressTag': '1231212',
                    'asset': 'BNB'
                }
        """
        ...  # pragma: no cover

    def get_account_status(self, **kwargs) -> Awaitable:
        """Fetches account status detail.

        Args:
            recvWindow (:obj:`long`, optional):
            timestamp (long):

        Returns:
            dict: For example::

                {
                    'msg': 'Order failed:Low Order fill rate! Will be reactivated after 5 minutes.',
                    'success': True,
                    'objs': [
                        '5'
                    ]
                }
        """
        ...  # pragma: no cover

    def get_system_status(self) -> Awaitable:
        """Fetches system status.

        Returns:
            dict: For example::

                {
                    'status': 0,    # 0: normal，1：system maintenance
                    'msg': 'normal' # normal or system maintenance
                }
        """
        ...  # pragma: no cover

    def get_account_api_trading_status(self, **kwargs) -> Awaitable:
        """Fetches account api trading status detail.

        Args:
            recvWindow (:obj:`long`, optional):
            timestamp (long):

        Returns:
            dict: For example::

                {
                    'success': True,  # Query result
                    'status': {  # API trading status detail
                        'isLocked': False,   # API trading function is locked or not
                        'plannedRecoverTime': 0,  # If API trading function is locked, this is the planned recover time
                        'triggerCondition': {
                            'GCR': 150,  # Number of GTC orders
                            'IFER': 150,  # Number of FOK / IOC orders
                            'UFR': 300  # Number of orders
                        },
                        'indicators': {  # The indicators updated every 30 seconds
                            'BTCUSDT': [  # The symbol
                                {
                                    'i': 'UFR',  # Unfilled Ratio (UFR)
                                    'c': 20,  # Count of all orders
                                    'v': 0.05,  # Current UFR value
                                    't': 0.995  # Trigger UFR value
                                },
                                {
                                    'i': 'IFER',  # IOC / FOK Expiration Ratio(IFER)
                                    'c': 20,  # Count of FOK / IOC orders
                                    'v': 0.99,  # Current IFER value
                                    't': 0.99  # Trigger IFER value
                                },
                                {
                                    'i': 'GCR',  # GTC Cancellation Ratio(GCR)
                                    'c': 20,  # Count of GTC orders
                                    'v': 0.99,  # Current GCR value
                                    't': 0.99  # Trigger GCR value
                                }
                            ],
                            'ETHUSDT': [
                                # ...
                            ]
                        },
                        'updateTime': 1547630471725  # The query result return time
                    }
                }
        """
        ...  # pragma: no cover

    def get_dust_log(self, **kwargs) -> Awaitable:
        """Fetches small amounts of assets exchanged BNB records.

        Args:
            recvWindow (:obj:`long`, optional):
            timestamp (long):

        Returns:
            dict: For example::

                {
                    'success': True,
                    'results': {
                        'total': 2,  # Total counts of exchange
                        'rows': [
                            {
                                'transfered_total': '0.00132256',  # Total transfered BNB amount for this exchange.
                                'service_charge_total': '0.00002699',  # Total service charge amount for this exchange.
                                'tran_id': 4359321,
                                'logs': [  # Details of  this exchange.
                                    {
                                        'tranId': 4359321,
                                        'serviceChargeAmount': '0.000009',
                                        'uid': '10000015',
                                        'amount': '0.0009',
                                        'operateTime': '2018-05-03 17:07:04',
                                        'transferedAmount': '0.000441',
                                        'fromAsset': 'USDT'
                                    },
                                    {
                                        'tranId': 4359321,
                                        'serviceChargeAmount': '0.00001799',
                                        'uid': '10000015',
                                        'amount': '0.0009',
                                        'operateTime': '2018-05-03 17:07:04',
                                        'transferedAmount': '0.00088156',
                                        'fromAsset': 'ETH'
                                    }
                                ],
                                'operate_time': '2018-05-03 17:07:04'  # The time of this exchange.
                            },
                            {
                                'transfered_total': '0.00058795',
                                'service_charge_total': '0.000012',
                                'tran_id': 4357015,
                                'logs': [  # Details of  this exchange.
                                    {
                                        'tranId': 4357015,
                                        'serviceChargeAmount': '0.00001',
                                        'uid': '10000015',
                                        'amount': '0.001',
                                        'operateTime': '2018-05-02 13:52:24',
                                        'transferedAmount': '0.00049',
                                        'fromAsset': 'USDT'
                                    },
                                    {
                                        'tranId': 4357015,
                                        'serviceChargeAmount': '0.000002',
                                        'uid': '10000015',
                                        'amount': '0.0001',
                                        'operateTime': '2018-05-02 13:51:11',
                                        'transferedAmount': '0.00009795',
                                        'fromAsset': 'ETH'
                                    }
                                ],
                                'operate_time': '2018-05-02 13:51:11'
                            }
                        ]
                    }
                }
        """
        ...  # pragma: no cover

    def get_trade_fee(self, **kwargs) -> Awaitable:
        """Fetches trade fee.

        Args:
            recvWindow (:obj:`long`, optional):
            timestamp (long):
            symbol (:obj:`str`):

        Returns:
            dict: For example::

                {
                    'tradeFee': [{
                        'symbol': 'ADABNB',
                        'maker': 0.9000,
                        'taker': 1.0000
                    }, {
                        'symbol': 'BNBBTC',
                        'maker': 0.3000,
                        'taker': 0.3000
                    }],
                    'success': True
                }
        """
        ...  # pragma: no cover

    def get_asset_detail(self, **kwargs) -> Awaitable:
        """Fetches asset detail.

        Args:
            recvWindow (:obj:`long`, optional):
            timestamp (long):

        Returns:
            dict: For example::

                {
                    'success': True,
                    'assetDetail': {
                        'CTR': {
                            'minWithdrawAmount': '70.00000000',  # min withdraw amount
                            'depositStatus': False,  # deposit status
                            'withdrawFee': 35,  # withdraw fee
                            'withdrawStatus': True,  # withdraw status
                            'depositTip': 'Delisted, Deposit Suspended'  # reason
                        },
                        'SKY': {
                            'minWithdrawAmount': '0.02000000',
                            'depositStatus': True,
                            'withdrawFee': 0.01,
                            'withdrawStatus': True
                        }
                    }
                }
        """
        ...  # pragma: no cover

    def get_sub_accounts(self, **kwargs) -> Awaitable:
        """Fetches sub account list.

        Args:
            email (:obj:`str`, optional)
            status (:obj:`str`, optional): Sub-account status: `enabled` or `disabled`
            page (:obj:`int`, optional): Defaults to 1
            limit (:obj:`int`, optional): Defaults to 500
            recvWindow (:obj:`long`, optional):
            timestamp (long):

        Returns:
            dict: For example::

                {
                    'success': True,
                    'subAccounts': [
                        {
                            'email': '123@test.com',
                            'status': 'enabled',
                            'activated': True,
                            'mobile': '91605290',
                            'gAuth': True,
                            'createTime': 1544433328000
                        },
                        {
                            'email': '321@test.com',
                            'status': 'disabled',
                            'activated': True,
                            'mobile': '22501238',
                            'gAuth': True,
                            'createTime': 1544433328000
                        }
                    ]
                }
        """
        ...  # pragma: no cover

    def get_sub_account_transfer_history(self, **kwargs) -> Awaitable:
        """Fetches transfer history list

        Args:
            email (:obj:`str`, optional)
            startTime (:obj:`long`, optional): Default return the history with in 100 days
            endTime (:obj:`long`, optional): Default return the history with in 100 days
            page (:obj:`int`, optional): Defaults to 1
            limit (:obj:`int`, optional): Defaults to 500
            recvWindow (:obj:`long`, optional):
            timestamp (long):

        Returns:
            dict: For example::

                {
                    'success': True,
                    'transfers': [
                        {
                            'from': 'aaa@test.com',
                            'to': 'bbb@test.com',
                            'asset': 'BTC',
                            'qty': '1',
                            'time': 1544433328000
                        },
                        {
                            'from': 'bbb@test.com',
                            'to': 'ccc@test.com',
                            'asset': 'ETH',
                            'qty': '2',
                            'time': 1544433328000
                        }
                    ]
                }
        """
        ...  # pragma: no cover

    def sub_account_transfer(self, **kwargs) -> Awaitable:
        """Executes sub-account transfer

        Args:
            fromEmail (str): Sender email
            toEmail (str): Recipient email
            asset (str):
            amount (float):
            recvWindow (:obj:`long`, optional):
            timestamp (long):

        Returns:
            dict: For example::

                {
                    'success': True,
                    'txnId': '2966662589'
                }
        """
        ...  # pragma: no cover

    def get_sub_account_assets(self, **kwargs) -> Awaitable:
        """Fetches sub-account assets

        Args:
            email (str): Sub account email
            symbol (:obj:`str`, optional):
            recvWindow (:obj:`long`, optional):
            timestamp (long):

        Returns:
            dict: For example::

                {
                    'success': True,
                    'balances': [
                        {
                            'asset': 'ADA',
                            'free': 10000,
                            'locked': 0
                        },
                        {
                            'asset': 'BNB',
                            'free': 10003,
                            'locked': 0
                        }
                    ]
                }
        """
        ...  # pragma: no cover

    def dust_transfer(self, **kwargs) -> Awaitable:
        """Converts dust assets to BNB.

        Args:
            asset (list): list of the assets being converted.
            recvWindow (:obj:`long`, optional):
            timestamp (long):

        Returns:
            dict: For example::

                {
                    'totalServiceCharge': '0.02102542',
                    'totalTransfered': '1.05127099',
                    'transferResult': [
                        {
                            'amount': '0.03000000',
                            'fromAsset': 'ETH',
                            'operateTime': 1563368549307,
                            'serviceChargeAmount': '0.00500000',
                            'tranId': 2970932918,
                            'transferedAmount': '0.25000000'
                        },
                        {
                            'amount': '0.09000000',
                            'fromAsset': 'LTC',
                            'operateTime': 1563368549404,
                            'serviceChargeAmount': '0.01548000',
                            'tranId': 2970932918,
                            'transferedAmount': '0.77400000'
                        }
                    ]
                }
        """
        ...  # pragma: no cover

    def get_assert_dividend_record(self, **kwargs) -> Awaitable:
        """Gets asset dividend record.

        Args:
            asset (:obj:`str`, optional):
            startTime (:obj:`long`, optional):
            endTime (:obj:`long`, optional):
            recvWindow (:obj:`long`, optional):
            timestamp (long):

        Returns:
            dict: For example::

                {
                    'rows': [
                        {
                            'amount': '10.00000000',
                            'asset': 'BHFT',
                            'divTime': 1563189166000,
                            'enInfo': 'BHFT distribution',
                            'tranId': 2968885920
                        },
                        {
                            'amount': '10.00000000',
                            'asset': 'BHFT',
                            'divTime': 1563189165000,
                            'enInfo': 'BHFT distribution',
                            'tranId': 2968885920
                        }
                    ],
                    'total': 2
                }
        """
        ...  # pragma: no cover


for getter_setting in APIS:
    define_getter(WapiAPIGetters, **getter_setting)
