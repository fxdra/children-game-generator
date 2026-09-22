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
    QGridLayout,
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

        self.mode_combo.currentTextChanged.connect(
            self._mode_changed
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

        # PAIRS GRID
        pairs_grid = QGridLayout()

        pairs_grid.setHorizontalSpacing(
            16
        )

        pairs_grid.setVerticalSpacing(
            10
        )

        pairs_grid.setContentsMargins(
            0,
            8,
            0,
            0,
        )

        # Column widths
        pairs_grid.setColumnMinimumWidth(
            0,
            24,
        )

        pairs_grid.setColumnMinimumWidth(
            1,
            72,
        )

        pairs_grid.setColumnMinimumWidth(
            2,
            72,
        )

        pairs_grid.setColumnStretch(
            0,
            0,
        )

        pairs_grid.setColumnStretch(
            1,
            0,
        )

        pairs_grid.setColumnStretch(
            2,
            0,
        )

        pairs_grid.setAlignment(
            Qt.AlignLeft
        )

        # HEADER
        header_number = QLabel(
            ""
        )

        header_asset = QLabel(
            "Asset OpenMoji"
        )

        header_asset.setObjectName(
            "formLabel"
        )

        header_match = QLabel(
            "Pasangan"
        )

        header_match.setObjectName(
            "formLabel"
        )

        pairs_grid.addWidget(
            header_number,
            0,
            0,
        )

        pairs_grid.addWidget(
            header_asset,
            0,
            1,
        )

        pairs_grid.addWidget(
            header_match,
            0,
            2,
        )

        self.header_match = header_match

        # DEFAULT PAIRS
        default_pairs = [
            ("cat", "KUCING"),
            ("dog", "ANJING"),
            ("apple", "APEL"),
            ("banana", "PISANG"),
            ("1F433", "PAUS"),
            ("1F436", "ANJING"),
        ]

        for index, (
            asset_name,
            word,
        ) in enumerate(
            default_pairs,
            start=1,
        ):
            row = index

            # Number
            pair_label = self._create_pair_label(
                index
            )

            pairs_grid.addWidget(
                pair_label,
                row,
                0,
            )

            # Left asset
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

            pairs_grid.addWidget(
                asset_input,
                row,
                1,
            )

            # Word input
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

            pairs_grid.addWidget(
                word_input,
                row,
                2,
            )

            # Right asset
            match_asset_input = QPushButton()

            match_asset_input.setObjectName(
                "assetPickerButton"
            )

            match_asset_input.setFixedSize(
                72,
                56,
            )

            match_asset_input.setCursor(
                Qt.PointingHandCursor
            )

            match_asset_input.setToolTip(
                "Klik untuk memilih asset pasangan"
            )

            match_asset_input.clicked.connect(
                lambda checked=False,
                pair_index=index - 1:
                self._open_match_asset_picker(
                    pair_index
                )
            )

            match_asset_input.setVisible(
                False
            )

            pairs_grid.addWidget(
                match_asset_input,
                row,
                2,
            )

            self.pair_inputs.append(
                {
                    "asset": asset_input,
                    "word": word_input,
                    "match_asset": match_asset_input,
                }
            )

        pairs_layout.addLayout(
            pairs_grid
        )

        main_layout.addWidget(
            pairs_card
        )

        # FOOTER
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

    def _mode_changed(
        self,
        mode: str,
    ):
        is_image_mode = (
            mode == "Gambar ↔ Gambar"
        )

        if is_image_mode:
            self.header_match.setText(
                "Asset Pasangan"
            )
        else:
            self.header_match.setText(
                "Pasangan Kata"
            )

        for pair in self.pair_inputs:
            pair["word"].setVisible(
                not is_image_mode
            )

            pair["match_asset"].setVisible(
                is_image_mode
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

    def _open_match_asset_picker(
        self,
        pair_index: int,
    ):
        dialog = AssetPickerDialog(
            self
        )

        dialog.asset_selected.connect(
            lambda asset_name:
            self._match_asset_selected(
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

    def _match_asset_selected(
        self,
        pair_index: int,
        asset_name: str,
        dialog: AssetPickerDialog,
    ):
        pair_input = self.pair_inputs[
            pair_index
        ]

        match_asset_button = pair_input[
            "match_asset"
        ]

        self._set_asset_button_icon(
            match_asset_button,
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

        mode = self.mode_combo.currentText()

        for index, pair in enumerate(
            self.pair_inputs,
            start=1,
        ):
            asset_name = pair["asset"].property(
                "asset_name"
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

            # =========================
            # GAMBAR ↔ GAMBAR
            # =========================

            if mode == "Gambar ↔ Gambar":
                match_asset_name = (
                    pair["match_asset"].property(
                        "asset_name"
                    )
                )

                if not match_asset_name:
                    QMessageBox.warning(
                        self,
                        "Data Belum Lengkap",
                        (
                            f"Asset pasangan pada "
                            f"nomor {index} harus diisi."
                        ),
                    )

                    pair["match_asset"].setFocus()

                    return

                pairs.append(
                    {
                        "asset": asset_name,
                        "match_asset": match_asset_name,
                    }
                )

            # =========================
            # GAMBAR ↔ KATA
            # =========================

            else:
                word = (
                    pair["word"]
                    .text()
                    .strip()
                )

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
            "matching_mode": mode,
            "pairs": pairs,
        }

        self.preview_requested.emit(
            matching_data
        )

    def reset_form(self):
        self.material_data = {}

        self.mode_combo.setCurrentIndex(
            0
        )

        default_words = [
            "KUCING",
            "ANJING",
            "APEL",
            "PISANG",
            "PAUS",
            "ANJING",
        ]

        for pair_input, word in zip(
            self.pair_inputs,
            default_words,
        ):
            asset_button = pair_input[
                "asset"
            ]

            match_asset_button = pair_input[
                "match_asset"
            ]

            asset_button.setIcon(
                QIcon()
            )

            asset_button.setProperty(
                "asset_name",
                None,
            )

            match_asset_button.setIcon(
                QIcon()
            )

            match_asset_button.setProperty(
                "asset_name",
                None,
            )

            pair_input["word"].setText(
                word
            )

        self.material_info.clear()
        self.material_data = {}
        self.mode_combo.setCurrentIndex(0)

        default_pairs = [
            ("cat", "KUCING"),
            ("dog", "ANJING"),
            ("apple", "APEL"),
            ("banana", "PISANG"),
            ("1F433", "PAUS"),
            ("1F436", "ANJING"),
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