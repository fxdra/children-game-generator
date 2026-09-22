from random import Random

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import (
    QFont,
    QPainter,
    QPen,
)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.services.openmoji_asset import OpenMojiAssetService


class MatchingCardCanvas(QWidget):
    def __init__(self, matching_data: dict, parent=None):
        super().__init__(parent)

        self.matching_data = matching_data

        self.setMinimumSize(
            500,
            707,
        )

        self.cards = self._build_cards()

    def _build_cards(self):
        pairs = self.matching_data.get(
            "pairs",
            []
        )

        words = [
            pair["word"]
            for pair in pairs
        ]

        randomizer = Random()
        randomizer.shuffle(words)

        cards = []

        for pair_index, pair in enumerate(
            pairs,
            start=1,
        ):
            cards.append({
                "pair_index": pair_index,
                "type": "image",
                "asset": pair["asset"],
                "word": pair["word"],
            })

            cards.append({
                "pair_index": pair_index,
                "type": "word",
                "asset": pair["asset"],
                "word": words[pair_index - 1],
            })

        return cards

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        width = self.width()
        height = self.height()

        # =========================
        # A4 PAGE
        # =========================

        page_margin = width * 0.07

        painter.fillRect(
            0,
            0,
            width,
            height,
            Qt.white,
        )

        # =========================
        # HEADER
        # =========================

        title = self.matching_data.get(
            "title",
            "Matching Card",
        )

        painter.setPen(
            Qt.black
        )

        title_font = QFont(
            "Arial",
            max(12, int(width * 0.028)),
        )

        title_font.setBold(True)

        painter.setFont(title_font)

        painter.drawText(
            QRectF(
                page_margin,
                page_margin * 0.55,
                width - page_margin * 2,
                30,
            ),
            Qt.AlignCenter,
            title,
        )

        # =========================
        # CARD GRID
        # =========================

        grid_top = height * 0.13
        grid_bottom = height * 0.94

        grid_left = page_margin
        grid_right = width - page_margin

        columns = 2
        rows = 4

        horizontal_gap = width * 0.035
        vertical_gap = height * 0.018

        card_width = (
            grid_right
            - grid_left
            - horizontal_gap
        ) / columns

        card_height = (
            grid_bottom
            - grid_top
            - vertical_gap * (rows - 1)
        ) / rows

        for index, card in enumerate(
            self.cards
        ):
            row = index // columns
            column = index % columns

            x = (
                grid_left
                + column
                * (
                    card_width
                    + horizontal_gap
                )
            )

            y = (
                grid_top
                + row
                * (
                    card_height
                    + vertical_gap
                )
            )

            rect = QRectF(
                x,
                y,
                card_width,
                card_height,
            )

            self._draw_card(
                painter,
                rect,
                card,
            )

        painter.end()

    def _draw_card(
        self,
        painter: QPainter,
        rect: QRectF,
        card: dict,
    ):
        # =========================
        # CARD BACKGROUND
        # =========================

        painter.setBrush(
            Qt.white
        )

        painter.setPen(
            QPen(
                Qt.black,
                2,
            )
        )

        painter.drawRoundedRect(
            rect,
            8,
            8,
        )

        # =========================
        # IMAGE CARD
        # =========================

        if card["type"] == "image":
            self._draw_image_card(
                painter,
                rect,
                card,
            )

        # =========================
        # WORD CARD
        # =========================

        else:
            self._draw_word_card(
                painter,
                rect,
                card,
            )

    def _draw_image_card(
        self,
        painter: QPainter,
        rect: QRectF,
        card: dict,
    ):
        try:
            asset_path = (
                OpenMojiAssetService.get_asset(
                    card["asset"],
                    "color",
                )
            )

            renderer = QSvgRenderer(
                str(asset_path)
            )

            if not renderer.isValid():
                raise ValueError(
                    "SVG OpenMoji tidak valid."
                )

            size = min(
                rect.width(),
                rect.height(),
            ) * 0.55

            x = (
                rect.center().x()
                - size / 2
            )

            y = (
                rect.center().y()
                - size / 2
            )

            target_rect = QRectF(
                x,
                y,
                size,
                size,
            )

            renderer.render(
                painter,
                target_rect,
            )

        except Exception:
            painter.setPen(
                Qt.red
            )

            error_font = QFont(
                "Arial",
                10,
            )

            error_font.setBold(True)

            painter.setFont(
                error_font
            )

            painter.drawText(
                rect,
                Qt.AlignCenter,
                (
                    "Asset tidak\n"
                    "ditemukan"
                ),
            )

    def _draw_word_card(
        self,
        painter: QPainter,
        rect: QRectF,
        card: dict,
    ):
        word_font = QFont(
            "Arial",
            max(
                14,
                int(rect.width() * 0.085),
            ),
        )

        word_font.setBold(True)

        painter.setFont(
            word_font
        )

        painter.setPen(
            Qt.black
        )

        painter.drawText(
            rect.adjusted(
                12,
                12,
                -12,
                -12,
            ),
            Qt.AlignCenter,
            card["word"],
        )


class MatchingCardPreviewDialog(QDialog):
    def __init__(
        self,
        matching_data: dict,
        parent=None,
    ):
        super().__init__(parent)

        self.matching_data = matching_data

        self.setWindowTitle(
            "Preview Matching Card"
        )

        self.resize(
            760,
            900,
        )

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(
            self
        )

        main_layout.setContentsMargins(
            20,
            20,
            20,
            20,
        )

        main_layout.setSpacing(
            16
        )

        canvas = MatchingCardCanvas(
            self.matching_data,
            self,
        )

        main_layout.addWidget(
            canvas,
            1,
        )

        footer_layout = QHBoxLayout()

        footer_layout.addStretch()

        close_button = QPushButton(
            "Tutup"
        )

        close_button.clicked.connect(
            self.accept
        )

        footer_layout.addWidget(
            close_button
        )

        main_layout.addLayout(
            footer_layout
        )