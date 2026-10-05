from PySide6.QtCore import Qt, Signal
from PySide6.QtSvgWidgets import QSvgWidget

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.services.maze_generator import MazeGenerator
from app.ui.asset_picker import AssetPickerDialog


class MazeEditor(QWidget):
    """
    Editor parent untuk aktivitas Maze / Tracing.

    Saat ini:
    - Maze sudah tersedia
    - Tracing masih placeholder

    Tugas:
    - menerima data materi dari MaterialEditor
    - memilih jenis aktivitas: Maze / Tracing
    - mengatur konfigurasi Maze
    - memilih asset START dan FINISH
    - membuat MazeGenerator
    - mengirim data ke MazePreview
    """

    back_requested = Signal()
    preview_requested = Signal(dict)

    DEFAULT_WIDTH = 180
    DEFAULT_HEIGHT = 240
    DEFAULT_SIDE_LENGTH = 12

    DEFAULT_INSTRUCTION = (
        "Bantu karakter menemukan jalan menuju tujuan!"
    )

    def __init__(self, parent=None):
        super().__init__(parent)

        self.material_data = {}
        self.selected_assets = []
        self.activity_type = "Maze"

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            30,
            30,
            30,
            30,
        )

        main_layout.setSpacing(18)

        # ==============================================
        # HEADER
        # ==============================================

        title = QLabel("Buat Maze / Tracing")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Pilih jenis aktivitas dan atur materi yang akan dibuat."
        )
        subtitle.setObjectName("pageSubtitle")

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        # ==============================================
        # JENIS AKTIVITAS
        # ==============================================

        activity_card = QFrame()
        activity_card.setObjectName("contentCard")

        activity_layout = QFormLayout(activity_card)

        activity_layout.setContentsMargins(
            24,
            20,
            24,
            20,
        )

        activity_layout.setVerticalSpacing(12)
        activity_layout.setHorizontalSpacing(20)

        self.activity_combo = QComboBox()
        self.activity_combo.setObjectName("formCombo")

        self.activity_combo.addItems([
            "Maze",
            "Tracing",
        ])

        self.activity_combo.currentTextChanged.connect(
            self._activity_changed
        )

        activity_layout.addRow(
            self._form_label("Jenis Aktivitas"),
            self.activity_combo,
        )

        main_layout.addWidget(activity_card)

        # ==============================================
        # CONTENT STACK
        # ==============================================

        self.activity_stack = QStackedWidget()

        # Maze page
        self.maze_page = self._create_maze_page()

        # Tracing page
        self.tracing_page = self._create_tracing_page()

        self.activity_stack.addWidget(
            self.maze_page
        )

        self.activity_stack.addWidget(
            self.tracing_page
        )

        main_layout.addWidget(
            self.activity_stack,
            1,
        )

        # ==============================================
        # FOOTER
        # ==============================================

        footer = QHBoxLayout()

        self.back_button = QPushButton(
            "Kembali"
        )

        self.back_button.setObjectName(
            "secondaryButton"
        )

        self.back_button.clicked.connect(
            self.back_requested.emit
        )

        footer.addWidget(
            self.back_button
        )

        footer.addStretch()

        self.preview_button = QPushButton(
            "Preview"
        )

        self.preview_button.setObjectName(
            "primaryButton"
        )

        self.preview_button.clicked.connect(
            self._preview
        )

        footer.addWidget(
            self.preview_button
        )

        main_layout.addLayout(
            footer
        )

    # ==================================================
    # MAZE PAGE
    # ==================================================

    def _create_maze_page(self):
        page = QWidget()

        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        main_layout.setSpacing(18)

        # ==============================================
        # FORM CARD
        # ==============================================

        form_card = QFrame()
        form_card.setObjectName("contentCard")

        form_layout = QFormLayout(form_card)

        form_layout.setContentsMargins(
            24,
            24,
            24,
            24,
        )

        form_layout.setVerticalSpacing(16)
        form_layout.setHorizontalSpacing(20)

        # ----------------------------------------------
        # UKURAN MAZE
        # ----------------------------------------------

        self.width_spin = QSpinBox()

        self.width_spin.setRange(
            120,
            190,
        )

        self.width_spin.setValue(
            self.DEFAULT_WIDTH
        )

        self.width_spin.setSuffix(
            " mm"
        )

        self.width_spin.setObjectName(
            "formSpinBox"
        )

        self.height_spin = QSpinBox()

        self.height_spin.setRange(
            180,
            270,
        )

        self.height_spin.setValue(
            self.DEFAULT_HEIGHT
        )

        self.height_spin.setSuffix(
            " mm"
        )

        self.height_spin.setObjectName(
            "formSpinBox"
        )

        form_layout.addRow(
            self._form_label("Lebar Maze"),
            self.width_spin,
        )

        form_layout.addRow(
            self._form_label("Tinggi Maze"),
            self.height_spin,
        )

        # ----------------------------------------------
        # INSTRUKSI
        # ----------------------------------------------

        self.instruction_label = QLabel(
            self.DEFAULT_INSTRUCTION
        )

        self.instruction_label.setObjectName(
            "materialInfo"
        )

        self.instruction_label.setWordWrap(
            True
        )

        form_layout.addRow(
            self._form_label("Instruksi"),
            self.instruction_label,
        )

        main_layout.addWidget(
            form_card
        )

        # ==============================================
        # ASSET CARD
        # ==============================================

        asset_card = QFrame()
        asset_card.setObjectName("contentCard")

        asset_layout = QVBoxLayout(asset_card)

        asset_layout.setContentsMargins(
            24,
            24,
            24,
            24,
        )

        asset_layout.setSpacing(12)

        asset_title = QLabel(
            "Asset Maze"
        )

        asset_title.setObjectName(
            "sectionTitle"
        )

        asset_description = QLabel(
            "Pilih satu asset untuk START dan satu asset "
            "untuk FINISH."
        )

        asset_description.setObjectName(
            "materialInfo"
        )

        asset_description.setWordWrap(
            True
        )

        asset_layout.addWidget(
            asset_title
        )

        asset_layout.addWidget(
            asset_description
        )

        # ----------------------------------------------
        # ASSET PREVIEW
        # ----------------------------------------------

        preview_row = QHBoxLayout()

        self.start_preview = (
            self._create_asset_slot(
                "START"
            )
        )

        self.finish_preview = (
            self._create_asset_slot(
                "FINISH"
            )
        )

        preview_row.addWidget(
            self.start_preview["frame"],
            1,
        )

        preview_row.addWidget(
            self.finish_preview["frame"],
            1,
        )

        asset_layout.addLayout(
            preview_row
        )

        # ----------------------------------------------
        # PICK BUTTON
        # ----------------------------------------------

        self.pick_assets_button = QPushButton(
            "Pilih 2 Asset"
        )

        self.pick_assets_button.setObjectName(
            "secondaryButton"
        )

        self.pick_assets_button.clicked.connect(
            self._open_asset_picker
        )

        asset_layout.addWidget(
            self.pick_assets_button
        )

        main_layout.addWidget(
            asset_card
        )

        main_layout.addStretch()

        return page

    # ==================================================
    # TRACING PAGE
    # ==================================================

    def _create_tracing_page(self):
        page = QWidget()

        layout = QVBoxLayout(page)

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        card = QFrame()
        card.setObjectName(
            "contentCard"
        )

        card_layout = QVBoxLayout(card)

        card_layout.setContentsMargins(
            30,
            30,
            30,
            30,
        )

        title = QLabel(
            "Tracing"
        )

        title.setObjectName(
            "sectionTitle"
        )

        description = QLabel(
            "Editor Tracing akan tersedia pada tahap berikutnya."
        )

        description.setObjectName(
            "materialInfo"
        )

        description.setWordWrap(
            True
        )

        card_layout.addWidget(
            title
        )

        card_layout.addSpacing(
            8
        )

        card_layout.addWidget(
            description
        )

        card_layout.addStretch()

        layout.addWidget(
            card
        )

        return page

    # ==================================================
    # ACTIVITY SWITCH
    # ==================================================

    def _activity_changed(
        self,
        activity_type,
    ):
        self.activity_type = (
            activity_type
        )

        if activity_type == "Maze":
            self.activity_stack.setCurrentWidget(
                self.maze_page
            )

            self.preview_button.setEnabled(
                True
            )

        elif activity_type == "Tracing":
            self.activity_stack.setCurrentWidget(
                self.tracing_page
            )

            self.preview_button.setEnabled(
                False
            )

    # ==================================================
    # HELPER
    # ==================================================

    def _form_label(self, text):
        label = QLabel(text)
        label.setObjectName(
            "formLabel"
        )
        return label

    def _create_asset_slot(
        self,
        title,
    ):
        frame = QFrame()
        frame.setObjectName(
            "filterCard"
        )

        layout = QVBoxLayout(frame)

        layout.setContentsMargins(
            12,
            12,
            12,
            12,
        )

        layout.setSpacing(
            6
        )

        title_label = QLabel(
            title
        )

        title_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        title_label.setObjectName(
            "sectionTitle"
        )

        svg_widget = QSvgWidget()

        svg_widget.setFixedSize(
            100,
            100,
        )

        status_label = QLabel(
            "Belum dipilih"
        )

        status_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        status_label.setObjectName(
            "materialInfo"
        )

        layout.addWidget(
            title_label
        )

        layout.addWidget(
            svg_widget,
            0,
            Qt.AlignmentFlag.AlignCenter,
        )

        layout.addWidget(
            status_label
        )

        return {
            "frame": frame,
            "svg": svg_widget,
            "status": status_label,
        }

    # ==================================================
    # MATERIAL DATA
    # ==================================================

    def set_material_data(
        self,
        material_data,
    ):
        self.material_data = dict(
            material_data
        )

        self.instruction_label.setText(
            self.DEFAULT_INSTRUCTION
        )

    # ==================================================
    # RESET
    # ==================================================

    def reset_form(self):
        self.material_data = {}

        self.activity_type = "Maze"

        self.activity_combo.blockSignals(
            True
        )

        self.activity_combo.setCurrentText(
            "Maze"
        )

        self.activity_combo.blockSignals(
            False
        )

        self.activity_stack.setCurrentWidget(
            self.maze_page
        )

        self.preview_button.setEnabled(
            True
        )

        self.width_spin.setValue(
            self.DEFAULT_WIDTH
        )

        self.height_spin.setValue(
            self.DEFAULT_HEIGHT
        )

        self.selected_assets.clear()

        self._clear_asset_slot(
            self.start_preview
        )

        self._clear_asset_slot(
            self.finish_preview
        )

    def _clear_asset_slot(
        self,
        slot,
    ):
        slot["svg"].load(
            b"""
            <svg xmlns="http://www.w3.org/2000/svg"
                 width="1"
                 height="1"
                 viewBox="0 0 1 1">
            </svg>
            """
        )

        slot["status"].setText(
            "Belum dipilih"
        )

    # ==================================================
    # ASSET PICKER
    # ==================================================

    def _open_asset_picker(self):
        dialog = AssetPickerDialog(
            self
        )

        dialog.set_target(
            0,
            2,
        )

        dialog.asset_selected.connect(
            self._asset_selected
        )

        dialog.exec()

    def _asset_selected(
        self,
        asset_name,
    ):
        # Jangan izinkan START dan FINISH sama.
        if asset_name in self.selected_assets:
            QMessageBox.warning(
                self,
                "Asset Duplikat",
                (
                    "START dan FINISH harus "
                    "menggunakan asset yang berbeda."
                ),
            )
            return

        if len(self.selected_assets) >= 2:
            return

        self.selected_assets.append(
            asset_name
        )

        index = (
            len(self.selected_assets) - 1
        )

        if index == 0:
            self._set_asset_slot(
                self.start_preview,
                asset_name,
            )

        elif index == 1:
            self._set_asset_slot(
                self.finish_preview,
                asset_name,
            )

    def _set_asset_slot(
        self,
        slot,
        asset_name,
    ):
        try:
            from app.services.openmoji_asset import (
                OpenMojiAssetService,
            )

            asset_path = (
                OpenMojiAssetService.get_asset(
                    asset_name,
                    "color",
                )
            )

            slot["svg"].load(
                asset_path.read_bytes()
            )

        except Exception as error:
            QMessageBox.warning(
                self,
                "Asset Gagal Dimuat",
                (
                    f"Asset '{asset_name}' "
                    f"gagal dimuat.\n\n"
                    f"{error}"
                ),
            )
            return

        slot["status"].setText(
            asset_name
        )

    # ==================================================
    # PREVIEW
    # ==================================================

    def _preview(self):
        if self.activity_type != "Maze":
            return

        if len(self.selected_assets) != 2:
            QMessageBox.warning(
                self,
                "Asset Belum Lengkap",
                (
                    "Pilih asset START dan FINISH "
                    "terlebih dahulu."
                ),
            )
            return

        width = self.width_spin.value()
        height = self.height_spin.value()

        try:
            maze_generator = MazeGenerator(
                width_mm=width,
                height_mm=height,
                side_length_mm=self.DEFAULT_SIDE_LENGTH,
            )

            maze_generator.generate()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Maze Gagal Dibuat",
                (
                    "Maze gagal dibuat.\n\n"
                    f"{error}"
                ),
            )
            return

        title = self.material_data.get(
            "title",
            "Maze",
        )

        maze_data = {
            **self.material_data,

            # Parent activity tetap:
            # Maze / Tracing
            "activity_type": "Maze / Tracing",

            # Sub-activity:
            "sub_activity_type": "Maze",

            "title": title,

            "maze_generator": maze_generator,

            "start_asset": (
                self.selected_assets[0]
            ),

            "finish_asset": (
                self.selected_assets[1]
            ),

            "width_mm": width,
            "height_mm": height,

            "side_length_mm": (
                self.DEFAULT_SIDE_LENGTH
            ),

            "instruction": (
                self.DEFAULT_INSTRUCTION
            ),
        }

        self.preview_requested.emit(
            maze_data
        )