#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python3 -*-
# This file (c) 2023 Calin Culianu <calin.culianu@gmail.com>
# Part of the Electron Cash SPV Wallet
# License: MIT
""" Encapsulation and handling of token metadata -- Qt-specific functions """

from oregano.token_meta import TokenMeta
from .utils import qblockies

from PyQt5.QtCore import QBuffer, QByteArray, QIODevice
from PyQt5.QtGui import QColor, QIcon, QPixmap


class TokenMetaQt(TokenMeta):

    def _icon_to_bytes(self, icon: QIcon) -> bytes:
        ba = QByteArray()
        buffer = QBuffer(ba)
        buffer.open(QIODevice.WriteOnly)
        pm = icon.pixmap(32, 32)
        pm.save(buffer, "PNG")
        return bytes(ba)

    def _bytes_to_icon(self, buf: bytes) -> QIcon:
        ba = QByteArray(buf)
        pm = QPixmap()
        pm.loadFromData(ba, "PNG")
        icon = QIcon(pm)
        return icon

    def gen_default_icon(self, token_id_hex: str) -> QIcon:
        img = qblockies.create(token_id_hex, size=12, scale=4, spotcolor=QColor(0, 0, 0))
        return QIcon(QPixmap.fromImage(img))

    @property
    def _icon_ext(self) -> str:
        """Override"""
        return "png"
