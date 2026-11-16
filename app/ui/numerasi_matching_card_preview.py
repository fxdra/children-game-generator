from pathlib import Path

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QFont, QPainter, QPen
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QMessageBox

from app.services.openmoji_asset import OpenMojiAssetService
from app.services.numerasi_matching_card_pdf import NumerasiMatchingCardPDFService


class NumerasiMatchingCardCanvas(QWidget):
    def __init__(self, matching_data, parent=None):
        super().__init__(parent)
        self.matching_data = matching_data
        self.cards = NumerasiMatchingCardPDFService.build_cards(matching_data)
        self.setMinimumSize(500, 707)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), Qt.white)
        w, h = self.width(), self.height()
        title = self.matching_data.get("title", "Numerasi Matching Card")
        painter.setPen(Qt.black)
        painter.setFont(QFont("Arial", max(12, int(w * .027)), QFont.Bold))
        painter.drawText(QRectF(20, 12, w - 40, 36), Qt.AlignCenter, title)

        # Dua kolom berisi kotak kecil. Lingkaran di sisi tengah menjadi
        # titik untuk anak menarik garis dari soal ke pasangan yang benar.
        margin_x, top, bottom = w * .055, h * .085, h * .045
        rows = max(1, min(6, (len(self.cards) + 1) // 2))
        row_gap = h * .014
        row_h = (h - top - bottom - row_gap * (rows - 1)) / rows
        box_w = w * .34
        box_h = row_h * .68
        left_x = margin_x
        right_x = w - margin_x - box_w
        radius = max(4.0, w * .007)

        for i, card in enumerate(self.cards):
            col = 0 if i < rows else 1
            row = i if col == 0 else i - rows
            center_y = top + row * (row_h + row_gap) + row_h / 2
            x = left_x if col == 0 else right_x
            rect = QRectF(x, center_y - box_h / 2, box_w, box_h)

            painter.setPen(QPen(Qt.black, 1.2))
            painter.drawRoundedRect(rect, 7, 7)
            if card["type"] == "quantity":
                self._draw_quantity(painter, rect, card)
            else:
                text = str(card.get("text", ""))
                size = max(13, min(30, int(box_w * (0.15 if len(text) < 9 else 0.09))))
                painter.setFont(QFont("Arial", size, QFont.Bold))
                painter.drawText(rect.adjusted(6, 4, -6, -4), Qt.AlignCenter | Qt.TextWordWrap, text)

            circle_x = rect.right() + w * .018 if col == 0 else rect.left() - w * .018
            painter.setPen(QPen(Qt.black, 1.4))
            painter.setBrush(Qt.white)
            painter.drawEllipse(QRectF(circle_x - radius, center_y - radius, radius * 2, radius * 2))

        painter.end()

    def _draw_quantity(self, painter, rect, card):
        count = max(1, min(int(card["quantity"]), 20))
        path = OpenMojiAssetService.get_asset(card["asset"], "color")
        renderer = QSvgRenderer(str(path))
        cols = min(5, count)
        rows = (count + cols - 1) // cols
        cell_w = (rect.width() - 18) / cols
        cell_h = (rect.height() - 18) / rows
        side = min(cell_w, cell_h, 38)
        for n in range(count):
            r, c = divmod(n, cols)
            target = QRectF(
                rect.left() + 9 + c * cell_w + (cell_w - side) / 2,
                rect.top() + 9 + r * cell_h + (cell_h - side) / 2,
                side, side,
            )
            renderer.render(painter, target)


class NumerasiMatchingCardPreviewDialog(QDialog):
    def __init__(self, matching_data, parent=None):
        super().__init__(parent)
        self.matching_data = matching_data
        self.setWindowTitle("Preview Numerasi Matching Card")
        self.resize(760, 900)
        layout = QVBoxLayout(self)
        layout.addWidget(NumerasiMatchingCardCanvas(matching_data, self), 1, Qt.AlignHCenter)
        footer = QHBoxLayout()
        footer.addStretch()
        export = QPushButton("Export PDF")
        export.clicked.connect(self._export_pdf)
        footer.addWidget(export)
        close = QPushButton("Tutup")
        close.clicked.connect(self.accept)
        footer.addWidget(close)
        layout.addLayout(footer)

    def _export_pdf(self):
        output_dir = Path(__file__).resolve().parents[2] / "output" / "pdf"
        title = self.matching_data.get("title", "numerasi-matching-card")
        safe = "".join(c if c.isalnum() or c in " -_" else "_" for c in title).strip() or "numerasi-matching-card"
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / f"{safe}.pdf"
        suffix = 2
        while path.exists():
            path = output_dir / f"{safe} ({suffix}).pdf"
            suffix += 1
        try:
            NumerasiMatchingCardPDFService.export(self.matching_data, path)
            QMessageBox.information(self, "Berhasil", f"PDF berhasil dibuat:\n\n{path}")
        except Exception as error:
            QMessageBox.critical(self, "Export Gagal", f"Gagal membuat PDF:\n\n{error}")
