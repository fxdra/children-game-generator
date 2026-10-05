from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)

from app.services.maze_renderer import MazeRenderer
from app.services.maze_pdf import MazePDF


class MazePreviewDialog(QDialog):
    """
    Preview Maze sebelum diekspor menjadi PDF.
    """

    def __init__(
        self,
        maze_data: dict,
        parent=None,
    ):
        super().__init__(parent)

        self.maze_data = maze_data

        self.setWindowTitle("Preview Maze")
        self.resize(760, 900)

        self._setup_ui()
        self._load_preview()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            20,
            20,
            20,
            20,
        )

        layout.setSpacing(12)

        self.svg_widget = QSvgWidget()

        self.svg_widget.setMinimumSize(
            500,
            707,
        )

        self.svg_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        layout.addWidget(
            self.svg_widget,
            1,
        )

        # ==============================================
        # FOOTER BUTTONS
        # ==============================================

        button_layout = QHBoxLayout()

        button_layout.addStretch()

        self.export_button = QPushButton(
            "Export PDF"
        )

        self.export_button.setObjectName(
            "primaryButton"
        )

        self.export_button.clicked.connect(
            self._export_pdf
        )

        self.close_button = QPushButton(
            "Tutup"
        )

        self.close_button.setObjectName(
            "secondaryButton"
        )

        self.close_button.clicked.connect(
            self.accept
        )

        button_layout.addWidget(
            self.export_button
        )

        button_layout.addWidget(
            self.close_button
        )

        layout.addLayout(
            button_layout
        )

    def _load_preview(self):
        """
        Render maze menjadi SVG lalu tampilkan
        pada QSvgWidget.
        """

        try:
            maze_generator = self.maze_data[
                "maze_generator"
            ]

            start_asset = self.maze_data.get(
                "start_asset"
            )

            finish_asset = self.maze_data.get(
                "finish_asset"
            )

            renderer = MazeRenderer(
                maze_generator,
                start_asset=start_asset,
                finish_asset=finish_asset,
            )

            result = renderer.render()

            self.svg_widget.load(
                result["svg_data"]
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Preview Gagal",
                (
                    "Maze gagal ditampilkan.\n\n"
                    f"{error}"
                ),
            )

    def _export_pdf(self):
        """
        Export maze menjadi PDF.
        """

        try:
            maze_generator = self.maze_data[
                "maze_generator"
            ]

            start_asset = self.maze_data.get(
                "start_asset"
            )

            finish_asset = self.maze_data.get(
                "finish_asset"
            )

            title = self.maze_data.get(
                "title",
                "Maze",
            )

            instruction = self.maze_data.get(
                "instruction",
                MazePDF.DEFAULT_INSTRUCTION,
            )

            output_path = MazePDF.export(
                maze_generator=maze_generator,
                start_asset=start_asset,
                finish_asset=finish_asset,
                title=title,
                instruction=instruction,
            )

            QMessageBox.information(
                self,
                "PDF Berhasil",
                (
                    "Maze berhasil diekspor.\n\n"
                    f"{output_path}"
                ),
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Export Gagal",
                (
                    "Maze gagal diekspor menjadi PDF.\n\n"
                    f"{error}"
                ),
            )