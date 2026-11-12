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
    QLineEdit,
    QMessageBox,
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
        item_label="Karakter",
    ):
        super().__init__(parent)
        self.item_label = item_label
        self.selected_asset = None
        self.asset_buttons = []
        self.all_assets = []
        self.target_index = 0
        self.total_targets = 6
        self.setWindowTitle(
            f"Pilih {self.item_label}"
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
            f"Pilih {self.item_label}"
        )
        title.setObjectName(
            "pickerTitle"
        )
        main_layout.addWidget(
            title
        )
        self.target_label = QLabel(
        )
        self.target_label.setObjectName(
            "sectionTitle"
        )
        main_layout.addWidget(
            self.target_label
        )
        self.target_description = QLabel(
            "Pilih gambar untuk pasangan nomor 1."
        )
        self.target_description.setObjectName(
            "pageSubtitle"
        )
        main_layout.addWidget(
            self.target_description
        )
        self.search_input = QLineEdit()
        self.search_input.setObjectName(
            "searchInput"
        )
        self.search_input.setPlaceholderText(
            f"Cari {self.item_label.lower()}..."
        )
        self.search_input.textChanged.connect(
            self._filter_assets
        )
        main_layout.addWidget(
            self.search_input
        )
        # ASSET GRID
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

        # FOOTER
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
            f"Gunakan {self.item_label}"
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

    def _load_assets(
        self,
        assets=None,
    ):
        if assets is None:
            assets = (
                OpenMojiAssetService
                .get_all_assets()
            )
            self.all_assets = assets
        # Hapus widget grid sebelumnya.
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.asset_buttons.clear()
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
            button.setIcon(
                QIcon(
                    str(asset["path"])
                )
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
    
    def _filter_assets(
        self,
        text: str,
    ):
        text = text.strip().lower()
        if not text:
            self._load_assets(
                self.all_assets
            )
            return
        filtered_assets = [
            asset
            for asset in self.all_assets
            if text in asset["name"].lower()
            or text in asset["filename"].lower()
        ]
        self._load_assets(
            filtered_assets
        )
    
    def _render_asset(
        self,
        asset_path,
    ):
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
    
    def _update_target_indicator(self):
        current = self.target_index + 1
        if self.item_label == "Karakter":
            target_text = (
                f"Karakter {current} dari "
                f"{self.total_targets}"
            )
            description = (
                "Pilih karakter "
                f"{self._ordinal(current)}."
            )
        else:
            target_text = (
                f"Pasangan {current} dari "
                f"{self.total_targets}"
            )
            description = (
                "Pilih gambar untuk pasangan "
                f"nomor {current}."
            )
        self.target_label.setText(
            target_text
        )
        self.target_description.setText(
            description
        )

    def _ordinal(self, number):
        names = {
            1: "pertama",
            2: "kedua",
            3: "ketiga",
            4: "keempat",
            5: "kelima",
            6: "keenam",
        }
        return names.get(
            number,
            f"nomor {number}",
        )
    
    def _confirm_selection(self):
        if not self.selected_asset:
            return
        asset_name = self.selected_asset
        reply = QMessageBox.question(
            self,
            f"Gunakan {self.item_label}?",
            (
                f'Gunakan {self.item_label.lower()} '
                f'"{asset_name}" '
                f'untuk '
                f'{self._target_confirmation_text()}?'
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        self.asset_selected.emit(
            asset_name
        )
        # Pindah ke target berikutnya.
        if self.target_index < (
            self.total_targets - 1
        ):
            self.target_index += 1
        self._clear_selection()
    
    def _target_confirmation_text(self):
        current = self.target_index + 1
        if self.item_label == "Karakter":
            return (
                f"karakter {current} "
                f"dari {self.total_targets}"
            )
        return (
            f"pasangan {current} "
            f"dari {self.total_targets}"
        )
    
    def _clear_selection(self):
        self.selected_asset = None
        for button in self.asset_buttons:
            button.setChecked(False)
        self.select_button.setEnabled(
            False
        )
        self._update_target_indicator()
    
    def set_target(
        self,
        target_index: int,
        total_targets: int,
    ):
        self.target_index = target_index
        self.total_targets = total_targets
        self._clear_selection()
        self._update_target_indicator()
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dialog = AssetPickerDialog()
    dialog.exec()
    sys.exit()