__version__ = '0.0.0'

import sys

def _check_version_no_older(cur_ver, base_ver):
    cur_ver_parts = [int(n) for n in cur_ver.split('.')]
    base_ver_parts = [int(n) for n in base_ver.split('.')]
    return cur_ver_parts >= base_ver_parts

def _check_module(mod_name, package_name=None, version=None, version_getter=None, py_version=None):
    import importlib

    if package_name is None:
        package_name = mod_name

    if py_version is not None:
        if sys.version_info[0] != py_version:
            return

    try:
        mod = importlib.import_module(mod_name)
    except Exception:
        if version is None:
            print("Missing required package {}".format(package_name))
        else:
            print("Missing required package {} v{}".format(package_name, version))
        sys.exit(1)

    if version is not None:
        mod_version = version_getter(mod)
        if not _check_version_no_older(mod_version, version):
            print("The current version of package {} is {}, not compatible. You need use {} or newer.".format(package_name, mod_version, version))
            sys.exit(1)

_check_module('pandas')
# _check_module('python-binance', version='0.7.4')

from binance.client.client import Client
from binance.request.exceptions import *
