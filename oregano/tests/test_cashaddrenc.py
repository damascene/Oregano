#!/usr/bin/python3

# Copyright (c) 2017 Pieter Wuille
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


"""Reference tests for cashaddr adresses"""

import random
import unittest

from .. import address, cashaddr, networks

XRG_PREFIX = "bitcoincash"
XRG_TESTNET_PREFIX = "bchtest"

VALID_PUBKEY_ADDRESSES = [
    "bitcoincash:qpm2qsznhks23z7629mms6s4cwef74vcwvy22gdx6a",
    "bitcoincash:qr95sy3j9xwd2ap32xkykttr4cvcu7as4y0qverfuy",
    "bitcoincash:qqq3728yw0y47sqn6l2na30mcw6zm78dzqre909m2r"
]

VALID_SCRIPT_ADDRESSES = [
    "bitcoincash:ppm2qsznhks23z7629mms6s4cwef74vcwvn0h829pq",
    "bitcoincash:pr95sy3j9xwd2ap32xkykttr4cvcu7as4yc93ky28e",
    "bitcoincash:pqq3728yw0y47sqn6l2na30mcw6zm78dzq5ucqzc37"
]

VALID_HASHES = [
    bytes([ 118, 160, 64,  83, 189, 160, 168, 139, 218, 81,
            119, 184, 106, 21, 195, 178, 159, 85,  152, 115 ]),
    bytes([ 203, 72, 18, 50, 41,  156, 213, 116, 49,  81,
            172, 75, 45, 99, 174, 25,  142, 123, 176, 169 ]),
    bytes([ 1,   31, 40,  228, 115, 201, 95, 64,  19,  215,
            213, 62, 197, 251, 195, 180, 45, 248, 237, 16 ]),
]


