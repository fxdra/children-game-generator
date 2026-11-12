
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QPixmap, QIcon, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QComboBox,
    QVBoxLayout,
    QWidget,
)

from app.services.coloring_asset_service import (
    ColoringAssetService,
)


class ColoringAssetPickerDialog(QDialog):
    asset_selected = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.all_assets = []
        self.selected_asset = None
        self.asset_buttons = []

        self.setWindowTitle("Pilih Asset Coloring")
        self.resize(850, 680)

        self._setup_ui()
        self._load_assets()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        title = QLabel("Pilih Asset Coloring")
        title.setObjectName("pickerTitle")
        main_layout.addWidget(title)

        description = QLabel(
            "Pilih gambar untuk worksheet coloring."
        )
        description.setObjectName("pageSubtitle")
        main_layout.addWidget(description)

        # CATEGORY
        category_layout = QHBoxLayout()

        category_label = QLabel("Kategori:")
        self.category_combo = QComboBox()
        self.category_combo.addItems(
            ColoringAssetService.get_categories()
        )
        self.category_combo.currentTextChanged.connect(
            self._change_category
        )

        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_combo)
        category_layout.addStretch()

        main_layout.addLayout(category_layout)

        # SEARCH
        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText(
            "Cari nama gambar..."
        )
        self.search_input.textChanged.connect(
            self._filter_assets
        )
        main_layout.addWidget(self.search_input)

        # SELECTION COUNTER
        self.selection_label = QLabel(
            "Belum ada gambar dipilih"
        )
        self.selection_label.setObjectName("sectionTitle")
        main_layout.addWidget(self.selection_label)

        # ASSET GRID
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)

        self.asset_container = QWidget()
        self.grid_layout = QGridLayout(self.asset_container)
        self.grid_layout.setContentsMargins(8, 8, 8, 8)
        self.grid_layout.setSpacing(12)

        scroll_area.setWidget(self.asset_container)
        main_layout.addWidget(scroll_area, 1)

        # FOOTER
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()

        cancel_button = QPushButton("Batal")
        cancel_button.setObjectName("secondaryButton")
        cancel_button.clicked.connect(self.reject)

        self.select_button = QPushButton("Gunakan Gambar")
        self.select_button.setObjectName("primaryButton")
        self.select_button.setEnabled(False)
        self.select_button.clicked.connect(
            self._confirm_selection
        )

        footer_layout.addWidget(cancel_button)
        footer_layout.addWidget(self.select_button)

        main_layout.addLayout(footer_layout)

    def _change_category(self, category):
        self.selected_asset = None
        self.search_input.clear()
        self._update_selection_counter()
        self._load_assets(category)
    
    def _toggle_asset(self, asset):
        if (
            self.selected_asset
            and self.selected_asset["filename"] == asset["filename"]
            and self.selected_asset["category"] == asset["category"]
        ):
            self.selected_asset = None
        else:
            self.selected_asset = asset

        self._refresh_buttons()
        self._update_selection_counter()

    def _load_assets(self, category=None, assets=None):
        if category is None:
            category = self.category_combo.currentText()

        if assets is None:
            assets = ColoringAssetService.get_assets(category)
            self.all_assets = assets

        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        self.asset_buttons.clear()

        columns = 5

        for index, asset in enumerate(assets):
            row = index // columns
            column = index % columns

            button = QPushButton()
            button.setCheckable(True)
            button.setFixedSize(120, 120)
            button.setCursor(Qt.PointingHandCursor)

            pixmap = self._render_asset(asset["path"])

            if not pixmap.isNull():
                button.setIcon(QIcon(pixmap))
                button.setIconSize(QSize(96, 96))

            button.setToolTip(asset["filename"])

            button.clicked.connect(
                lambda checked=False,
                selected_asset=asset:
                self._toggle_asset(selected_asset)
            )

            self.grid_layout.addWidget(
                button,
                row,
                column,
            )

            self.asset_buttons.append({
                "button": button,
                "asset": asset,
            })

    def _render_asset(self, asset_path):
        asset_path = str(asset_path)

        if asset_path.lower().endswith(".svg"):
            renderer = QSvgRenderer(asset_path)

            if not renderer.isValid():
                return QPixmap()

            pixmap = QPixmap(96, 96)
            pixmap.fill(Qt.transparent)

            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()

            return pixmap

        pixmap = QPixmap(asset_path)

        if pixmap.isNull():
            return pixmap

        return pixmap.scaled(
            96,
            96,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
    
    def _refresh_buttons(self):
        for item in self.asset_buttons:
            asset = item["asset"]
            button = item["button"]

            button.setChecked(
                self.selected_asset is not None
                and asset["category"] == self.selected_asset["category"]
                and asset["filename"] == self.selected_asset["filename"]
            )

    def _update_selection_counter(self):
        selected = self.selected_asset is not None

        self.selection_label.setText(
            "1 gambar dipilih" if selected
            else "Belum ada gambar dipilih"
        )

        self.select_button.setEnabled(selected)

    def _filter_assets(self, text):
        text = text.strip().lower()

        if not text:
            self._load_assets(
                assets=self.all_assets
            )
            self._refresh_buttons()
            return

        filtered_assets = [
            asset
            for asset in self.all_assets
            if text in asset["name"].lower()
            or text in asset["filename"].lower()
        ]

        self._load_assets(assets=filtered_assets)
        self._refresh_buttons()

    def _confirm_selection(self):
        if not self.selected_asset:
            return

        asset = self.selected_asset

        reply = QMessageBox.question(
            self,
            "Konfirmasi Gambar",
            f'Gunakan gambar "{asset["name"]}"?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply != QMessageBox.Yes:
            return

        self.asset_selected.emit(asset)
        self.accept()

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    dialog = ColoringAssetPickerDialog()
    dialog.asset_selected.connect(print)
    dialog.exec()

    sys.exit()