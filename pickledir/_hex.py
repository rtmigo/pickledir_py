# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

def padded_hex(x: int, width: int) -> str:
    return hex(x)[2:].rjust(width, '0')


def hex_last_n(x: int, width: int) -> str:
    s = padded_hex(x, width)
    return s[-width:]


def mask_4096(x: int) -> str:
    return hex_last_n(x, 3)
