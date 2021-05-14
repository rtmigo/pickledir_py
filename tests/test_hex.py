# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

import random
import unittest

from pickledir._hex import padded_hex, hex_last_n, mask_4096, hash_4096


class TestHex(unittest.TestCase):
    def test_padded(self):
        self.assertEqual(padded_hex(11, 3), '00b')
        self.assertEqual(padded_hex(14, 4), '000e')

    def test_lastn(self):
        self.assertEqual(hex_last_n(11, 3), '00b')
        self.assertEqual(hex_last_n(14, 4), '000e')
        self.assertEqual(hex_last_n(6123469812364, 4), '328c')

    def test_mask(self):
        for _ in range(1000):
            x = random.randint(0, 129873102973)
            m = mask_4096(x)
            self.assertEqual(len(m), 3)
            parsed = int(m, 16)
            self.assertGreaterEqual(parsed, 0)
            self.assertLess(parsed, 4096)

    def test_hash(self):
        # testing that we are getting all 4096 values
        hashes = set()
        for i in range(20000):
            h = hash_4096(str(i).encode())
            self.assertEqual(len(h), 3)
            hashes.add(h)
            if len(hashes) >= 4096:
                return
        raise AssertionError(len(hashes))
