from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import (
    QIcon,
    QPainter,
    QPixmap,
)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.services.openmoji_asset import OpenMojiAssetService
from app.ui.asset_picker import AssetPickerDialog

class MatchingCardEditor(QWidget):
    back_requested = Signal()
    preview_requested = Signal(dict)

    def __init__(self):
        super().__init__()

        self.setObjectName("matchingCardEditor")

        self.material_data = {}

        self.pair_inputs = []

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            36,
            32,
            36,
            32,
        )

        main_layout.setSpacing(20)

        # =========================
        # HEADER
        # =========================

        title = QLabel(
            "Editor Matching Card"
        )

        title.setObjectName(
            "pageTitle"
        )

        subtitle = QLabel(
            "Buat pasangan kartu gambar dan kata."
        )

        subtitle.setObjectName(
            "pageSubtitle"
        )

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        # =========================
        # MATERIAL INFO
        # =========================

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

        # =========================
        # SETTINGS
        # =========================

        settings_card = QFrame()

        settings_card.setObjectName(
            "contentCard"
        )

        settings_layout = QFormLayout(
            settings_card
        )

        settings_layout.setContentsMargins(
            24,
            24,
            24,
            24,
        )

        settings_layout.setHorizontalSpacing(
            24
        )

        settings_layout.setVerticalSpacing(
            18
        )

        self.mode_combo = QComboBox()

        self.mode_combo.setObjectName(
            "formCombo"
        )

        self.mode_combo.addItems(
            [
                "Gambar ↔ Kata",
                "Gambar ↔ Gambar",
            ]
        )

        settings_layout.addRow(
            self._create_label(
                "Mode Matching"
            ),
            self.mode_combo,
        )

        main_layout.addWidget(
            settings_card
        )

        # =========================
        # PAIRS
        # =========================

        pairs_card = QFrame()

        pairs_card.setObjectName(
            "contentCard"
        )

        pairs_layout = QVBoxLayout(
            pairs_card
        )

        pairs_layout.setContentsMargins(
            24,
            24,
            24,
            24,
        )

        pairs_layout.setSpacing(8)

        pairs_title = QLabel(
            "Pasangan Kartu"
        )

        pairs_title.setObjectName(
            "sectionTitle"
        )

        pairs_layout.addWidget(
            pairs_title
        )

        pairs_description = QLabel(
            "Masukkan nama asset OpenMoji dan pasangan katanya."
        )

        pairs_description.setObjectName(
            "sectionDescription"
        )

        pairs_layout.addWidget(
            pairs_description
        )

        # Header
        header_layout = QHBoxLayout()

        header_asset = QLabel(
            "Asset OpenMoji"
        )

        header_asset.setObjectName(
            "formLabel"
        )

        header_word = QLabel(
            "Pasangan Kata"
        )

        header_word.setObjectName(
            "formLabel"
        )

        header_layout.addWidget(
            header_asset,
            1,
        )

        header_layout.addWidget(
            header_word,
            1,
        )

        pairs_layout.addLayout(
            header_layout
        )

        default_pairs = [
            ("cat", "KUCING"),
            ("dog", "ANJING"),
            ("apple", "APEL"),
            ("banana", "PISANG"),
        ]

        for index, (
            asset_name,
            word,
        ) in enumerate(
            default_pairs,
            start=1,
        ):
            row = QHBoxLayout()

            row.setSpacing(12)

            row.setContentsMargins(
                0,
                0,
                0,
                8,
            )

            asset_input = QPushButton()

            asset_input.setObjectName(
                "assetPickerButton"
            )

            asset_input.setFixedSize(
                72,
                56,
            )

            asset_input.setCursor(
                Qt.PointingHandCursor
            )

            asset_input.setToolTip(
                "Klik untuk memilih asset"
            )

            asset_input.clicked.connect(
                lambda checked=False,
                pair_index=index - 1:
                self._open_asset_picker(
                    pair_index
                )
            )

            self._set_asset_button_icon(
                asset_input,
                asset_name,
            )

            word_input = QLineEdit()

            word_input.setObjectName(
                "formInput"
            )

            word_input.setPlaceholderText(
                "Contoh: KUCING"
            )

            word_input.setText(
                word
            )

            row.addWidget(
                self._create_pair_label(
                    index
                )
            )

            row.addWidget(
                asset_input,
                1,
            )

            row.addWidget(
                word_input,
                1,
            )

            pairs_layout.addLayout(
                row
            )

            self.pair_inputs.append(
                {
                    "asset": asset_input,
                    "word": word_input,
                }
            )

            if index < len(default_pairs):
                spacer = QWidget()
                spacer.setFixedHeight(
                    10
                )

                pairs_layout.addWidget(
                    spacer
                )

        main_layout.addWidget(
            pairs_card
        )

        # =========================
        # FOOTER
        # =========================

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

        preview_button = QPushButton(
            "Preview Matching Card →"
        )

        preview_button.setObjectName(
            "primaryButton"
        )

        preview_button.setCursor(
            Qt.PointingHandCursor
        )

        back_button.clicked.connect(
            self.back_requested.emit
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

    def _create_label(
        self,
        text: str,
    ):
        label = QLabel(text)

        label.setObjectName(
            "formLabel"
        )

        return label

    def _create_pair_label(
        self,
        number: int,
    ):
        label = QLabel(
            f"{number}."
        )

        label.setObjectName(
            "formLabel"
        )

        label.setFixedWidth(24)

        return label

    def _set_asset_button_icon(
        self,
        button: QPushButton,
        asset_name: str,
    ):
        asset_path = (
            OpenMojiAssetService.get_asset(
                asset_name,
                "color",
            )
        )

        pixmap = QPixmap(
            48,
            48,
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

        button.setIcon(
            QIcon(pixmap)
        )

        button.setIconSize(
            pixmap.size()
        )

        button.setProperty(
            "asset_name",
            asset_name,
        )

    def _open_asset_picker(
        self,
        pair_index: int,
    ):
        dialog = AssetPickerDialog(
            self
        )

        dialog.asset_selected.connect(
            lambda asset_name:
            self._asset_selected(
                pair_index,
                asset_name,
                dialog,
            )
        )

        dialog.exec()

    def _asset_selected(
        self,
        pair_index: int,
        asset_name: str,
        dialog: AssetPickerDialog,
    ):
        pair_input = self.pair_inputs[
            pair_index
        ]

        asset_button = pair_input[
            "asset"
        ]

        self._set_asset_button_icon(
            asset_button,
            asset_name,
        )

        dialog.accept()

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

    def _preview(self):
        pairs = []

        for index, pair in enumerate(
            self.pair_inputs,
            start=1,
        ):
            asset_name = pair["asset"].property(
                "asset_name"
            )

            word = (
                pair["word"]
                .text()
                .strip()
            )

            if not asset_name:
                QMessageBox.warning(
                    self,
                    "Data Belum Lengkap",
                    (
                        f"Asset pada pasangan "
                        f"{index} harus diisi."
                    ),
                )

                pair["asset"].setFocus()

                return

            if not word:
                QMessageBox.warning(
                    self,
                    "Data Belum Lengkap",
                    (
                        f"Kata pada pasangan "
                        f"{index} harus diisi."
                    ),
                )

                pair["word"].setFocus()

                return

            pairs.append(
                {
                    "asset": asset_name,
                    "word": word,
                }
            )

        matching_data = {
            **self.material_data,
            "matching_mode": (
                self.mode_combo.currentText()
            ),
            "pairs": pairs,
        }

        self.preview_requested.emit(
            matching_data
        )

    def reset_form(self):
        self.material_data = {}
        self.mode_combo.setCurrentIndex(0)

        default_pairs = [
            ("cat", "KUCING"),
            ("dog", "ANJING"),
            ("apple", "APEL"),
            ("banana", "PISANG"),
        ]

        for pair_input, (asset_name, word) in zip(
            self.pair_inputs,
            default_pairs,
        ):
            asset_button = pair_input[
                "asset"
            ]

            self._set_asset_button_icon(
                asset_button,
                asset_name,
            )

            pair_input["word"].setText(
                word
            )

        self.material_info.clear()