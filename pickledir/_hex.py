# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT
import zlib


def padded_hex(x: int, width: int) -> str:
    return hex(x)[2:].rjust(width, '0')


def hex_last_n(x: int, width: int) -> str:
    s = padded_hex(x, width)
    return s[-width:]


def mask_4096(x: int) -> str:
    return hex_last_n(x, 3)


def hash_4096(data: bytes) -> str:
    # Adler32 is faster, but it seems CRC32 sums
    # are more uniformly distributed.

    # https://www.sami-lehtinen.net/blog
    # /python-hash-function-performance-comparison
    #   zlib.adler32 49 units
    #   zlib.crc32 91 units
    #   hashlib.md5 180 units
    #   hashlib.sha1 179 units
    #   hashlib.sha256 403 units

    h = zlib.crc32(data)

    # mixing all the bits together:
    # 0xAABBBCCC will be
    # 0x0AA xor 0xBBB xor 0xCCC

    h = h ^ (h >> 12) ^ (h >> 24)

    return mask_4096(h)
