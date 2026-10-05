from PySide6.QtCore import Qt
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

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

        main_layout = QVBoxLayout(
            self
        )

        main_layout.setContentsMargins(
            20,
            20,
            20,
            20,
        )

        # =================================================
        # RENDER COLORING SVG
        # =================================================

        result = ColoringRenderer.render_coloring_sheet(
            self.coloring_data["assets"]
        )

        self.svg_widget = QSvgWidget()
        self.svg_widget.load(result["svg_data"])

        self.svg_widget.setMinimumSize(
            600,
            820,
        )

        main_layout.addWidget(
            self.svg_widget,
            1,
        )

        # =================================================
        # FOOTER
        # =================================================

        footer_layout = QHBoxLayout()
        footer_layout.addStretch()
        export_button = QPushButton(
            "Export PDF"
        )
        export_button.setObjectName(
            "primaryButton"
        )
        export_button.setCursor(
            Qt.PointingHandCursor
        )
        export_button.clicked.connect(
            self._export_pdf
        )

        footer_layout.addWidget(
            export_button
        )

        close_button = QPushButton(
            "Tutup"
        )
        close_button.setObjectName(
            "secondaryButton"
        )
        close_button.setCursor(
            Qt.PointingHandCursor
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