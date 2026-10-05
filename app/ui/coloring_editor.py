from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPainter, QPixmap
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
from app.services.coloring_renderer import ColoringRenderer
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
        self.selected_asset = None

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
            "Pilih gambar yang akan digunakan sebagai contoh dan gambar mewarnai."
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
            "Pilih satu asset OpenMoji. Asset Color digunakan sebagai contoh, sedangkan asset Black digunakan sebagai gambar untuk diwarnai."
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

        # -----------------------------------------------
        # Asset preview + button
        # -----------------------------------------------

        asset_row = QHBoxLayout()

        asset_row.setSpacing(20)

        self.asset_preview = QLabel()

        self.asset_preview.setFixedSize(
            120,
            120,
        )

        self.asset_preview.setAlignment(
            Qt.AlignCenter
        )

        self.asset_preview.setObjectName(
            "coloringAssetPreview"
        )

        asset_row.addWidget(
            self.asset_preview
        )

        asset_info_layout = QVBoxLayout()

        asset_info_layout.setSpacing(8)

        self.asset_name_label = QLabel(
            "Belum ada asset"
        )

        self.asset_name_label.setObjectName(
            "sectionTitle"
        )

        asset_info_layout.addWidget(
            self.asset_name_label
        )

        self.asset_status_label = QLabel(
            "Pilih asset OpenMoji untuk mulai."
        )

        self.asset_status_label.setObjectName(
            "sectionDescription"
        )

        self.asset_status_label.setWordWrap(
            True
        )

        asset_info_layout.addWidget(
            self.asset_status_label
        )

        asset_info_layout.addStretch()

        choose_button = QPushButton(
            "Pilih Asset"
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

        asset_info_layout.addWidget(
            choose_button,
            alignment=Qt.AlignLeft,
        )

        asset_row.addLayout(
            asset_info_layout
        )

        asset_layout.addLayout(
            asset_row
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

        # Coloring hanya mempunyai 1 target.
        dialog.set_target(
            0,
            1,
        )

        dialog.asset_selected.connect(
            lambda asset_name:
            self._asset_selected(
                asset_name,
                dialog,
            )
        )

        dialog.exec()

    # =====================================================
    # ASSET SELECTED
    # =====================================================

    def _asset_selected(
        self,
        asset_name: str,
        dialog: AssetPickerDialog,
    ):

        self.selected_asset = asset_name

        self._set_asset_preview(
            asset_name
        )

        self.asset_name_label.setText(
            asset_name
        )

        self.asset_status_label.setText(
            "Asset siap digunakan sebagai "
            "reference Color dan target Black."
        )

        # Setelah satu asset dipilih,
        # picker tidak perlu tetap terbuka.
        dialog.accept()

    # =====================================================
    # ASSET PREVIEW
    # =====================================================

    def _set_asset_preview(
        self,
        asset_name: str,
    ):

        asset_path = (
            OpenMojiAssetService.get_asset(
                asset_name,
                "color",
            )
        )

        pixmap = QPixmap(
            96,
            96,
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

        self.asset_preview.setPixmap(
            pixmap
        )

    # =====================================================
    # PREVIEW
    # =====================================================

    def _preview(self):

        if not self.selected_asset:

            QMessageBox.warning(
                self,
                "Asset Belum Dipilih",
                "Pilih asset OpenMoji terlebih dahulu.",
            )

            return

        coloring_data = {
            **self.material_data,
            "asset": self.selected_asset,
        }

        self.preview_requested.emit(
            coloring_data
        )

    # =====================================================
    # RESET
    # =====================================================

    def reset_form(self):

        self.material_data = {}
        self.selected_asset = None

        self.material_info.clear()

        self.asset_name_label.setText(
            "Belum ada asset"
        )

        self.asset_status_label.setText(
            "Pilih asset OpenMoji untuk mulai."
        )

        self.asset_preview.clear()