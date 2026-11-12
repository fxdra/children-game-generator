from pathlib import Path

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer

from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from app.services.coloring_renderer import ColoringRenderer
from app.services.coloring_pdf import ColoringPDF
from app.services.coloring_renderer import ColoringRenderer
from app.services.coloring_pdf import ColoringPDF

class ColoringPreviewDialog(QDialog):

    def __init__(
        self,
        coloring_data: dict,
        parent=None,
    ):
        super().__init__(parent)
        self.coloring_data = coloring_data
        self.setWindowTitle(
            "Preview Coloring"
        )
        self.resize(
            850,
            1000,
        )
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # RENDER PREVIEW
        if self.coloring_data.get("source") == "coloring_assets":
            self._render_custom_asset(main_layout)

        else:
            # OPENMOJI - PERTAHANKAN RENDERER LAMA
            result = ColoringRenderer.render_coloring_sheet(
                self.coloring_data["assets"]
            )

            self.svg_widget = QSvgWidget()
            self.svg_widget.load(result["svg_data"])
            self.svg_widget.setMinimumSize(600, 820)

            main_layout.addWidget(self.svg_widget, 1)

        # FOOTER
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()

        export_button = QPushButton("Export PDF")
        export_button.setObjectName("primaryButton")
        export_button.setCursor(Qt.PointingHandCursor)
        export_button.clicked.connect(self._export_pdf)

        # PDF custom belum diintegrasikan pada tahap ini.
        if self.coloring_data.get("source") == "coloring_assets":
            export_button.setEnabled(False)
            export_button.setToolTip(
                "Export PDF Coloring Assets belum tersedia."
            )

        footer_layout.addWidget(export_button)

        close_button = QPushButton("Tutup")
        close_button.setObjectName("secondaryButton")
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.clicked.connect(self.accept)

        footer_layout.addWidget(close_button)
        main_layout.addLayout(footer_layout)

    def _render_custom_asset(self, main_layout):
        asset = self.coloring_data["custom_asset"]
        asset_path = Path(asset["path"])

        if not asset_path.is_file():
            raise FileNotFoundError(
                f"Asset tidak ditemukan: {asset_path}"
            )

        # Kanvas A4 portrait
        page_width = 600
        page_height = 820

        page_pixmap = QPixmap(
            page_width,
            page_height,
        )
        page_pixmap.fill(Qt.white)

        painter = QPainter(page_pixmap)

        # Area gambar di dalam halaman
        target_rect = QRectF(
            30,
            30,
            page_width - 60,
            page_height - 60,
        )

        if asset_path.suffix.lower() == ".svg":
            renderer = QSvgRenderer(str(asset_path))

            if not renderer.isValid():
                painter.end()
                raise ValueError("File SVG tidak valid.")

            source_size = renderer.defaultSize()

            if source_size.isEmpty():
                painter.end()
                raise ValueError(
                    "Ukuran SVG tidak dapat dibaca."
                )

            scaled_size = source_size.scaled(
                int(target_rect.width()),
                int(target_rect.height()),
                Qt.KeepAspectRatio,
            )

            x = (
                target_rect.center().x()
                - scaled_size.width() / 2
            )
            y = (
                target_rect.center().y()
                - scaled_size.height() / 2
            )

            renderer.render(
                painter,
                QRectF(
                    x,
                    y,
                    scaled_size.width(),
                    scaled_size.height(),
                ),
            )

        else:
            source_pixmap = QPixmap(str(asset_path))

            if source_pixmap.isNull():
                painter.end()
                raise ValueError(
                    "File gambar tidak dapat dibaca."
                )

            scaled_pixmap = source_pixmap.scaled(
                int(target_rect.width()),
                int(target_rect.height()),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )

            x = int(
                target_rect.center().x()
                - scaled_pixmap.width() / 2
            )
            y = int(
                target_rect.center().y()
                - scaled_pixmap.height() / 2
            )

            painter.drawPixmap(
                x,
                y,
                scaled_pixmap,
            )

        painter.end()

        self.custom_preview = QLabel()
        self.custom_preview.setAlignment(Qt.AlignCenter)
        self.custom_preview.setPixmap(page_pixmap)
        self.custom_preview.setFixedSize(
            page_width,
            page_height,
        )
        self.custom_preview.setStyleSheet(
            "background-color: white; border: 1px solid #cccccc;"
        )

        main_layout.addWidget(
            self.custom_preview,
            alignment=Qt.AlignCenter,
        )

    def _export_pdf(self):
        try:
            output_path = ColoringPDF.export(
                self.coloring_data
            )
            QMessageBox.information(
                self,
                "PDF Berhasil",
                (
                    "Worksheet Coloring berhasil "
                    "dibuat.\n\n"
                    f"File:\n{output_path}"
                ),
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Gagal Export PDF",
                (
                    "Terjadi kesalahan saat "
                    "membuat PDF.\n\n"
                    f"{e}"
                ),
            )
