#!/usr/bin/python3

# Copyright (c) 2023 Calin Culianu <calin.culianu@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


"""Test vector for CashTokens encoding/decoding"""

import random
import unittest

from .. import token

TOKEN_PREFIX_TEST_CASES_VALID = [
    {
        "prefix": "efaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa1001",
        "data": {
            "amount": "1",
            "category": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        }
    },
    {
        "prefix": "ef21430000000000000000000000000000000000000000000000000000000034121001",
        "data": {
            "amount": "1",
            "category": "1234000000000000000000000000000000000000000000000000000000004321"
        }
    },
    {
        "prefix": "ef21436587090000000000000000000000000000000000000000000090785634121001",
        "data": {
            "amount": "1",
            "category": "1234567890000000000000000000000000000000000000000000000987654321"
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb1001",
        "data": {
            "amount": "1",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb10fc",
        "data": {
            "amount": "252",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb10fdfd00",
        "data": {
            "amount": "253",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb10fdffff",
        "data": {
            "amount": "65535",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb10fe00000100",
        "data": {
            "amount": "65536",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb10fe01000100",
        "data": {
            "amount": "65537",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb10feffffffff",
        "data": {
            "amount": "4294967295",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb10ff0000000001000000",
        "data": {
            "amount": "4294967296",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb10ff0100000001000000",
        "data": {
            "amount": "4294967297",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb10ffffffffffffffff7f",
        "data": {
            "amount": "9223372036854775807",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb20",
        "data": {
            "amount": "0",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "",
                "capability": "none"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb3001",
        "data": {
            "amount": "1",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "",
                "capability": "none"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb30fc",
        "data": {
            "amount": "252",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "",
                "capability": "none"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb30fdfd00",
        "data": {
            "amount": "253",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "",
                "capability": "none"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb30fdffff",
        "data": {
            "amount": "65535",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "",
                "capability": "none"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb30fe00000100",
        "data": {
            "amount": "65536",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "",
                "capability": "none"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb30feffffffff",
        "data": {
            "amount": "4294967295",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "",
                "capability": "none"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb30ff0000000001000000",
        "data": {
            "amount": "4294967296",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "",
                "capability": "none"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb30ffffffffffffffff7f",
        "data": {
            "amount": "9223372036854775807",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "",
                "capability": "none"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb6001cc",
        "data": {
            "amount": "0",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "cc",
                "capability": "none"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb60051234567890",
        "data": {
            "amount": "0",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "1234567890",
                "capability": "none"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb7001cc01",
        "data": {
            "amount": "1",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "cc",
                "capability": "none"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb7001ccfc",
        "data": {
            "amount": "252",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "cc",
                "capability": "none"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb7001ccfdfd00",
        "data": {
            "amount": "253",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "cc",
                "capability": "none"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb7001ccfdffff",
        "data": {
            "amount": "65535",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "cc",
                "capability": "none"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb7001ccfe00000100",
        "data": {
            "amount": "65536",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "cc",
                "capability": "none"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb7001ccfeffffffff",
        "data": {
            "amount": "4294967295",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "cc",
                "capability": "none"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb7001ccff0000000001000000",
        "data": {
            "amount": "4294967296",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "cc",
                "capability": "none"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb7001ccffffffffffffffff7f",
        "data": {
            "amount": "9223372036854775807",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "cc",
                "capability": "none"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb700accccccccccccccccccccfdffff",
        "data": {
            "amount": "65535",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "cccccccccccccccccccc",
                "capability": "none"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb7028cccccccccccccccccccccccccccccc"
                  "ccccccccccccccccccccccccccccccccccccccccccccccccccfe00000100",
        "data": {
            "amount": "65536",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
                "capability": "none"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb7029cccccccccccccccccccccccccccccc"
                  "ccccccccccccccccccccccccccccccccccccccccccccccccccccfe00000100",
        "data": {
            "amount": "65536",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
                "capability": "none"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb60fdfd00cccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
        "data": {
            "amount": "0",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
                "capability": "none"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb70fdfd00cccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccfe00000100",
        "data": {
            "amount": "65536",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
                "capability": "none"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb70fde903cccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccfe00000100",
        "data": {
            "amount": "65536",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
                "capability": "none"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb21",
        "data": {
            "amount": "0",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "",
                "capability": "mutable"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb31feffffffff",
        "data": {
            "amount": "4294967295",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "",
                "capability": "mutable"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb6101cc",
        "data": {
            "amount": "0",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "cc",
                "capability": "mutable"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb7101ccff0000000001000000",
        "data": {
            "amount": "4294967296",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "cc",
                "capability": "mutable"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb7102ccccffffffffffffffff7f",
        "data": {
            "amount": "9223372036854775807",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "cccc",
                "capability": "mutable"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb710acccccccccccccccccccc01",
        "data": {
            "amount": "1",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "cccccccccccccccccccc",
                "capability": "mutable"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb7128cccccccccccccccccccccccccccccc"
                  "ccccccccccccccccccccccccccccccccccccccccccccccccccfc",
        "data": {
            "amount": "252",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
                "capability": "mutable"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb7129cccccccccccccccccccccccccccccc"
                  "ccccccccccccccccccccccccccccccccccccccccccccccccccccfc",
        "data": {
            "amount": "252",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
                "capability": "mutable"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb71fdfd00cccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc01",
        "data": {
            "amount": "1",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
                "capability": "mutable"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb22",
        "data": {
            "amount": "0",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "",
                "capability": "minting"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb3201",
        "data": {
            "amount": "1",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "",
                "capability": "minting"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb32fdfd00",
        "data": {
            "amount": "253",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "",
                "capability": "minting"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb32fe00000100",
        "data": {
            "amount": "65536",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "",
                "capability": "minting"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb32ff0000000001000000",
        "data": {
            "amount": "4294967296",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "",
                "capability": "minting"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb32ffffffffffffffff7f",
        "data": {
            "amount": "9223372036854775807",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "",
                "capability": "minting"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb6201cc",
        "data": {
            "amount": "0",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "cc",
                "capability": "minting"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb6229cccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccc",
        "data": {
            "amount": "0",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
                "capability": "minting"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb7201ccfdffff",
        "data": {
            "amount": "65535",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "cc",
                "capability": "minting"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb7202ccccfe00000100",
        "data": {
            "amount": "65536",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "cccc",
                "capability": "minting"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb720accccccccccccccccccccff01000000"
                  "01000000",
        "data": {
            "amount": "4294967297",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "cccccccccccccccccccc",
                "capability": "minting"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb7228cccccccccccccccccccccccccccccc"
                  "ccccccccccccccccccccccccccccccccccccccccccccccccccffffffffffffffff7f",
        "data": {
            "amount": "9223372036854775807",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
                "capability": "minting"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb7229cccccccccccccccccccccccccccccc"
                  "ccccccccccccccccccccccccccccccccccccccccccccccccccccffffffffffffffff7f",
        "data": {
            "amount": "9223372036854775807",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
                "capability": "minting"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb62fdfd00cccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
        "data": {
            "amount": "0",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
                "capability": "minting"
            }
        }
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb72fdfd00cccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                  "ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccfe00000100",
        "data": {
            "amount": "65536",
            "category": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "nft": {
                "commitment": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
                              "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
                "capability": "minting"
            }
        }
    }
]

TOKEN_PREFIX_TEST_CASES_INVALID = [
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb00",
        "error": "Invalid token prefix: must encode at least one token. Bitfield: 0b0",
        "bchn_exception_message": "Invalid token bitfield: 0x00"
    },
    {
        "prefix": "ef",
        "error": "Invalid token prefix: insufficient length. The minimum possible length is 34. Missing bytes: 33",
        "bchn_exception_message": "end of data"
    },
    {
        "prefix": "efbbbbbbbb1001",
        "error": "Invalid token prefix: insufficient length. The minimum possible length is 34. Missing bytes: 27",
        "bchn_exception_message": "end of data"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        "error": "Invalid token prefix: insufficient length. The minimum possible length is 34. Missing bytes: 1",
        "bchn_exception_message": "end of data"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb80",
        "error": "Invalid token prefix: reserved bit is set. Bitfield: 0b10000000",
        "bchn_exception_message": "Invalid token bitfield: 0x80"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbba0",
        "error": "Invalid token prefix: reserved bit is set. Bitfield: 0b10100000",
        "bchn_exception_message": "Invalid token bitfield: 0xa0"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb9001",
        "error": "Invalid token prefix: reserved bit is set. Bitfield: 0b10010000",
        "bchn_exception_message": "Invalid token bitfield: 0x90"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb23",
        "error": "Invalid token prefix: capability must be none (0), mutable (1), or minting (2). Capability value: 3",
        "bchn_exception_message": "Invalid token bitfield: 0x23"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb24",
        "error": "Invalid token prefix: capability must be none (0), mutable (1), or minting (2). Capability value: 4",
        "bchn_exception_message": "Invalid token bitfield: 0x24"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb25",
        "error": "Invalid token prefix: capability must be none (0), mutable (1), or minting (2). Capability value: 5",
        "bchn_exception_message": "Invalid token bitfield: 0x25"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb26",
        "error": "Invalid token prefix: capability must be none (0), mutable (1), or minting (2). Capability value: 6",
        "bchn_exception_message": "Invalid token bitfield: 0x26"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb27",
        "error": "Invalid token prefix: capability must be none (0), mutable (1), or minting (2). Capability value: 7",
        "bchn_exception_message": "Invalid token bitfield: 0x27"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb28",
        "error": "Invalid token prefix: capability must be none (0), mutable (1), or minting (2). Capability value: 8",
        "bchn_exception_message": "Invalid token bitfield: 0x28"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb29",
        "error": "Invalid token prefix: capability must be none (0), mutable (1), or minting (2). Capability value: 9",
        "bchn_exception_message": "Invalid token bitfield: 0x29"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb2a",
        "error": "Invalid token prefix: capability must be none (0), mutable (1), or minting (2). Capability value: 10",
        "bchn_exception_message": "Invalid token bitfield: 0x2a"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb2b",
        "error": "Invalid token prefix: capability must be none (0), mutable (1), or minting (2). Capability value: 11",
        "bchn_exception_message": "Invalid token bitfield: 0x2b"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb2c",
        "error": "Invalid token prefix: capability must be none (0), mutable (1), or minting (2). Capability value: 12",
        "bchn_exception_message": "Invalid token bitfield: 0x2c"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb2d",
        "error": "Invalid token prefix: capability must be none (0), mutable (1), or minting (2). Capability value: 13",
        "bchn_exception_message": "Invalid token bitfield: 0x2d"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb2e",
        "error": "Invalid token prefix: capability must be none (0), mutable (1), or minting (2). Capability value: 14",
        "bchn_exception_message": "Invalid token bitfield: 0x2e"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb2f",
        "error": "Invalid token prefix: capability must be none (0), mutable (1), or minting (2). Capability value: 15",
        "bchn_exception_message": "Invalid token bitfield: 0x2f"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb1101",
        "error": "Invalid token prefix: capability requires an NFT. Bitfield: 0b10001",
        "bchn_exception_message": "Invalid token bitfield: 0x11"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb1201",
        "error": "Invalid token prefix: capability requires an NFT. Bitfield: 0b10010",
        "bchn_exception_message": "Invalid token bitfield: 0x12"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb40",
        "error": "Invalid token prefix: commitment requires an NFT. Bitfield: 0b1000000",
        "bchn_exception_message": "Invalid token bitfield: 0x40"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb5001",
        "error": "Invalid token prefix: commitment requires an NFT. Bitfield: 0b1010000",
        "bchn_exception_message": "Invalid token bitfield: 0x50"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb60",
        "error": "Invalid token prefix: invalid non-fungible token commitment. Error reading CompactSize-prefixed bin: "
                 "invalid CompactSize. Error reading CompactSize: requires at least one byte.",
        "bchn_exception_message": "end of data"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb61",
        "error": "Invalid token prefix: invalid non-fungible token commitment. Error reading CompactSize-prefixed bin: "
                 "invalid CompactSize. Error reading CompactSize: requires at least one byte.",
        "bchn_exception_message": "end of data"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb62",
        "error": "Invalid token prefix: invalid non-fungible token commitment. Error reading CompactSize-prefixed bin: "
                 "invalid CompactSize. Error reading CompactSize: requires at least one byte.",
        "bchn_exception_message": "end of data"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb60fd0100cc",
        "error": "Invalid token prefix: invalid non-fungible token commitment. Error reading CompactSize-prefixed bin: "
                 "invalid CompactSize. Error reading CompactSize: CompactSize is not minimally encoded. Value: 1, "
                 "encoded length: 3, canonical length: 1",
        "bchn_exception_message": "non-canonical ReadCompactSize"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb60fe01000000cc",
        "error": "Invalid token prefix: invalid non-fungible token commitment. Error reading CompactSize-prefixed bin: "
                 "invalid CompactSize. Error reading CompactSize: CompactSize is not minimally encoded. Value: 1, "
                 "encoded length: 5, canonical length: 1",
        "bchn_exception_message": "non-canonical ReadCompactSize"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb60ff0100000000000000cc",
        "error": "Invalid token prefix: invalid non-fungible token commitment. Error reading CompactSize-prefixed bin: "
                 "invalid CompactSize. Error reading CompactSize: CompactSize is not minimally encoded. Value: 1, "
                 "encoded length: 9, canonical length: 1",
        "bchn_exception_message": "non-canonical ReadCompactSize"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb6000",
        "error": "Invalid token prefix: if encoded, commitment length must be greater than 0.",
        "bchn_exception_message": "token commitment may not be empty"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb700001",
        "error": "Invalid token prefix: if encoded, commitment length must be greater than 0.",
        "bchn_exception_message": "token commitment may not be empty"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb6001",
        "error": "Invalid token prefix: invalid non-fungible token commitment. Error reading CompactSize-prefixed bin: "
                 "insufficient bytes. Required bytes: 1, remaining bytes: 0",
        "bchn_exception_message": "end of data"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb6101",
        "error": "Invalid token prefix: invalid non-fungible token commitment. Error reading CompactSize-prefixed bin: "
                 "insufficient bytes. Required bytes: 1, remaining bytes: 0",
        "bchn_exception_message": "end of data"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb6102cc",
        "error": "Invalid token prefix: invalid non-fungible token commitment. Error reading CompactSize-prefixed bin: "
                 "insufficient bytes. Required bytes: 2, remaining bytes: 1",
        "bchn_exception_message": "end of data"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb6202cc",
        "error": "Invalid token prefix: invalid non-fungible token commitment. Error reading CompactSize-prefixed bin: "
                 "insufficient bytes. Required bytes: 2, remaining bytes: 1",
        "bchn_exception_message": "end of data"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb10",
        "error": "Invalid token prefix: invalid fungible token amount encoding. Error reading CompactSize: requires at "
                 "least one byte.",
        "bchn_exception_message": "end of data"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb10fd00",
        "error": "Invalid token prefix: invalid fungible token amount encoding. Error reading CompactSize: insufficient"
                 " bytes. CompactSize prefix 253 requires at least 3 bytes. Remaining bytes: 2",
        "bchn_exception_message": "end of data"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb10fe000000",
        "error": "Invalid token prefix: invalid fungible token amount encoding. Error reading CompactSize: insufficient"
                 " bytes. CompactSize prefix 254 requires at least 5 bytes. Remaining bytes: 4",
        "bchn_exception_message": "end of data"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb10ff00000000000000",
        "error": "Invalid token prefix: invalid fungible token amount encoding. Error reading CompactSize: insufficient"
                 " bytes. CompactSize prefix 255 requires at least 9 bytes. Remaining bytes: 8",
        "bchn_exception_message": "end of data"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb7001cc",
        "error": "Invalid token prefix: invalid fungible token amount encoding. Error reading CompactSize: requires at "
                 "least one byte.",
        "bchn_exception_message": "end of data"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb7001ccfd00",
        "error": "Invalid token prefix: invalid fungible token amount encoding. Error reading CompactSize: insufficient"
                 " bytes. CompactSize prefix 253 requires at least 3 bytes. Remaining bytes: 2",
        "bchn_exception_message": "end of data"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb7001ccfe000000",
        "error": "Invalid token prefix: invalid fungible token amount encoding. Error reading CompactSize: insufficient"
                 " bytes. CompactSize prefix 254 requires at least 5 bytes. Remaining bytes: 4",
        "bchn_exception_message": "end of data"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb7001ccff00000000000000",
        "error": "Invalid token prefix: invalid fungible token amount encoding. Error reading CompactSize: insufficient"
                 " bytes. CompactSize prefix 255 requires at least 9 bytes. Remaining bytes: 8",
        "bchn_exception_message": "end of data"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb30",
        "error": "Invalid token prefix: invalid fungible token amount encoding. Error reading CompactSize: requires at"
                 " least one byte.",
        "bchn_exception_message": "end of data"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb1000",
        "error": "Invalid token prefix: if encoded, fungible token amount must be greater than 0.",
        "bchn_exception_message": "token amount may not be 0"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb3000",
        "error": "Invalid token prefix: if encoded, fungible token amount must be greater than 0.",
        "bchn_exception_message": "token amount may not be 0"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb10fd0100",
        "error": "Invalid token prefix: invalid fungible token amount encoding. Error reading CompactSize: CompactSize "
                 "is not minimally encoded. Value: 1, encoded length: 3, canonical length: 1",
        "bchn_exception_message": "non-canonical ReadCompactSize"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb10fe01000000",
        "error": "Invalid token prefix: invalid fungible token amount encoding. Error reading CompactSize: CompactSize "
                 "is not minimally encoded. Value: 1, encoded length: 5, canonical length: 1",
        "bchn_exception_message": "non-canonical ReadCompactSize"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb10ff0100000000000000",
        "error": "Invalid token prefix: invalid fungible token amount encoding. Error reading CompactSize: CompactSize "
                 "is not minimally encoded. Value: 1, encoded length: 9, canonical length: 1",
        "bchn_exception_message": "non-canonical ReadCompactSize"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb30fd0100",
        "error": "Invalid token prefix: invalid fungible token amount encoding. Error reading CompactSize: CompactSize "
                 "is not minimally encoded. Value: 1, encoded length: 3, canonical length: 1",
        "bchn_exception_message": "non-canonical ReadCompactSize"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb30fe01000000",
        "error": "Invalid token prefix: invalid fungible token amount encoding. Error reading CompactSize: CompactSize "
                 "is not minimally encoded. Value: 1, encoded length: 5, canonical length: 1",
        "bchn_exception_message": "non-canonical ReadCompactSize"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb30ff0100000000000000",
        "error": "Invalid token prefix: invalid fungible token amount encoding. Error reading CompactSize: CompactSize "
                 "is not minimally encoded. Value: 1, encoded length: 9, canonical length: 1",
        "bchn_exception_message": "non-canonical ReadCompactSize"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb10ff0000000000000080",
        "error": "Invalid token prefix: exceeds maximum fungible token amount of 9223372036854775807. Encoded amount: "
                 "9223372036854775808",
        "bchn_exception_message": "amount out of range"
    },
    {
        "prefix": "efbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb30ff0000000000000080",
        "error": "Invalid token prefix: exceeds maximum fungible token amount of 9223372036854775807. Encoded amount: "
                 "9223372036854775808",
        "bchn_exception_message": "amount out of range"
    }
]


class TestTokens(unittest.TestCase):
    """Unit test class for CashTokens."""

    def test_encode_decode_valid(self):
        """Test whether valid tokens encode and decode properly, for all of the test cases."""
        for dd in TOKEN_PREFIX_TEST_CASES_VALID:
            ii = random.randint(0, 1)
            rand_spk = int.to_bytes(random.getrandbits(256), length=32, byteorder='little') if ii & 0x1 else b''
            prefix = bytes.fromhex(dd["prefix"])
            self.assertEqual(prefix[0:1], token.PREFIX_BYTE)
            wspk = prefix + rand_spk
            token_data, spk = token.unwrap_spk(wspk)
            self.assertEqual(token.wrap_spk(token_data, spk), wspk)
            self.assertEqual(token_data.serialize(), prefix[1:])
            data = dd["data"]
            self.assertEqual(rand_spk, spk)
            self.assertEqual(token_data.amount, int(data["amount"]))
            self.assertEqual(token_data.id_hex, data["category"])
            self.assertEqual(token_data.id, bytes.fromhex(data["category"])[::-1])
            self.assertEqual(bool(token_data.amount), token_data.has_amount())
            self.assertEqual(bool(len(token_data.commitment)), token_data.has_commitment_length())
            nft = data.get("nft")
            if nft is not None:
                assert token_data.has_nft()
                self.assertEqual(token_data.commitment.hex(), nft["commitment"])
                cap = nft["capability"]
                if cap == "minting":
                    assert token_data.is_minting_nft()
                    assert not token_data.is_mutable_nft()
                    assert not token_data.is_immutable_nft()
                    self.assertEqual(token_data.get_capability(), token.Capability.Minting)
                elif cap == "mutable":
                    assert not token_data.is_minting_nft()
                    assert token_data.is_mutable_nft()
                    assert not token_data.is_immutable_nft()
                    self.assertEqual(token_data.get_capability(), token.Capability.Mutable)
                elif cap == "none":
                    assert not token_data.is_minting_nft()
                    assert not token_data.is_mutable_nft()
                    assert token_data.is_immutable_nft()
                    self.assertEqual(token_data.get_capability(), token.Capability.NoCapability)
                else:
                    assert False, f"Unexpected capability: {cap}"
            else:
                assert not token_data.has_nft()
                self.assertEqual(token_data.get_capability(), token.Capability.NoCapability)
            # Test id_hex setter
            rand_id = int.to_bytes(random.getrandbits(256), length=32, byteorder='little')
            token_data.id_hex = rand_id_hex = rand_id[::-1].hex()
            self.assertEqual(token_data.id, rand_id)
            self.assertEqual(token_data.id_hex, rand_id_hex)

    def test_encode_decode_invalid(self):
        """Test that the invalid test cases fail to deserialize"""
        for i, dd in enumerate(TOKEN_PREFIX_TEST_CASES_INVALID):
            prefix = bytes.fromhex(dd["prefix"])
            self.assertEqual(prefix[0:1], token.PREFIX_BYTE)
            token_data = token.OutputData()
            with self.assertRaises(token.SerializationError):
                token_data.deserialize(buffer=prefix[1:])


if __name__ == '__main__':
    unittest.main()
