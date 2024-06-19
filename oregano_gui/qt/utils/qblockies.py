#!/usr/bin/env python3
"""
Create a QImage deterministically from any string.
Based on: https://github.com/tristan/blockies
LICENSE: WTFPL (public domain)
Adapted to Qt by: Calin A. Culianu <calin.culianu@gmail.com>
"""
import ctypes
import math
from random import random
from typing import Optional

from PyQt5.QtCore import Qt, QPoint, QRect, QSize
from PyQt5.QtGui import QColor, QImage, QPainter

DEFAULT_SIZE = 8  # Number of pixels in image, create 8x8 base blocks
DEFAULT_SCALE = 4  # Size of image is size * scale = 32 x 32 by default

DEFAULT_RANDSEED_LEN = 4


def zero_fill_right_shift(num, shift):
    if num < 0:
        num += 4294967296
    if num > 4294967295:
        num = int(bin(num)[-32:], 2)
    return num >> shift


def int32(num):
    return ctypes.c_int32(num).value


class Context:

    def __init__(self, seed: str, randseed_len=DEFAULT_RANDSEED_LEN):
        assert str
        randseed = self.randseed = [0] * randseed_len
        for i in range(len(seed)):
            randseed[i % randseed_len] = int32(randseed[i % randseed_len] << 5) - randseed[i % randseed_len]\
                                         + ord(seed[i])

    def rand(self) -> float:
        """Returns a deterministically random number from 0.0 to 1.0"""
        randseed = self.randseed
        t = int32(randseed[0] ^ (randseed[0] << 11))

        for i in range(0, len(randseed) - 1):
            randseed[i] = randseed[i + 1]

        idx = len(randseed) - 1
        randseed[idx] = int32(randseed[idx]) ^ (int32(randseed[idx]) >> 19) ^ t ^ (t >> 8)
        return zero_fill_right_shift(randseed[idx], 0) / zero_fill_right_shift((1 << 31), 0)

    def create_color(self) -> QColor:
        h = math.floor(self.rand() * 360) / 360.0
        s = ((self.rand() * 60) + 40) / 100.0
        l = ((self.rand() + self.rand() + self.rand() + self.rand()) * 25) / 100.0
        return QColor.fromHslF(h, s, l)

    def create_image_data(self, size):
        width = size
        height = size

        data_width = math.ceil(width / 2)
        mirror_width = size - data_width

        data = []

        for y in range(0, height):
            row = [math.floor(self.rand() * 2.3) for _ in range(data_width)]
            r = row[:mirror_width]
            r.reverse()
            row.extend(r)
            data.extend(row)

        return data


def create(seed: Optional[str] = None,
           color: Optional[QColor] = None,
           bgcolor: Optional[QColor] = None,
           size=DEFAULT_SIZE,
           scale=DEFAULT_SCALE,
           spotcolor: Optional[QColor] = None) -> QImage:

    seed = seed or hex(math.floor(random() * math.pow(10, 16)))
    ctx = Context(seed)
    color = color or ctx.create_color()
    bgcolor = bgcolor or ctx.create_color()
    spotcolor = spotcolor or ctx.create_color()

    image_data = ctx.create_image_data(size)

    width = math.sqrt(len(image_data))
    width = int(width)
    render_size = width * scale
    image = QImage(render_size, render_size, QImage.Format_RGB32)
    image.fill(bgcolor)
    painter = QPainter(image)
    try:
        painter.setBackgroundMode(Qt.OpaqueMode)
        pen = painter.pen()
        pen.setStyle(Qt.NoPen)
        pen.setWidth(0)
        painter.setPen(pen)
        brush = painter.brush()
        brush.setStyle(Qt.SolidPattern)
        painter.setBrush(brush)

        for i, val in enumerate(image_data):
            if val == 0:
                continue

            row = i // width
            col = i % width

            fillcolor = color if val == 1 else spotcolor

            brush.setColor(fillcolor)
            painter.setBrush(brush)

            rect_topleft = QPoint(int(col * scale), int(row * scale))
            rect_size = QSize(scale, scale)
            rect = QRect(rect_topleft, rect_size)
            painter.drawRect(rect)
    finally:
        # In case an exception is raised, we must explicitly call painter.end()
        # before popping stack else PyQt5 crashes with a segmentation fault!
        painter.end()
    return image
