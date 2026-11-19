from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)

from app.services.number_path_renderer import NumberPathRenderer
from app.services.number_path_pdf import NumberPathPDF


class NumerasiMazePreviewDialog(QDialog):
    def __init__(self, maze_data: dict, parent=None):
        super().__init__(parent)
        self.maze_data = maze_data
        self.is_number_path = maze_data.get("sub_activity_type") == "Number Path"
        self.setWindowTitle(
            f"Preview {maze_data.get('sub_activity_type', 'Numerasi Maze')}"
        )
        self.resize(760, 900)

        layout = QVBoxLayout(self)
        self.svg_widget = QSvgWidget()
        self.svg_widget.setMinimumSize(500, 650)
        self.svg_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        layout.addWidget(self.svg_widget, 1)

        buttons = QHBoxLayout()
        buttons.addStretch()
        export_button = QPushButton("Export PDF")
        export_button.setObjectName("primaryButton")
        export_button.clicked.connect(self._export_pdf)
        close_button = QPushButton("Tutup")
        close_button.setObjectName("secondaryButton")
        close_button.clicked.connect(self.accept)
        buttons.addWidget(export_button)
        buttons.addWidget(close_button)
        layout.addLayout(buttons)
        self._load_preview()

    def _load_preview(self):
        try:
            maze = self.maze_data.get("meatfighter_maze")

            if maze is None:
                raise ValueError(
                    "Data Meat Fighter Maze tidak ditemukan."
                )

            subtype = self.maze_data.get("sub_activity_type")

            if subtype == "Number Path":
                svg_data = NumberPathRenderer(
                    maze,
                    difficulty=self.maze_data.get("difficulty", "Mudah"),
                    start_asset=self.maze_data.get("start_asset"),
                    finish_asset=self.maze_data.get("finish_asset"),
                ).render(
                    self.maze_data.get("title", "Number Path"),
                    self.maze_data.get("instruction"),
                )

            elif subtype in ("Math Equation", "Number Pattern"):
                raise NotImplementedError(
                    f"Renderer {subtype} dengan Meat Fighter Maze "
                    "belum diintegrasikan."
                )

            else:
                raise ValueError(
                    f"Subaktivitas tidak dikenal: {subtype}"
                )

            self.svg_widget.load(svg_data)

        except Exception as error:
            QMessageBox.critical(
                self,
                "Preview Gagal",
                f"Numerasi Maze gagal ditampilkan.\n\n{error}",
            )
    
    def _export_pdf(self):
        try:
            subtype = self.maze_data.get("sub_activity_type")
            maze = self.maze_data.get("meatfighter_maze")

            if maze is None:
                raise ValueError(
                    "Data Meat Fighter Maze tidak ditemukan."
                )

            if subtype == "Number Path":
                path = NumberPathPDF.export(
                    maze,
                    self.maze_data.get("title", "Number Path"),
                    self.maze_data.get("instruction"),
                    difficulty=self.maze_data.get("difficulty", "Mudah"),
                    start_asset=self.maze_data.get("start_asset"),
                    finish_asset=self.maze_data.get("finish_asset"),
                )
            else:
                raise NotImplementedError(
                    f"PDF {subtype} dengan Meat Fighter Maze "
                    "belum diintegrasikan."
                )

            QMessageBox.information(
                self,
                "PDF Berhasil",
                f"PDF berhasil diekspor.\n\n{path}",
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Export Gagal",
                f"PDF gagal diekspor.\n\n{error}",
            )
