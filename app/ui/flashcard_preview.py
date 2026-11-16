from pathlib import Path

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.services.flashcard_service import NumberCardService
from app.services.flashcard_renderer import NumberCardRenderer
from app.services.flashcard_pdf import NumberCardPDFService


class NumberCardCanvas(QWidget):
    """Canvas preview kartu angka dengan rasio halaman A4 portrait."""

    def __init__(self, cards: list, title: str = None, parent=None):
        super().__init__(parent)

        self.cards = list(cards)
        self.title = title or NumberCardRenderer.DEFAULT_TITLE

        # Rasio A4 portrait: 210 x 297 mm.
        self.setMinimumSize(500, 707)
        self.setAttribute(Qt.WA_StyledBackground, True)

    def set_cards(self, cards: list):
        self.cards = list(cards)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.fillRect(self.rect(), Qt.white)

        # Pertahankan rasio A4 dan pusatkan halaman di area preview.
        available = self.rect().adjusted(12, 12, -12, -12)
        page_ratio = 210 / 297
        page_width = min(
            available.width(),
            available.height() * page_ratio,
        )
        page_height = page_width / page_ratio

        page_left = available.center().x() - page_width / 2
        page_top = available.center().y() - page_height / 2
        page_rect = QRectF(
            page_left,
            page_top,
            page_width,
            page_height,
        )

        try:
            NumberCardRenderer.draw_page(
                painter=painter,
                page_rect=page_rect,
                cards=self.cards,
                title=self.title,
            )
        except Exception as error:
            painter.save()
            painter.setPen(Qt.red)
            painter.drawText(
                self.rect().adjusted(20, 20, -20, -20),
                Qt.AlignCenter | Qt.TextWordWrap,
                f"Gagal menampilkan preview kartu:\n{error}",
            )
            painter.restore()
        finally:
            painter.end()


class FlashcardPreviewDialog(QDialog):
    """Dialog preview kartu angka dengan navigasi antarhalaman."""

    def __init__(
        self,
        start_number: int = NumberCardService.MIN_NUMBER,
        end_number: int = NumberCardService.MAX_NUMBER,
        parent=None,
    ):
        super().__init__(parent)

        self.start_number = start_number
        self.end_number = end_number
        self.pages = NumberCardService.create_pages(
            start_number=self.start_number,
            end_number=self.end_number,
        )
        self.current_page_index = 0

        self.setWindowTitle("Preview Kartu Pintar Angka")
        self.resize(900, 900)
        self.setMinimumSize(650, 760)

        self._setup_ui()
        self._refresh_page()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)

        self.canvas = NumberCardCanvas(
            cards=self.pages[self.current_page_index],
            parent=self,
        )
        main_layout.addWidget(self.canvas, 1)

        navigation_layout = QHBoxLayout()
        navigation_layout.setSpacing(10)

        self.previous_button = QPushButton("← Previous")
        self.previous_button.setObjectName("secondaryButton")
        self.previous_button.clicked.connect(self._previous_page)
        navigation_layout.addWidget(self.previous_button)

        navigation_layout.addStretch()

        self.page_label = QLabel()
        self.page_label.setAlignment(Qt.AlignCenter)
        navigation_layout.addWidget(self.page_label)

        navigation_layout.addStretch()

        self.next_button = QPushButton("Next →")
        self.next_button.setObjectName("secondaryButton")
        self.next_button.clicked.connect(self._next_page)
        navigation_layout.addWidget(self.next_button)

        main_layout.addLayout(navigation_layout)

        footer_layout = QHBoxLayout()

        self.export_button = QPushButton("Export PDF")
        self.export_button.setObjectName("primaryButton")
        self.export_button.clicked.connect(self._export_pdf)
        footer_layout.addWidget(self.export_button)

        footer_layout.addStretch()

        close_button = QPushButton("Close")
        close_button.setObjectName("secondaryButton")
        close_button.clicked.connect(self.accept)
        footer_layout.addWidget(close_button)

        main_layout.addLayout(footer_layout)
    
    def _refresh_page(self):
        total_pages = len(self.pages)

        if total_pages == 0:
            self.page_label.setText("No pages available")
            self.previous_button.hide()
            self.next_button.hide()
            self.export_button.setEnabled(False)
            return

        self.canvas.set_cards(
            self.pages[self.current_page_index]
        )

        self.page_label.setText(
            f"Halaman {self.current_page_index + 1} dari {total_pages}"
        )

        # Tombol Previous hanya tampil jika bukan halaman pertama.
        self.previous_button.setVisible(
            self.current_page_index > 0
        )

        # Tombol Next hanya tampil jika bukan halaman terakhir.
        self.next_button.setVisible(
            self.current_page_index < total_pages - 1
        )

    def _previous_page(self):
        if self.current_page_index > 0:
            self.current_page_index -= 1
            self._refresh_page()

    def _next_page(self):
        if self.current_page_index < len(self.pages) - 1:
            self.current_page_index += 1
            self._refresh_page()

    def _export_pdf(self):
        default_name = (
            f"kartu_pintar_angka_{self.start_number}_"
            f"sampai_{self.end_number}.pdf"
        )