from pathlib import Path

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import (
    QPainter,
    QPixmap,
    QIcon,
)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.services.openmoji_asset import OpenMojiAssetService


class AssetPickerDialog(QDialog):
    asset_selected = Signal(str)

    def __init__(
        self,
        parent=None,
    ):
        super().__init__(parent)

        self.selected_asset = None
        self.asset_buttons = []

        self.setWindowTitle(
            "Pilih Asset"
        )

        self.resize(
            720,
            600,
        )

        self._setup_ui()
        self._load_assets()

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

        title = QLabel(
            "Pilih Asset"
        )

        title.setObjectName(
            "pageTitle"
        )

        main_layout.addWidget(
            title
        )

        subtitle = QLabel(
            "Pilih gambar yang akan digunakan."
        )

        subtitle.setObjectName(
            "pageSubtitle"
        )

        main_layout.addWidget(
            subtitle
        )

        # =========================
        # ASSET GRID
        # =========================

        scroll_area = QScrollArea()

        scroll_area.setWidgetResizable(
            True
        )

        scroll_area.setFrameShape(
            QScrollArea.NoFrame
        )

        self.asset_container = QWidget()

        self.grid_layout = QGridLayout(
            self.asset_container
        )

        self.grid_layout.setContentsMargins(
            8,
            8,
            8,
            8,
        )

        self.grid_layout.setSpacing(
            12
        )

        scroll_area.setWidget(
            self.asset_container
        )

        main_layout.addWidget(
            scroll_area,
            1,
        )

        # =========================
        # FOOTER
        # =========================

        footer_layout = QHBoxLayout()

        footer_layout.addStretch()

        cancel_button = QPushButton(
            "Batal"
        )

        cancel_button.setObjectName(
            "secondaryButton"
        )

        cancel_button.clicked.connect(
            self.reject
        )

        self.select_button = QPushButton(
            "Pilih"
        )

        self.select_button.setObjectName(
            "primaryButton"
        )

        self.select_button.setEnabled(
            False
        )

        self.select_button.clicked.connect(
            self._confirm_selection
        )

        footer_layout.addWidget(
            cancel_button
        )

        footer_layout.addWidget(
            self.select_button
        )

        main_layout.addLayout(
            footer_layout
        )

    def _load_assets(self):
        assets = OpenMojiAssetService.get_all_assets()

        columns = 6

        for index, asset in enumerate(
            assets
        ):
            row = index // columns
            column = index % columns

            button = QPushButton()

            button.setCheckable(
                True
            )

            button.setFixedSize(
                92,
                92,
            )

            pixmap = self._render_asset(
                asset["path"]
            )

            button.setIcon(
                QIcon(pixmap)
            )

            button.setIconSize(
                QSize(
                    64,
                    64,
                )
            )

            button.setToolTip(
                asset["name"]
            )

            button.setCursor(
                Qt.PointingHandCursor
            )

            button.clicked.connect(
                lambda checked=False,
                asset_name=asset["name"],
                button=button:
                self._select_asset(
                    asset_name,
                    button,
                )
            )

            self.grid_layout.addWidget(
                button,
                row,
                column,
            )

            self.asset_buttons.append(
                button
            )

    def _render_asset(self, asset_path):
        pixmap = QPixmap(
            64,
            64,
        )

        pixmap.fill(
            Qt.transparent
        )

        renderer = QSvgRenderer(
            str(asset_path)
        )

        painter = QPainter(
            pixmap
        )

        renderer.render(
            painter
        )

        painter.end()

        return pixmap

    def _select_asset(
        self,
        asset_name: str,
        selected_button: QPushButton,
    ):
        self.selected_asset = asset_name

        for button in self.asset_buttons:
            button.setChecked(
                button is selected_button
            )

        self.select_button.setEnabled(
            True
        )

    def _confirm_selection(self):
        if not self.selected_asset:
            return

        self.asset_selected.emit(
            self.selected_asset
        )

        self.accept()

if __name__ == "__main__":
    import sys

    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    dialog = AssetPickerDialog()
    dialog.exec()

    sys.exit()