class TestCashAddrAddress(unittest.TestCase):
    """Unit test class for cashaddr addressess."""

    # Valid address sizes from the cashaddr spec
    valid_sizes = [160, 192, 224, 256, 320, 384, 448, 512]

    def test_encode_bad_inputs(self):
        with self.assertRaises(TypeError):
            cashaddr.encode_full(2, cashaddr.PUBKEY_TYPE, bytes(20))
        with self.assertRaises(TypeError):
            cashaddr.encode_full(XRG_PREFIX, cashaddr.PUBKEY_TYPE, '0' * 40)
        with self.assertRaises(ValueError):
            cashaddr.encode_full(XRG_PREFIX, 15, bytes(20))

    def test_encode_decode(self):
        """Test whether valid addresses encode and decode properly, for all
        valid hash sizes.
        """
        for prefix in (XRG_PREFIX, XRG_TESTNET_PREFIX):
            for bits_size in self.valid_sizes:
                size = bits_size // 8
                # Convert to a valid number of bytes for a hash
                hashbytes = bytes(random.randint(0, 255) for i in range(size))
                addr = cashaddr.encode_full(prefix, cashaddr.PUBKEY_TYPE,
                                            hashbytes)
                rprefix, kind, addr_hash = cashaddr.decode(addr)
                self.assertEqual(rprefix, prefix)
                self.assertEqual(kind, cashaddr.PUBKEY_TYPE)
                self.assertEqual(addr_hash, hashbytes)

    def test_bad_encode_size(self):
        """Test that bad sized hashes fail to encode."""
        for bits_size in self.valid_sizes:
            size = bits_size // 8
            # Make size invalid
            size += 1
            # Convert to a valid number of bytes for a hash
            hashbytes = bytes(random.randint(0, 255) for i in range(size))
            with self.assertRaises(ValueError):
                cashaddr.encode_full(XRG_PREFIX, cashaddr.PUBKEY_TYPE,
                                     hashbytes)

    def test_decode_bad_inputs(self):
        with self.assertRaises(TypeError):
            cashaddr.decode(b'foobar')

    def test_bad_decode_size(self):
        """Test that addresses with invalid sizes fail to decode."""
        for bits_size in self.valid_sizes:
            size = bits_size // 8
            # Convert to a valid number of bytes for a hash
            hashbytes = bytes(random.randint(0, 255) for i in range(size))
            payload = cashaddr._pack_addr_data(cashaddr.PUBKEY_TYPE, hashbytes)
            # Add some more 5-bit data after size has been encoded
            payload += bytes(random.randint(0, 15) for i in range(3))
            # Add checksum
            payload += cashaddr._create_checksum(XRG_PREFIX, payload)
            addr = XRG_PREFIX + ':' + ''.join(cashaddr._CHARSET[d] for d in payload)
            # Check decode fails.  This can trigger the length mismatch,
            # excess padding, or non-zero padding errors
            with self.assertRaises(ValueError):
               cashaddr.decode(addr)

    def test_address_case(self):
        prefix, kind, hash160 = cashaddr.decode("bitcoincash:ppm2qsznhks23z7629mms6s4cwef74vcwvn0h829pq")
        assert prefix == "bitcoincash"
        prefix, kind, hash160 = cashaddr.decode("BITCOINCASH:PPM2QSZNHKS23Z7629MMS6S4CWEF74VCWVN0H829PQ")
        assert prefix == "BITCOINCASH"
        with self.assertRaises(ValueError):
            cashaddr.decode("bitcoincash:PPM2QSZNHKS23Z7629MMS6S4CWEF74VCWVN0H829PQ")
        with self.assertRaises(ValueError):
            cashaddr.decode("bitcoincash:ppm2qsznhks23z7629mmS6s4cwef74vcwvn0h829pq")

    def test_prefix(self):
        with self.assertRaises(ValueError):
            cashaddr.decode(":ppm2qsznhks23z7629mms6s4cwef74vcwvn0h82")
        with self.assertRaises(ValueError):
            cashaddr.decode("ppm2qsznhks23z7629mms6s4cwef74vcwvn0h82")
        with self.assertRaises(ValueError):
            cashaddr.decode("bitcoin cash:ppm2qsznhks23z7629mms6s4cwef74vcwvn0h82")
        with self.assertRaises(ValueError):
            cashaddr.decode("bitcoin cash:ab")
        # b is invalid
        with self.assertRaises(ValueError):
            cashaddr.decode("bitcoincash:ppm2qsznbks23z7629mms6s4cwef74vcwvn0h82")

    def test_bad_decode_checksum(self):
        """Test whether addresses with invalid checksums fail to decode."""
        for bits_size in self.valid_sizes:
            size = bits_size // 8
            # Convert to a valid number of bytes for a hash
            hashbytes = bytes(random.randint(0, 255) for i in range(size))
            addr = cashaddr.encode_full(XRG_PREFIX, cashaddr.PUBKEY_TYPE,
                                        hashbytes)
            addrlist = list(addr)
            # Inject an error
            values = list(cashaddr._CHARSET)
            while True:
                pos = random.randint(len(XRG_PREFIX) + 1, len(addr) - 1)
                choice = random.choice(values)
                if choice != addrlist[pos] and addrlist[pos] in values:
                    addrlist[pos] = choice
                    break

            mangled_addr = ''.join(addrlist)
            with self.assertRaises(ValueError, msg=mangled_addr) as e:
                cashaddr.decode(mangled_addr)
            self.assertTrue('invalid checksum' in e.exception.args[0])

    def test_valid_scripthash(self):
        """Test whether valid P2PK addresses decode to the correct output."""
        for (address, hashbytes) in zip(VALID_SCRIPT_ADDRESSES, VALID_HASHES):
            rprefix, kind, addr_hash = cashaddr.decode(address)
            self.assertEqual(rprefix, XRG_PREFIX)
            self.assertEqual(kind, cashaddr.SCRIPT_TYPE)
            self.assertEqual(addr_hash, hashbytes)

    def test_valid_pubkeys(self):
        """Test whether valid P2SH addresses decode to the correct output."""
        for (address, hashbytes) in zip(VALID_PUBKEY_ADDRESSES, VALID_HASHES):
            rprefix, kind, addr_hash = cashaddr.decode(address)
            self.assertEqual(rprefix, XRG_PREFIX)
            self.assertEqual(kind, cashaddr.PUBKEY_TYPE)
            self.assertEqual(addr_hash, hashbytes)

    def test_cashtokens_test_vector(self):
        test_vector = [
            {
                "payloadSize": 20,
                "type": 0,
                "cashaddr": "bitcoincash:qr6m7j9njldwwzlg9v7v53unlr4jkmx6eylep8ekg2",
                "payload": "F5BF48B397DAE70BE82B3CCA4793F8EB2B6CDAC9"
            },
            {
                "payloadSize": 20,
                "type": 2,
                "cashaddr": "bitcoincash:zr6m7j9njldwwzlg9v7v53unlr4jkmx6eycnjehshe",
                "payload": "F5BF48B397DAE70BE82B3CCA4793F8EB2B6CDAC9"
            },
            {
                "payloadSize": 20,
                "type": 1,
                "cashaddr": "bchtest:pr6m7j9njldwwzlg9v7v53unlr4jkmx6eyvwc0uz5t",
                "payload": "F5BF48B397DAE70BE82B3CCA4793F8EB2B6CDAC9"
            },
            {
                "payloadSize": 20,
                "type": 1,
                "cashaddr": "pref:pr6m7j9njldwwzlg9v7v53unlr4jkmx6ey65nvtks5",
                "payload": "F5BF48B397DAE70BE82B3CCA4793F8EB2B6CDAC9"
            },
            {
                "payloadSize": 20,
                "type": 15,
                "cashaddr": "prefix:0r6m7j9njldwwzlg9v7v53unlr4jkmx6ey3qnjwsrf",
                "payload": "F5BF48B397DAE70BE82B3CCA4793F8EB2B6CDAC9"
            },
            {
                "payloadSize": 20,
                "type": 0,
                "cashaddr": "bitcoincash:qr7fzmep8g7h7ymfxy74lgc0v950j3r2959lhtxxsl",
                "payload": "FC916F213A3D7F1369313D5FA30F6168F9446A2D"
            },
            {
                "payloadSize": 20,
                "type": 2,
                "cashaddr": "bitcoincash:zr7fzmep8g7h7ymfxy74lgc0v950j3r295z4y4gq0v",
                "payload": "FC916F213A3D7F1369313D5FA30F6168F9446A2D"
            },
            {
                "payloadSize": 20,
                "type": 0,
                "cashaddr": "bchtest:qr7fzmep8g7h7ymfxy74lgc0v950j3r295pdnvy3hr",
                "payload": "FC916F213A3D7F1369313D5FA30F6168F9446A2D"
            },
            {
                "payloadSize": 20,
                "type": 2,
                "cashaddr": "bchtest:zr7fzmep8g7h7ymfxy74lgc0v950j3r295x8qj2hgs",
                "payload": "FC916F213A3D7F1369313D5FA30F6168F9446A2D"
            },
            {
                "payloadSize": 20,
                "type": 0,
                "cashaddr": "bchreg:qr7fzmep8g7h7ymfxy74lgc0v950j3r295m39d8z59",
                "payload": "FC916F213A3D7F1369313D5FA30F6168F9446A2D"
            },
            {
                "payloadSize": 20,
                "type": 2,
                "cashaddr": "bchreg:zr7fzmep8g7h7ymfxy74lgc0v950j3r295umknfytk",
                "payload": "FC916F213A3D7F1369313D5FA30F6168F9446A2D"
            },
            {
                "payloadSize": 20,
                "type": 0,
                "cashaddr": "prefix:qr7fzmep8g7h7ymfxy74lgc0v950j3r295fu6e430r",
                "payload": "FC916F213A3D7F1369313D5FA30F6168F9446A2D"
            },
            {
                "payloadSize": 20,
                "type": 2,
                "cashaddr": "prefix:zr7fzmep8g7h7ymfxy74lgc0v950j3r295wkf8mhss",
                "payload": "FC916F213A3D7F1369313D5FA30F6168F9446A2D"
            },
            {
                "payloadSize": 20,
                "type": 0,
                "cashaddr": "bitcoincash:qpagr634w55t4wp56ftxx53xukhqgl24yse53qxdge",
                "payload": "7A81EA357528BAB834D256635226E5AE047D5524"
            },
            {
                "payloadSize": 20,
                "type": 2,
                "cashaddr": "bitcoincash:zpagr634w55t4wp56ftxx53xukhqgl24ys77z7gth2",
                "payload": "7A81EA357528BAB834D256635226E5AE047D5524"
            },
            {
                "payloadSize": 20,
                "type": 0,
                "cashaddr": "bitcoincash:qq9l9e2dgkx0hp43qm3c3h252e9euugrfc6vlt3r9e",
                "payload": "0BF2E54D458CFB86B106E388DD54564B9E71034E"
            },
            {
                "payloadSize": 20,
                "type": 2,
                "cashaddr": "bitcoincash:zq9l9e2dgkx0hp43qm3c3h252e9euugrfcaxv4l962",
                "payload": "0BF2E54D458CFB86B106E388DD54564B9E71034E"
            },
            {
                "payloadSize": 20,
                "type": 0,
                "cashaddr": "bitcoincash:qre24q38ghy6k3pegpyvtxahu8q8hqmxmqqn28z85p",
                "payload": "F2AA822745C9AB44394048C59BB7E1C07B8366D8"
            },
            {
                "payloadSize": 20,
                "type": 2,
                "cashaddr": "bitcoincash:zre24q38ghy6k3pegpyvtxahu8q8hqmxmq8eeevptj",
                "payload": "F2AA822745C9AB44394048C59BB7E1C07B8366D8"
            },
            {
                "payloadSize": 20,
                "type": 0,
                "cashaddr": "bitcoincash:qz7xc0vl85nck65ffrsx5wvewjznp9lflgktxc5878",
                "payload": "BC6C3D9F3D278B6A8948E06A399974853097E9FA"
            },
            {
                "payloadSize": 20,
                "type": 2,
                "cashaddr": "bitcoincash:zz7xc0vl85nck65ffrsx5wvewjznp9lflg3p4x6pp5",
                "payload": "BC6C3D9F3D278B6A8948E06A399974853097E9FA"
            },
            {
                "payloadSize": 20,
                "type": 1,
                "cashaddr": "bitcoincash:ppawqn2h74a4t50phuza84kdp3794pq3ccvm92p8sh",
                "payload": "7AE04D57F57B55D1E1BF05D3D6CD0C7C5A8411C6"
            },
            {
                "payloadSize": 20,
                "type": 3,
                "cashaddr": "bitcoincash:rpawqn2h74a4t50phuza84kdp3794pq3cct3k50p0y",
                "payload": "7AE04D57F57B55D1E1BF05D3D6CD0C7C5A8411C6"
            },
            {
                "payloadSize": 20,
                "type": 1,
                "cashaddr": "bitcoincash:pqv53dwyatxse2xh7nnlqhyr6ryjgfdtagkd4vc388",
                "payload": "1948B5C4EACD0CA8D7F4E7F05C83D0C92425ABEA"
            },
            {
                "payloadSize": 20,
                "type": 3,
                "cashaddr": "bitcoincash:rqv53dwyatxse2xh7nnlqhyr6ryjgfdtag38xjkhc5",
                "payload": "1948B5C4EACD0CA8D7F4E7F05C83D0C92425ABEA"
            },
            {
                "payloadSize": 20,
                "type": 1,
                "cashaddr": "bitcoincash:prseh0a4aejjcewhc665wjqhppgwrz2lw5txgn666a",
                "payload": "E19BBFB5EE652C65D7C6B54748170850E1895F75"
            },
            {
                "payloadSize": 20,
                "type": 3,
                "cashaddr": "bitcoincash:rrseh0a4aejjcewhc665wjqhppgwrz2lw5vvmd5u9w",
                "payload": "E19BBFB5EE652C65D7C6B54748170850E1895F75"
            },
            {
                "payloadSize": 20,
                "type": 1,
                "cashaddr": "bitcoincash:pzltaslh7xnrsxeqm7qtvh0v53n3gfk0v5wwf6d7j4",
                "payload": "BEBEC3F7F1A6381B20DF80B65DECA4671426CF65"
            },
            {
                "payloadSize": 20,
                "type": 3,
                "cashaddr": "bitcoincash:rzltaslh7xnrsxeqm7qtvh0v53n3gfk0v5fy6yrcdx",
                "payload": "BEBEC3F7F1A6381B20DF80B65DECA4671426CF65"
            },
            {
                "payloadSize": 32,
                "type": 1,
                "cashaddr": "bitcoincash:pvqqqqqqqqqqqqqqqqqqqqqqzg69v7ysqqqqqqqqqqqqqqqqqqqqqpkp7fqn0",
                "payload": "0000000000000000000000000000123456789000000000000000000000000000"
            },
            {
                "payloadSize": 32,
                "type": 3,
                "cashaddr": "bitcoincash:rvqqqqqqqqqqqqqqqqqqqqqqzg69v7ysqqqqqqqqqqqqqqqqqqqqqn9alsp2y",
                "payload": "0000000000000000000000000000123456789000000000000000000000000000"
            },
            {
                "payloadSize": 32,
                "type": 1,
                "cashaddr": "bitcoincash:pdzyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3jh2p5nn",
                "payload": "4444444444444444444444444444444444444444444444444444444444444444"
            },
            {
                "payloadSize": 32,
                "type": 3,
                "cashaddr": "bitcoincash:rdzyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zygrpttc42c",
                "payload": "4444444444444444444444444444444444444444444444444444444444444444"
            },
            {
                "payloadSize": 32,
                "type": 1,
                "cashaddr": "bitcoincash:pwyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zygsh3sujgcr",
                "payload": "8888888888888888888888888888888888888888888888888888888888888888"
            },
            {
                "payloadSize": 32,
                "type": 3,
                "cashaddr": "bitcoincash:rwyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zygs9zvatfpg",
                "payload": "8888888888888888888888888888888888888888888888888888888888888888"
            },
            {
                "payloadSize": 32,
                "type": 1,
                "cashaddr": "bitcoincash:p0xvenxvenxvenxvenxvenxvenxvenxvenxvenxvenxvenxvenxvcm6gz4t77",
                "payload": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
            },
            {
                "payloadSize": 32,
                "type": 3,
                "cashaddr": "bitcoincash:r0xvenxvenxvenxvenxvenxvenxvenxvenxvenxvenxvenxvenxvcff5rv284",
                "payload": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
            },
            {
                "payloadSize": 32,
                "type": 1,
                "cashaddr": "bitcoincash:p0llllllllllllllllllllllllllllllllllllllllllllllllll7x3vthu35",
                "payload": "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
            },
            {
                "payloadSize": 32,
                "type": 3,
                "cashaddr": "bitcoincash:r0llllllllllllllllllllllllllllllllllllllllllllllllll75zs2wagl",
                "payload": "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
            },
            {
                "payloadSize": 24,
                "type": 0,
                "cashaddr": "bitcoincash:q9adhakpwzztepkpwp5z0dq62m6u5v5xtyj7j3h2ws4mr9g0",
                "payload": "7ADBF6C17084BC86C1706827B41A56F5CA32865925E946EA"
            },
            {
                "payloadSize": 24,
                "type": 1,
                "cashaddr": "bchtest:p9adhakpwzztepkpwp5z0dq62m6u5v5xtyj7j3h2u94tsynr",
                "payload": "7ADBF6C17084BC86C1706827B41A56F5CA32865925E946EA"
            },
            {
                "payloadSize": 24,
                "type": 1,
                "cashaddr": "pref:p9adhakpwzztepkpwp5z0dq62m6u5v5xtyj7j3h2khlwwk5v",
                "payload": "7ADBF6C17084BC86C1706827B41A56F5CA32865925E946EA"
            },
            {
                "payloadSize": 24,
                "type": 15,
                "cashaddr": "prefix:09adhakpwzztepkpwp5z0dq62m6u5v5xtyj7j3h2p29kc2lp",
                "payload": "7ADBF6C17084BC86C1706827B41A56F5CA32865925E946EA"
            },
            {
                "payloadSize": 28,
                "type": 0,
                "cashaddr": "bitcoincash:qgagf7w02x4wnz3mkwnchut2vxphjzccwxgjvvjmlsxqwkcw59jxxuz",
                "payload": "3A84F9CF51AAE98A3BB3A78BF16A6183790B18719126325BFC0C075B"
            },
            {
                "payloadSize": 28,
                "type": 1,
                "cashaddr": "bchtest:pgagf7w02x4wnz3mkwnchut2vxphjzccwxgjvvjmlsxqwkcvs7md7wt",
                "payload": "3A84F9CF51AAE98A3BB3A78BF16A6183790B18719126325BFC0C075B"
            },
            {
                "payloadSize": 28,
                "type": 1,
                "cashaddr": "pref:pgagf7w02x4wnz3mkwnchut2vxphjzccwxgjvvjmlsxqwkcrsr6gzkn",
                "payload": "3A84F9CF51AAE98A3BB3A78BF16A6183790B18719126325BFC0C075B"
            },
            {
                "payloadSize": 28,
                "type": 15,
                "cashaddr": "prefix:0gagf7w02x4wnz3mkwnchut2vxphjzccwxgjvvjmlsxqwkc5djw8s9g",
                "payload": "3A84F9CF51AAE98A3BB3A78BF16A6183790B18719126325BFC0C075B"
            },
            {
                "payloadSize": 32,
                "type": 0,
                "cashaddr": "bitcoincash:qvch8mmxy0rtfrlarg7ucrxxfzds5pamg73h7370aa87d80gyhqxq5nlegake",
                "payload": "3173EF6623C6B48FFD1A3DCC0CC6489B0A07BB47A37F47CFEF4FE69DE825C060"
            },
            {
                "payloadSize": 32,
                "type": 1,
                "cashaddr": "bchtest:pvch8mmxy0rtfrlarg7ucrxxfzds5pamg73h7370aa87d80gyhqxq7fqng6m6",
                "payload": "3173EF6623C6B48FFD1A3DCC0CC6489B0A07BB47A37F47CFEF4FE69DE825C060"
            },
            {
                "payloadSize": 32,
                "type": 1,
                "cashaddr": "pref:pvch8mmxy0rtfrlarg7ucrxxfzds5pamg73h7370aa87d80gyhqxq4k9m7qf9",
                "payload": "3173EF6623C6B48FFD1A3DCC0CC6489B0A07BB47A37F47CFEF4FE69DE825C060"
            },
            {
                "payloadSize": 32,
                "type": 15,
                "cashaddr": "prefix:0vch8mmxy0rtfrlarg7ucrxxfzds5pamg73h7370aa87d80gyhqxqsh6jgp6w",
                "payload": "3173EF6623C6B48FFD1A3DCC0CC6489B0A07BB47A37F47CFEF4FE69DE825C060"
            },
            {
                "payloadSize": 40,
                "type": 0,
                "cashaddr": "bitcoincash:qnq8zwpj8cq05n7pytfmskuk9r4gzzel8qtsvwz79zdskftrzxtar994cgutavfklv39gr3uvz",
                "payload": "C07138323E00FA4FC122D3B85B9628EA810B3F381706385E289B0B25631197D194B5C238BEB136FB"
            },
            {
                "payloadSize": 40,
                "type": 1,
                "cashaddr": "bchtest:pnq8zwpj8cq05n7pytfmskuk9r4gzzel8qtsvwz79zdskftrzxtar994cgutavfklvmgm6ynej",
                "payload": "C07138323E00FA4FC122D3B85B9628EA810B3F381706385E289B0B25631197D194B5C238BEB136FB"
            },
            {
                "payloadSize": 40,
                "type": 1,
                "cashaddr": "pref:pnq8zwpj8cq05n7pytfmskuk9r4gzzel8qtsvwz79zdskftrzxtar994cgutavfklv0vx5z0w3",
                "payload": "C07138323E00FA4FC122D3B85B9628EA810B3F381706385E289B0B25631197D194B5C238BEB136FB"
            },
            {
                "payloadSize": 40,
                "type": 15,
                "cashaddr": "prefix:0nq8zwpj8cq05n7pytfmskuk9r4gzzel8qtsvwz79zdskftrzxtar994cgutavfklvwsvctzqy",
                "payload": "C07138323E00FA4FC122D3B85B9628EA810B3F381706385E289B0B25631197D194B5C238BEB136FB"
            },
            {
                "payloadSize": 48,
                "type": 0,
                "cashaddr": "bitcoincash:qh3krj5607v3qlqh5c3wq3lrw3wnuxw0sp8dv0zugrrt5a3kj6ucysfz8kxwv2k53krr7n933jfsunqex2w82sl",
                "payload": "E361CA9A7F99107C17A622E047E3745D3E19CF804ED63C5C40C6BA763696B98241223D8CE62AD48D863F4CB18C930E4C"
            },
            {
                "payloadSize": 48,
                "type": 1,
                "cashaddr": "bchtest:ph3krj5607v3qlqh5c3wq3lrw3wnuxw0sp8dv0zugrrt5a3kj6ucysfz8kxwv2k53krr7n933jfsunqnzf7mt6x",
                "payload": "E361CA9A7F99107C17A622E047E3745D3E19CF804ED63C5C40C6BA763696B98241223D8CE62AD48D863F4CB18C930E4C"
            },
            {
                "payloadSize": 48,
                "type": 1,
                "cashaddr": "pref:ph3krj5607v3qlqh5c3wq3lrw3wnuxw0sp8dv0zugrrt5a3kj6ucysfz8kxwv2k53krr7n933jfsunqjntdfcwg",
                "payload": "E361CA9A7F99107C17A622E047E3745D3E19CF804ED63C5C40C6BA763696B98241223D8CE62AD48D863F4CB18C930E4C"
            },
            {
                "payloadSize": 48,
                "type": 15,
                "cashaddr": "prefix:0h3krj5607v3qlqh5c3wq3lrw3wnuxw0sp8dv0zugrrt5a3kj6ucysfz8kxwv2k53krr7n933jfsunqakcssnmn",
                "payload": "E361CA9A7F99107C17A622E047E3745D3E19CF804ED63C5C40C6BA763696B98241223D8CE62AD48D863F4CB18C930E4C"
            },
            {
                "payloadSize": 56,
                "type": 0,
                "cashaddr": "bitcoincash:qmvl5lzvdm6km38lgga64ek5jhdl7e3aqd9895wu04fvhlnare5937w4ywkq57juxsrhvw8ym5d8qx7sz7zz0zvcypqscw8jd03f",
                "payload": "D9FA7C4C6EF56DC4FF423BAAE6D495DBFF663D034A72D1DC7D52CBFE7D1E6858F9D523AC0A7A5C34077638E4DD1A701BD017842789982041"
            },
            {
                "payloadSize": 56,
                "type": 1,
                "cashaddr": "bchtest:pmvl5lzvdm6km38lgga64ek5jhdl7e3aqd9895wu04fvhlnare5937w4ywkq57juxsrhvw8ym5d8qx7sz7zz0zvcypqs6kgdsg2g",
                "payload": "D9FA7C4C6EF56DC4FF423BAAE6D495DBFF663D034A72D1DC7D52CBFE7D1E6858F9D523AC0A7A5C34077638E4DD1A701BD017842789982041"
            },
            {
                "payloadSize": 56,
                "type": 1,
                "cashaddr": "pref:pmvl5lzvdm6km38lgga64ek5jhdl7e3aqd9895wu04fvhlnare5937w4ywkq57juxsrhvw8ym5d8qx7sz7zz0zvcypqsammyqffl",
                "payload": "D9FA7C4C6EF56DC4FF423BAAE6D495DBFF663D034A72D1DC7D52CBFE7D1E6858F9D523AC0A7A5C34077638E4DD1A701BD017842789982041"
            },
            {
                "payloadSize": 56,
                "type": 15,
                "cashaddr": "prefix:0mvl5lzvdm6km38lgga64ek5jhdl7e3aqd9895wu04fvhlnare5937w4ywkq57juxsrhvw8ym5d8qx7sz7zz0zvcypqsgjrqpnw8",
                "payload": "D9FA7C4C6EF56DC4FF423BAAE6D495DBFF663D034A72D1DC7D52CBFE7D1E6858F9D523AC0A7A5C34077638E4DD1A701BD017842789982041"
            },
            {
                "payloadSize": 64,
                "type": 0,
                "cashaddr": "bitcoincash:qlg0x333p4238k0qrc5ej7rzfw5g8e4a4r6vvzyrcy8j3s5k0en7calvclhw46hudk5flttj6ydvjc0pv3nchp52amk97tqa5zygg96mtky5sv5w",
                "payload": "D0F346310D5513D9E01E299978624BA883E6BDA8F4C60883C10F28C2967E67EC77ECC7EEEAEAFC6DA89FAD72D11AC961E164678B868AEEEC5F2C1DA08884175B"
            },
            {
                "payloadSize": 64,
                "type": 1,
                "cashaddr": "bchtest:plg0x333p4238k0qrc5ej7rzfw5g8e4a4r6vvzyrcy8j3s5k0en7calvclhw46hudk5flttj6ydvjc0pv3nchp52amk97tqa5zygg96mc773cwez",
                "payload": "D0F346310D5513D9E01E299978624BA883E6BDA8F4C60883C10F28C2967E67EC77ECC7EEEAEAFC6DA89FAD72D11AC961E164678B868AEEEC5F2C1DA08884175B"
            },
            {
                "payloadSize": 64,
                "type": 1,
                "cashaddr": "pref:plg0x333p4238k0qrc5ej7rzfw5g8e4a4r6vvzyrcy8j3s5k0en7calvclhw46hudk5flttj6ydvjc0pv3nchp52amk97tqa5zygg96mg7pj3lh8",
                "payload": "D0F346310D5513D9E01E299978624BA883E6BDA8F4C60883C10F28C2967E67EC77ECC7EEEAEAFC6DA89FAD72D11AC961E164678B868AEEEC5F2C1DA08884175B"
            },
            {
                "payloadSize": 64,
                "type": 15,
                "cashaddr": "prefix:0lg0x333p4238k0qrc5ej7rzfw5g8e4a4r6vvzyrcy8j3s5k0en7calvclhw46hudk5flttj6ydvjc0pv3nchp52amk97tqa5zygg96ms92w6845",
                "payload": "D0F346310D5513D9E01E299978624BA883E6BDA8F4C60883C10F28C2967E67EC77ECC7EEEAEAFC6DA89FAD72D11AC961E164678B868AEEEC5F2C1DA08884175B"
            }
        ]
        for d in test_vector:
            psize, kind, addrstring, payload = d["payloadSize"], d["type"], d["cashaddr"], bytes.fromhex(d["payload"])
            prefix, addrpayload = addrstring.split(':', 1)
            self.assertEqual(cashaddr.encode_full(prefix, kind, payload, checktype=False),
                             addrstring)
            cashaddr.decode(addrstring, checktype=False)
            dprefix, dkind, dhash = cashaddr.decode(addrstring, checktype=False)
            self.assertEqual(prefix, dprefix)
            self.assertEqual(dkind, kind)
            self.assertEqual(payload, dhash)

            net = networks.MainNet()
            # Fudge prefix
            net.CASHADDR_PREFIX = prefix

            # Test Address class optionally if the test vector matches something it supports
            if len(payload) in (20, 32) and kind in (address.Address.ADDR_P2PKH, address.Address.ADDR_P2SH):
                if len(payload) == 32 and kind == address.Address.ADDR_P2PKH:
                    # Address class doesn't support P2PKH with 32-byte hash, so skip, but first test that it raises
                    with self.assertRaises(address.AddressError):
                        address.Address.from_string(addrstring, net=net)
                    self.assertFalse(address.Address.is_valid(addrstring, net=net))
                    continue
                # Test decode the string
                addr = address.Address.from_string(addrstring, net=net)
                self.assertEqual(addr.kind, kind)
                self.assertEqual(addr.hash, payload)
                self.assertFalse(address.Address.is_token(addrstring, net=net))
                self.assertFalse(address.Address.is_legacy(addrstring, net=net))
                self.assertTrue(address.Address.is_valid(addrstring, net=net))
                # Test encodes back identically
                self.assertEqual(addr.to_full_string(address.Address.FMT_CASHADDR, net=net), addrstring)
                # Test constructor works as expected
                self.assertEqual(addr, address.Address(payload, kind))
                # Test the "token-aware" addrstring parses back to an identical address object
                tok_addrstring = addr.to_full_token_string(net=net)
                self.assertEqual(address.Address.from_string(tok_addrstring, net=net), addr)
                tok_addrstring = addr.to_token_string(net=net)
                self.assertTrue(address.Address.is_token(tok_addrstring, net=net))
                self.assertEqual(address.Address.from_string(tok_addrstring, net=net), addr)
                _, ca_type = address.Address.from_cashaddr_string(tok_addrstring, net=net, return_ca_type=True)
                self.assertTrue((kind == address.Address.ADDR_P2PKH and ca_type == cashaddr.TOKEN_PUBKEY_TYPE)
                                or (kind == address.Address.ADDR_P2SH and ca_type == cashaddr.TOKEN_SCRIPT_TYPE))
                # Test legacy encode/decode cycle produces identical results
                legstr = addr.to_string(fmt=address.Address.FMT_LEGACY, net=net)
                self.assertNotEqual(legstr, addrstring)
                self.assertNotEqual(legstr, tok_addrstring)
                self.assertTrue(address.Address.is_valid(legstr, net=net))
                self.assertEqual(address.Address.from_string(legstr, net=net), addr)

                # Check locking script matches what we expect
                if kind == address.Address.ADDR_P2PKH:
                    self.assertEqual(addr.to_script(), address.P2PKH_prefix + payload + address.P2PKH_suffix)
                else:
                    if len(payload) == 32:
                        self.assertEqual(addr.to_script(), address.P2SH32_prefix + payload + address.P2SH32_suffix)
                    else:
                        self.assertEqual(addr.to_script(), address.P2SH_prefix + payload + address.P2SH_suffix)
            elif len(payload) in (20, 32) and kind in (cashaddr.TOKEN_PUBKEY_TYPE, cashaddr.TOKEN_SCRIPT_TYPE):
                if len(payload) == 32 and kind == cashaddr.TOKEN_PUBKEY_TYPE:
                    # Address class doesn't support P2PKH with 32-byte hash, so skip, but first test that it raises
                    with self.assertRaises(address.AddressError):
                        address.Address.from_string(addrstring, net=net)
                    self.assertFalse(address.Address.is_valid(addrstring, net=net))
                    continue
                self.assertTrue(address.Address.is_valid(addrstring, net=net))
                addr = address.Address.from_string(addrstring, net=net)
                self.assertEqual(addr.to_full_token_string(net=net), addrstring)
                self.assertNotEqual(addr.to_full_string(address.Address.FMT_CASHADDR, net=net), addrstring)
                self.assertEqual(addr.hash, payload)
                self.assertTrue((not kind == cashaddr.TOKEN_PUBKEY_TYPE or addr.kind == address.Address.ADDR_P2PKH)
                                and ((not kind == cashaddr.TOKEN_SCRIPT_TYPE
                                      or addr.kind == address.Address.ADDR_P2SH)))
            else:
                # Ensure that for everything else is invalid according to the Address class
                self.assertFalse(address.Address.is_valid(addrstring, net=net))
                with self.assertRaises(address.AddressError):
                    address.Address.from_string(addrstring, net=net)
                with self.assertRaises(AssertionError):
                    # Directly constructing an invalid should raise as well
                    address.Address(payload, kind)


if __name__ == '__main__':
    unittest.main()
