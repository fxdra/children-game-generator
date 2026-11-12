from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QComboBox,
)
from app.services.openmoji_asset import OpenMojiAssetService

from app.ui.coloring_asset_picker import ColoringAssetPickerDialog

from app.ui.asset_picker import AssetPickerDialog

class ColoringEditor(QWidget):
    back_requested = Signal()
    preview_requested = Signal(dict)
    def __init__(self):
        super().__init__()
        self.setObjectName(
            "coloringEditor"
        )
        self.material_data = {}
        # Menyimpan 3 asset Coloring.
        self.selected_assets = []
        self.coloring_source = "openmoji"
        self.selected_coloring_asset = None
        self._setup_ui()

    # UI
    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(
            36,
            32,
            36,
            32,
        )
        main_layout.setSpacing(20)

        # HEADER
        title = QLabel(
            "Editor Coloring"
        )
        title.setObjectName(
            "pageTitle"
        )
        subtitle = QLabel(
            "Pilih 3 gambar yang akan digunakan sebagai contoh dan gambar mewarnai."
        )
        subtitle.setObjectName(
            "pageSubtitle"
        )
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        # MATERIAL INFO
        info_card = QFrame()
        info_card.setObjectName(
            "contentCard"
        )
        info_layout = QVBoxLayout(
            info_card
        )
        info_layout.setContentsMargins(
            24,
            20,
            24,
            20,
        )
        self.material_info = QLabel()
        self.material_info.setObjectName(
            "materialInfo"
        )
        info_layout.addWidget(
            self.material_info
        )
        main_layout.addWidget(
            info_card
        )

        # ASSET CARD
        asset_card = QFrame()
        asset_card.setObjectName(
            "contentCard"
        )
        asset_layout = QVBoxLayout(
            asset_card
        )
        asset_layout.setContentsMargins(
            24,
            24,
            24,
            24,
        )
        asset_layout.setSpacing(12)
        asset_title = QLabel(
            "Asset Coloring"
        )
        asset_title.setObjectName(
            "sectionTitle"
        )
        asset_layout.addWidget(
            asset_title
        )
        asset_description = QLabel(
            "Pilih 3 gambar. Gambar digunakan sebagai contoh, sedangkan Gambar Polos digunakan sebagai gambar untuk diwarnai."
        )
        asset_description.setObjectName(
            "sectionDescription"
        )
        asset_description.setWordWrap(
            True
        )
        asset_layout.addWidget(
            asset_description
        )

        # ASSET SOURCE
        source_label = QLabel("Sumber Gambar")
        source_label.setObjectName("sectionTitle")
        asset_layout.addWidget(source_label)

        self.source_combo = QComboBox()
        self.source_combo.addItems([
            "OpenMoji",
            "Coloring Folder",
        ])
        self.source_combo.currentTextChanged.connect(
            self._change_asset_source
        )
        asset_layout.addWidget(self.source_combo)

        # ASSET PREVIEW SLOTS
        self.asset_previews = []
        self.asset_name_labels = []
        self.asset_status_labels = []
        self.asset_slot_widgets = []

        for index in range(3):
            slot_widget = QWidget()

            slot_layout = QHBoxLayout(slot_widget)
            slot_layout.setContentsMargins(0, 0, 0, 0)
            slot_layout.setSpacing(20)

            preview = QLabel()
            preview.setFixedSize(100, 100)
            preview.setAlignment(Qt.AlignCenter)
            preview.setObjectName("coloringAssetPreview")

            slot_layout.addWidget(preview)

            info_layout = QVBoxLayout()
            info_layout.setSpacing(6)

            slot_label = QLabel(f"Asset {index + 1}")
            slot_label.setObjectName("sectionTitle")
            info_layout.addWidget(slot_label)

            name_label = QLabel("Belum ada asset")
            name_label.setObjectName("sectionDescription")
            info_layout.addWidget(name_label)

            status_label = QLabel("Belum dipilih.")
            status_label.setObjectName("sectionDescription")
            status_label.setWordWrap(True)
            info_layout.addWidget(status_label)

            info_layout.addStretch()
            slot_layout.addLayout(info_layout)

            asset_layout.addWidget(slot_widget)

            self.asset_previews.append(preview)
            self.asset_name_labels.append(name_label)
            self.asset_status_labels.append(status_label)
            self.asset_slot_widgets.append(slot_widget)

        # CHOOSE ASSET BUTTON
        self.choose_button = QPushButton("Pilih 3 Asset")
        self.choose_button.setObjectName("secondaryButton")
        self.choose_button.setCursor(Qt.PointingHandCursor)
        self.choose_button.clicked.connect(
            self._open_asset_picker
        )

        asset_layout.addWidget(
            self.choose_button,
            alignment=Qt.AlignLeft,
        )

        main_layout.addWidget(asset_card)
        main_layout.addStretch()

        # FOOTER
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(12)

        back_button = QPushButton("← Kembali")
        back_button.setObjectName("secondaryButton")
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.clicked.connect(
            self.back_requested.emit
        )

        preview_button = QPushButton("Preview Coloring →")
        preview_button.setObjectName("primaryButton")
        preview_button.setCursor(Qt.PointingHandCursor)
        preview_button.clicked.connect(
            self._preview
        )

        footer_layout.addWidget(back_button)
        footer_layout.addStretch()
        footer_layout.addWidget(preview_button)

        main_layout.addLayout(footer_layout)

    # MATERIAL DATA
    def set_material_data(
        self,
        material_data: dict,
    ):
        self.material_data = material_data
        self.material_info.setText(
            f"<b>{material_data['title']}</b>  •  "
            f"{material_data['category']}  •  "
            f"{material_data['age']}  •  "
            f"{material_data['activity_type']}"
        )

    def _change_asset_source(self, source):
        self.selected_assets.clear()
        self.selected_coloring_asset = None

        for preview in self.asset_previews:
            preview.clear()

        for label in self.asset_name_labels:
            label.setText("Belum ada asset")

        for label in self.asset_status_labels:
            label.setText("Belum dipilih.")

        if source == "OpenMoji":
            self.coloring_source = "openmoji"

            for widget in self.asset_slot_widgets:
                widget.show()

            self.asset_previews[0].setFixedSize(100, 100)

            self.choose_button.setText("Pilih 3 Asset")

        else:
            self.coloring_source = "coloring_assets"

            self.asset_slot_widgets[1].hide()
            self.asset_slot_widgets[2].hide()

            self.asset_previews[0].setFixedSize(260, 260)

            self.asset_name_labels[0].setText(
                "Belum ada gambar"
            )

            self.choose_button.setText("Pilih Gambar")

    # ASSET PICKER
    def _open_asset_picker(self):
        if self.coloring_source == "openmoji":
            dialog = AssetPickerDialog(self)
            dialog.set_target(0, 3)
            dialog.asset_selected.connect(
                self._asset_selected
            )
        else:
            dialog = ColoringAssetPickerDialog(self)
            dialog.asset_selected.connect(
                self._coloring_asset_selected
            )

        dialog.exec()

    # ASSET SELECTED
    def _asset_selected(
        self,
        asset_name: str,
    ):
        # Hindari asset yang sama dipakai
        # lebih dari satu kali.
        if asset_name in self.selected_assets:
            QMessageBox.warning(
                self,
                "Asset Sudah Dipilih",
                (
                    f'Asset "{asset_name}" '
                    "sudah digunakan.\n\n"
                    "Silakan pilih asset yang berbeda."
                ),
            )
            return
        if len(self.selected_assets) >= 3:
            return
        self.selected_assets.append(
            asset_name
        )
        index = (
            len(self.selected_assets) - 1
        )
        self._set_asset_preview(
            index,
            asset_name,
        )
        self.asset_name_labels[index].setText(
            asset_name
        )
        self.asset_status_labels[index].setText(
            "Asset siap digunakan sebagai "
            "reference Color dan target Black."
        )

    def _coloring_asset_selected(self, asset):
        self.selected_coloring_asset = asset

        self._set_coloring_asset_preview(
            asset["path"]
        )

        self.asset_name_labels[0].setText(
            asset["name"]
        )

        self.asset_status_labels[0].setText(
            f"Kategori: {asset['category']}"
        )

    # ASSET PREVIEW
    def _set_asset_preview(
        self,
        index: int,
        asset_name: str,
    ):
        asset_path = (
            OpenMojiAssetService.get_asset(
                asset_name,
                "color",
            )
        )
        pixmap = QPixmap(
            80,
            80,
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
        self.asset_previews[index].setPixmap(
            pixmap
        )

    def _set_coloring_asset_preview(self, asset_path):
        asset_path = str(asset_path)

        if asset_path.lower().endswith(".svg"):
            renderer = QSvgRenderer(asset_path)

            if not renderer.isValid():
                QMessageBox.warning(
                    self,
                    "Gagal Membaca Gambar",
                    "File SVG tidak dapat dibaca."
                )
                return

            pixmap = QPixmap(500, 500)
            pixmap.fill(Qt.transparent)

            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()

        else:
            pixmap = QPixmap(asset_path)

        if pixmap.isNull():
            QMessageBox.warning(
                self,
                "Gagal Membaca Gambar",
                "File gambar tidak dapat dibaca."
            )
            return

        scaled_pixmap = pixmap.scaled(
            240,
            240,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        self.asset_previews[0].setPixmap(
            scaled_pixmap
        )

    # PREVIEW
    def _preview(self):
        if self.coloring_source == "openmoji":
            if len(self.selected_assets) < 3:
                QMessageBox.warning(
                    self,
                    "Asset Belum Lengkap",
                    "Pilih 3 asset OpenMoji terlebih dahulu."
                )
                return

            coloring_data = {
                **self.material_data,
                "source": "openmoji",
                "assets": list(self.selected_assets),
            }

        else:
            if not self.selected_coloring_asset:
                QMessageBox.warning(
                    self,
                    "Asset Belum Dipilih",
                    "Pilih satu gambar terlebih dahulu."
                )
                return

            coloring_data = {
                **self.material_data,
                "source": "coloring_assets",
                "custom_asset": self.selected_coloring_asset,
            }

        self.preview_requested.emit(coloring_data)

    # RESET
    def reset_form(self):
        self.material_data = {}
        self.selected_assets = []
        self.material_info.clear()
        self.selected_coloring_asset = None
        self.coloring_source = "openmoji"
        self.source_combo.setCurrentText("OpenMoji")

        for preview in self.asset_previews:
            preview.clear()
        for label in self.asset_name_labels:
            label.setText(
                "Belum ada asset"
            )
        for label in self.asset_status_labels:
            label.setText(
                "Belum dipilih."
            )
