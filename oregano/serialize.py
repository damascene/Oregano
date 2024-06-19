#!/usr/bin/env python3
#
# Electron Cash - lightweight Bitcoin Cash client
# Based on Electrum Copyright (C) 2011 Thomas Voegtlin
# Copyright (C) 2023 The Electron Cash Developers
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""All utility functions related to serialization and deserialization of Bitcoin data."""

import struct
from typing import Optional, Union

from .util import to_bytes


class SerializationError(Exception):
    """ Thrown when there's a problem deserializing or serializing """


class BCDataStream:
    """ Work-alike python implementation of Bitcoin's CDataStream class. """

    def __init__(self, inp: Optional[Union[bytes, bytearray]] = None):
        self.input = inp
        self.read_cursor = 0

    def clear(self):
        self.input = None
        self.read_cursor = 0

    def write(self, _bytes: bytes):
        """ Initialize with string of _bytes. """
        if self.input is None:
            self.input = bytearray(_bytes)
        else:
            if not isinstance(self.input, bytearray):
                self.input = bytearray(self.input)
            self.input.extend(_bytes)

    def read_string(self, encoding='ascii'):
        # Strings are encoded depending on length:
        # 0 to 252 :  1-byte-length followed by bytes (if any)
        # 253 to 65,535 : byte'253' 2-byte-length followed by bytes
        # 65,536 to 4,294,967,295 : byte '254' 4-byte-length followed by bytes
        # ... and the Bitcoin client is coded to understand:
        # greater than 4,294,967,295 : byte '255' 8-byte-length followed by bytes of string
        # ... but I don't think it actually handles any strings that big.
        if self.input is None:
            raise SerializationError("call write(bytes) before trying to deserialize")

        length = self.read_compact_size()

        return self.read_bytes(length).decode(encoding)

    def write_string(self, string, encoding='ascii'):
        string = to_bytes(string, encoding)
        # Length-encoded as with read-string
        self.write_compact_size(len(string))
        self.write(string)

    def read_bytes(self, length=None, *, strict=False) -> bytes:
        if length is None:
            # Special case if length is None, we auto-read compactSize to determine length
            length = self.read_compact_size(strict=strict)
        try:
            result = self.input[self.read_cursor:self.read_cursor+length]
            if strict and len(result) != length:
                raise IndexError()
            if isinstance(result, bytearray):
                result = bytes(result)
            self.read_cursor += length
            return result
        except IndexError:
            raise SerializationError("attempt to read past end of buffer")

    def can_read_more(self) -> bool:
        if not self.input:
            return False
        return self.read_cursor < len(self.input)

    def read_boolean(self): return self.read_bytes(1)[0] != chr(0)
    def read_int16(self): return self._read_num('<h')
    def read_uint16(self): return self._read_num('<H')
    def read_int32(self): return self._read_num('<i')
    def read_uint32(self): return self._read_num('<I')
    def read_int64(self): return self._read_num('<q')
    def read_uint64(self): return self._read_num('<Q')

    def write_boolean(self, val): return self.write(chr(1) if val else chr(0))
    def write_int16(self, val): return self._write_num('<h', val)
    def write_uint16(self, val): return self._write_num('<H', val)
    def write_int32(self, val): return self._write_num('<i', val)
    def write_uint32(self, val): return self._write_num('<I', val)
    def write_int64(self, val): return self._write_num('<q', val)
    def write_uint64(self, val): return self._write_num('<Q', val)

    def read_compact_size(self, *, strict=False):
        try:
            val = self.input[self.read_cursor]
            self.read_cursor += 1
            if val == 253:
                val = self._read_num('<H')
                min_val = 253
            elif val == 254:
                val = self._read_num('<I')
                min_val = 2**16
            elif val == 255:
                val = self._read_num('<Q')
                min_val = 2**32
            else:
                min_val = 0
            if strict and val < min_val:
                raise SerializationError("CompactSize is not minimally encoded")
            return val
        except IndexError:
            raise SerializationError("attempt to read past end of buffer")

    def write_compact_size(self, size):
        if size < 0:
            raise SerializationError("attempt to write size < 0")
        elif size < 253:
            self.write(bytes([size]))
        elif size < 2**16:
            self.write(b'\xfd')
            self._write_num('<H', size)
        elif size < 2**32:
            self.write(b'\xfe')
            self._write_num('<I', size)
        elif size < 2**64:
            self.write(b'\xff')
            self._write_num('<Q', size)

    def _read_num(self, format):
        try:
            (i,) = struct.unpack_from(format, self.input, self.read_cursor)
            self.read_cursor += struct.calcsize(format)
        except Exception as e:
            raise SerializationError(e)
        return i

    def _write_num(self, format, num):
        s = struct.pack(format, num)
        self.write(s)
