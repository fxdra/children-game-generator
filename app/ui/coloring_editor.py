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
)

from app.services.openmoji_asset import OpenMojiAssetService
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

        self._setup_ui()

    # =====================================================
    # UI
    # =====================================================

    def _setup_ui(self):

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            36,
            32,
            36,
            32,
        )

        main_layout.setSpacing(20)

        # =================================================
        # HEADER
        # =================================================

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

        # =================================================
        # MATERIAL INFO
        # =================================================

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

        # =================================================
        # ASSET CARD
        # =================================================

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
            "Pilih 3 asset OpenMoji. Asset Color digunakan sebagai contoh, sedangkan asset Black digunakan sebagai gambar untuk diwarnai."
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

        # =================================================
        # ASSET PREVIEW SLOTS
        # =================================================

        self.asset_previews = []
        self.asset_name_labels = []
        self.asset_status_labels = []

        for index in range(3):

            slot_layout = QHBoxLayout()

            slot_layout.setSpacing(20)

            preview = QLabel()

            preview.setFixedSize(
                100,
                100,
            )

            preview.setAlignment(
                Qt.AlignCenter
            )

            preview.setObjectName(
                "coloringAssetPreview"
            )

            slot_layout.addWidget(
                preview
            )

            info_layout = QVBoxLayout()

            info_layout.setSpacing(6)

            slot_label = QLabel(
                f"Asset {index + 1}"
            )

            slot_label.setObjectName(
                "sectionTitle"
            )

            info_layout.addWidget(
                slot_label
            )

            name_label = QLabel(
                "Belum ada asset"
            )

            name_label.setObjectName(
                "sectionDescription"
            )

            info_layout.addWidget(
                name_label
            )

            status_label = QLabel(
                "Belum dipilih."
            )

            status_label.setObjectName(
                "sectionDescription"
            )

            status_label.setWordWrap(
                True
            )

            info_layout.addWidget(
                status_label
            )

            info_layout.addStretch()

            slot_layout.addLayout(
                info_layout
            )

            asset_layout.addLayout(
                slot_layout
            )

            self.asset_previews.append(
                preview
            )

            self.asset_name_labels.append(
                name_label
            )

            self.asset_status_labels.append(
                status_label
            )

        # =================================================
        # CHOOSE ASSET BUTTON
        # =================================================

        choose_button = QPushButton(
            "Pilih 3 Asset"
        )

        choose_button.setObjectName(
            "secondaryButton"
        )

        choose_button.setCursor(
            Qt.PointingHandCursor
        )

        choose_button.clicked.connect(
            self._open_asset_picker
        )

        asset_layout.addWidget(
            choose_button,
            alignment=Qt.AlignLeft,
        )

        main_layout.addWidget(
            asset_card
        )

        main_layout.addStretch()

        # =================================================
        # FOOTER
        # =================================================

        footer_layout = QHBoxLayout()

        footer_layout.setSpacing(12)

        back_button = QPushButton(
            "← Kembali"
        )

        back_button.setObjectName(
            "secondaryButton"
        )

        back_button.setCursor(
            Qt.PointingHandCursor
        )

        back_button.clicked.connect(
            self.back_requested.emit
        )

        preview_button = QPushButton(
            "Preview Coloring →"
        )

        preview_button.setObjectName(
            "primaryButton"
        )

        preview_button.setCursor(
            Qt.PointingHandCursor
        )

        preview_button.clicked.connect(
            self._preview
        )

        footer_layout.addWidget(
            back_button
        )

        footer_layout.addStretch()

        footer_layout.addWidget(
            preview_button
        )

        main_layout.addLayout(
            footer_layout
        )

    # =====================================================
    # MATERIAL DATA
    # =====================================================

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

    # =====================================================
    # ASSET PICKER
    # =====================================================

    def _open_asset_picker(self):

        dialog = AssetPickerDialog(
            self
        )

        dialog.set_target(
            0,
            3,
        )

        dialog.asset_selected.connect(
            self._asset_selected
        )

        dialog.exec()

    # =====================================================
    # ASSET SELECTED
    # =====================================================

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

    # =====================================================
    # ASSET PREVIEW
    # =====================================================

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

    # =====================================================
    # PREVIEW
    # =====================================================

    def _preview(self):

        if len(self.selected_assets) < 3:

            QMessageBox.warning(
                self,
                "Asset Belum Lengkap",
                (
                    "Pilih 3 asset OpenMoji "
                    "terlebih dahulu."
                ),
            )

            return

        coloring_data = {
            **self.material_data,
            "assets": list(
                self.selected_assets
            ),
        }

        self.preview_requested.emit(
            coloring_data
        )

    # =====================================================
    # RESET
    # =====================================================

    def reset_form(self):

        self.material_data = {}

        self.selected_assets = []

        self.material_info.clear()

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