from __future__ import annotations

from math import ceil
from pathlib import Path
from typing import Iterable

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtSvg import QSvgRenderer

from app.services.openmoji_asset import OpenMojiAssetService


class NumberCardRenderer:
    """
    Renderer bersama untuk preview PySide6 dan export PDF berbasis QPainter.

    Struktur data kartu mengikuti NumberCardService:
        {
            "number": 1,
            "word": "satu",
            "quantity": 1,
            "columns": 1,
            "rows": 1,
            "asset": "apple",  # alias atau nama file SVG OpenMoji
        }

    Pemanggilan:
        NumberCardRenderer.draw_page(painter, page_rect, cards)
    """

    CARDS_PER_PAGE = 6
    GRID_COLUMNS = 2
    GRID_ROWS = 3
    MAX_OBJECTS_PER_ROW = 10

    PAGE_MARGIN_X = 0.055
    PAGE_TOP = 0.115
    PAGE_BOTTOM = 0.045
    CARD_GAP_X = 0.025
    CARD_GAP_Y = 0.018

    CARD_BORDER_COLOR = QColor("#263238")
    TEXT_COLOR = QColor("#17212B")
    MUTED_COLOR = QColor("#667085")
    CARD_BACKGROUND = QColor("#FFFFFF")

    DEFAULT_TITLE = "Smart Card Angka"
    DEFAULT_ASSET = "apple"

    _svg_cache: dict[str, QSvgRenderer] = {}

    @classmethod
    def draw_page(
        cls,
        painter: QPainter,
        page_rect: QRectF,
        cards: Iterable[dict],
        title: str = DEFAULT_TITLE,
    ) -> None:
        """
        Menggambar satu halaman A4 portrait berisi maksimal enam kartu.

        page_rect menggunakan koordinat painter saat ini. Karena itu fungsi
        ini bisa dipakai pada QWidget preview maupun QPdfWriter.
        """
        cards = list(cards)

        if len(cards) > cls.CARDS_PER_PAGE:
            raise ValueError(
                f"Satu halaman hanya boleh berisi maksimal "
                f"{cls.CARDS_PER_PAGE} kartu; diterima {len(cards)}."
            )

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        painter.fillRect(page_rect, Qt.white)

        page_width = page_rect.width()
        page_height = page_rect.height()

        margin_x = page_width * cls.PAGE_MARGIN_X
        grid_left = page_rect.left() + margin_x
        grid_right = page_rect.right() - margin_x
        grid_top = page_rect.top() + page_height * cls.PAGE_TOP
        grid_bottom = page_rect.bottom() - page_height * cls.PAGE_BOTTOM

        header_rect = QRectF(
            grid_left,
            page_rect.top() + page_height * 0.025,
            grid_right - grid_left,
            page_height * 0.065,
        )

        title_font = QFont("Arial")
        title_font.setBold(True)
        title_font.setPointSizeF(max(10.0, page_width * 0.025))
        painter.setFont(title_font)
        painter.setPen(cls.TEXT_COLOR)
        painter.drawText(
            header_rect,
            Qt.AlignCenter | Qt.TextSingleLine,
            title,
        )

        horizontal_gap = page_width * cls.CARD_GAP_X
        vertical_gap = page_height * cls.CARD_GAP_Y

        card_width = (
            grid_right - grid_left - horizontal_gap
        ) / cls.GRID_COLUMNS

        card_height = (
            grid_bottom - grid_top
            - vertical_gap * (cls.GRID_ROWS - 1)
        ) / cls.GRID_ROWS

        for index, card in enumerate(cards):
            row = index // cls.GRID_COLUMNS
            column = index % cls.GRID_COLUMNS

            card_rect = QRectF(
                grid_left + column * (card_width + horizontal_gap),
                grid_top + row * (card_height + vertical_gap),
                card_width,
                card_height,
            )

            cls.draw_card(painter, card_rect, card)

        painter.restore()

    @classmethod
    def draw_card(
        cls,
        painter: QPainter,
        rect: QRectF,
        card: dict,
    ) -> None:
        """Menggambar satu kartu: angka, nama bilangan, dan objek."""
        quantity = cls._positive_int(card.get("quantity", card.get("number", 1)))
        number = card.get("number", quantity)
        word = str(card.get("word", "")).strip()

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)

        border_width = max(1.0, rect.width() * 0.006)
        painter.setPen(QPen(cls.CARD_BORDER_COLOR, border_width))
        painter.setBrush(cls.CARD_BACKGROUND)
        painter.drawRoundedRect(
            rect,
            rect.width() * 0.025,
            rect.width() * 0.025,
        )

        inner = rect.adjusted(
            rect.width() * 0.045,
            rect.height() * 0.035,
            -rect.width() * 0.045,
            -rect.height() * 0.035,
        )

        # Bagian atas: angka besar.
        number_text = str(number)

        number_rect = QRectF(
            inner.left(),
            inner.top(),
            inner.width(),
            inner.height() * 0.22,
        )

        number_font = QFont("Arial")
        number_font.setBold(True)

        # Angka dua digit dibuat lebih kecil agar tidak terpotong.
        if len(number_text) >= 2:
            number_size = min(
                rect.width() * 0.135,
                rect.height() * 0.17,
            )
        else:
            number_size = min(
                rect.width() * 0.17,
                rect.height() * 0.19,
            )

        number_font.setPointSizeF(max(18.0, number_size))

        painter.setFont(number_font)
        painter.setPen(cls.TEXT_COLOR)
        painter.drawText(
            number_rect,
            Qt.AlignHCenter | Qt.AlignVCenter,
            number_text,
        )

        # Nama bilangan.
        word_rect = QRectF(
            inner.left(),
            inner.top() + inner.height() * 0.22,
            inner.width(),
            inner.height() * 0.20,
        )

        word_font = QFont("Arial")
        word_font.setBold(True)
        word_font.setPointSizeF(12.0)

        painter.setFont(word_font)
        painter.setPen(cls.MUTED_COLOR)
        painter.drawText(
            word_rect,
            Qt.AlignHCenter | Qt.AlignVCenter | Qt.TextWordWrap,
            word,
        )

        # Area objek.
        object_rect = QRectF(
            inner.left(),
            inner.top() + inner.height() * 0.405,
            inner.width(),
            inner.height() * 0.57,
        )

        asset_name = (
            card.get("asset")
            or card.get("object_asset")
            or cls.DEFAULT_ASSET
        )

        cls.draw_objects(
            painter=painter,
            rect=object_rect,
            quantity=quantity,
            asset_name=str(asset_name),
            columns=card.get("columns"),
        )

        painter.restore()

    @classmethod
    def draw_objects(
        cls,
        painter: QPainter,
        rect: QRectF,
        quantity: int,
        asset_name: str,
        columns: int | None = None,
    ) -> None:
        """
        Menggambar seluruh objek OpenMoji.

        Baris berisi maksimal 10 objek. Baris terakhir dipusatkan agar
        susunan tidak selalu menempel ke sisi kiri.
        """
        quantity = cls._positive_int(quantity)

        if quantity > 50:
            raise ValueError(
                "Kartu Pintar Angka mendukung maksimal 50 objek per kartu."
            )

        if quantity == 0:
            return

        if columns is None:
            columns = min(quantity, cls.MAX_OBJECTS_PER_ROW)
        else:
            columns = max(
                1,
                min(int(columns), cls.MAX_OBJECTS_PER_ROW, quantity),
            )

        columns = min(columns, cls.MAX_OBJECTS_PER_ROW)
        rows = ceil(quantity / columns)

        cell_width = rect.width() / columns
        cell_height = rect.height() / rows

        icon_size = min(
            cell_width * 0.82,
            cell_height * 0.82,
            rect.width() * 0.22,
        )

        renderer = cls._get_svg_renderer(asset_name)

        for index in range(quantity):
            row = index // columns
            column = index % columns

            # Hitung jumlah objek aktual pada baris ini supaya baris
            # terakhir tetap berada di tengah.
            objects_in_row = min(columns, quantity - row * columns)
            row_width = objects_in_row * cell_width
            row_left = rect.center().x() - row_width / 2

            center_x = row_left + column * cell_width + cell_width / 2
            center_y = rect.top() + row * cell_height + cell_height / 2

            target_rect = QRectF(
                center_x - icon_size / 2,
                center_y - icon_size / 2,
                icon_size,
                icon_size,
            )

            renderer.render(painter, target_rect)

    @classmethod
    def _get_svg_renderer(cls, asset_name: str) -> QSvgRenderer:
        asset_path = Path(
            OpenMojiAssetService.get_asset(asset_name, "color")
        ).resolve()

        cache_key = str(asset_path)

        if cache_key not in cls._svg_cache:
            renderer = QSvgRenderer(cache_key)

            if not renderer.isValid():
                raise ValueError(
                    f"File SVG OpenMoji tidak valid: {asset_path}"
                )

            cls._svg_cache[cache_key] = renderer

        return cls._svg_cache[cache_key]

    @staticmethod
    def _positive_int(value) -> int:
        try:
            result = int(value)
        except (TypeError, ValueError):
            raise ValueError(
                f"Jumlah objek harus berupa bilangan bulat, diterima: {value!r}"
            )

        if result < 0:
            raise ValueError("Jumlah objek tidak boleh negatif.")

        return result
