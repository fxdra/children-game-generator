from PySide6.QtCore import Qt
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
)

from app.services.coloring_renderer import ColoringRenderer


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

        result = ColoringRenderer.render_coloring(
            self.coloring_data["asset"]
        )

        self.svg_widget = QSvgWidget()

        self.svg_widget.load(
            str(result["output_path"])
        )

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