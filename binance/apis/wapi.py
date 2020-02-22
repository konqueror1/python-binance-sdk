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
        name = 'withdraw',
        path = 'withdraw',
        method = RequestMethod.POST,
        security_type = SecurityType.TRADE
    ),

    dict(
        name = 'get_deposit_history',
        path = 'depositHistory'
    ),

    dict(
        name = 'get_withdraw_history',
        path = 'withdrawHistory'
    ),

    dict(
        name = 'get_deposit_address',
        path = 'depositAddress'
    ),

    dict(
        name = 'get_account_status',
        path = 'accountStatus'
    ),

    dict(
        name   = 'get_system_status',
        path   = 'systemStatus',
        params = False,
        security_type = SecurityType.NONE
    ),

    dict(
        name = 'get_account_api_trading_status',
        path = 'apiTradingStatus'
    ),

    dict(
        name = 'get_dust_log',
        path = 'userAssetDribbletLog'
    ),

    dict(
        name = 'get_trade_fee',
        path = 'tradeFee'
    ),

    dict(
        name = 'get_asset_detail',
        path = 'assetDetail'
    ),

    dict(
        name = 'get_sub_accounts',
        path = 'sub-account/list'
    ),

    dict(
        name = 'get_sub_account_transfer_history',
        path = 'sub-account/transfer/history'
    ),

    dict(
        name = 'sub_account_transfer',
        path = 'sub-account/transfer',
        method = RequestMethod.POST,
        security_type = SecurityType.TRADE
    ),

    dict(
        name = 'get_sub_account_assets',
        path = 'sub-account/assets'
    ),

    dict(
        name = 'dust_transfer',
        path = 'asset/dust',
        prefix = PREFIX_SAPI,
        method = RequestMethod.POST,
        security_type = SecurityType.TRADE
    ),

    dict(
        name = 'get_assert_dividend_record',
        path = 'asset/assetDividend',
        prefix = PREFIX_SAPI
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
):
    def getter(self, **kwargs):
        uri = self._wapi_uri(path, version, prefix)
        ka = kwargs if params else {}

        return self._request(
            method,
            uri,
            security_type,
            **ka
        )

    setattr(Target, name, getter)

class WapiAPIGetters:
    def _wapi_uri(self, path, version, prefix=PREFIX_WAPI):
        return self._api_host + prefix + version + '/' + path + '.html'

for getter_setting in APIS:
    define_getter(WapiAPIGetters, **getter_setting)
