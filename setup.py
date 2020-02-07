import os
from setuptools import setup
from binance import __version__

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'binance-sdk',
    packages = ['binance'],
    version = __version__,
    author = 'Kael Zhang',
    author_email = 'i+pypi@kael.me',
    description = ('Binance Python SDK'),
    extras_require = {
        'pandas': ['pandas']
    },
    license = 'MIT',
    keywords = 'binance exchange sdk rest api bitcoin btc bnb ethereum eth neo',
    url = 'https://github.com/kaelzhang/python-binance-sdk',
    long_description=read('README.rst'),
    classifiers=[
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
    ]
)
