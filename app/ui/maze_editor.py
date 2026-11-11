import shutil
from pathlib import Path

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QImageReader
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QSizePolicy

from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox, 
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QInputDialog,
    QGridLayout,
    QScrollArea,
)

from app.services.maze_generator import MazeGenerator
from app.ui.asset_picker import AssetPickerDialog

class MazeEditor(QWidget):
    """
    Editor parent untuk aktivitas Maze / Tracing.
    Saat ini:
    - Maze tersedia
    - Tracing masih placeholder
    Tugas:
    - menerima data materi dari MaterialEditor
    - memilih jenis aktivitas
    - mengatur konfigurasi Maze
    - memilih asset START dan FINISH
    - membuat MazeGenerator
    - mengirim data ke MazePreview
    """
    back_requested = Signal()
    preview_requested = Signal(dict)
    
    # DEFAULT MAZE
    DEFAULT_WIDTH = 180
    DEFAULT_HEIGHT = 240
    DEFAULT_SIDE_LENGTH = 12
    DEFAULT_INSTRUCTION = (
        "Bantu karakter menemukan jalan menuju tujuan!"
    )
    
    # DIFFICULTY PRESETS
    DIFFICULTY_PRESETS = {
        "Mudah": {
            "width": 180,
            "height": 240,
            "side_length": 12,
        },
        "Sedang": {
            "width": 180,
            "height": 240,
            "side_length": 10,
        },
        "Sulit": {
            "width": 180,
            "height": 240,
            "side_length": 8,
        },
    }

    # TRACING ASSET CONFIG
    TRACING_CATEGORIES = {
        "Animal": "animal",
        "Characters": "character",
        "Instruments": "instruments",
        "Miscellaneous": "miscellaneous",
        "Vehicles": "vehicle",
    }

    SUPPORTED_IMAGE_FORMATS = {
        ".png",
        ".jpg",
        ".jpeg",
        ".svg",
    }

    TRACING_ASSET_DIR = (
        Path(__file__).resolve().parents[2]
        / "assets"
        / "tracing"
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self.material_data = {}
        self.selected_assets = [None, None]
        self.active_asset_target = 0
        self.activity_type = "Maze"
        self._setup_ui()
    # MAIN UI
    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(
            30,
            30,
            30,
            30,
        )
        main_layout.setSpacing(18)
        
        # HEADER
        title = QLabel(
            "Buat Maze / Tracing"
        )
        title.setObjectName(
            "pageTitle"
        )
        subtitle = QLabel(
            "Pilih jenis aktivitas dan atur materi "
            "yang akan dibuat."
        )
        subtitle.setObjectName(
            "pageSubtitle"
        )
        main_layout.addWidget(
            title
        )
        main_layout.addWidget(
            subtitle
        )
        
        # JENIS AKTIVITAS
        activity_card = QFrame()
        activity_card.setObjectName(
            "contentCard"
        )
        activity_layout = QFormLayout(
            activity_card
        )
        activity_layout.setContentsMargins(
            24,
            20,
            24,
            20,
        )
        activity_layout.setVerticalSpacing(
            12
        )
        activity_layout.setHorizontalSpacing(
            20
        )
        self.activity_combo = QComboBox()
        self.activity_combo.setObjectName(
            "formCombo"
        )
        self.activity_combo.addItems([
            "Maze",
            "Tracing",
        ])
        self.activity_combo.currentTextChanged.connect(
            self._activity_changed
        )
        activity_layout.addRow(
            self._form_label(
                "Jenis Aktivitas"
            ),
            self.activity_combo,
        )
        main_layout.addWidget(
            activity_card
        )
        
        # CONTENT STACK
        self.activity_stack = QStackedWidget()
        self.maze_page = (
            self._create_maze_page()
        )
        self.tracing_page = (
            self._create_tracing_page()
        )
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
        
        # FOOTER
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

    # MAZE PAGE
    def _create_maze_page(self):
        page = QWidget()
        main_layout = QVBoxLayout(
            page
        )
        main_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        main_layout.setSpacing(
            18
        )
        
        # MAZE SETTINGS CARD
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
        settings_layout.setVerticalSpacing(
            16
        )
        settings_layout.setHorizontalSpacing(
            20
        )
        
        # TINGKAT KESULITAN
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.setObjectName(
            "formCombo"
        )
        self.difficulty_combo.addItems([
            "Mudah",
            "Sedang",
            "Sulit",
            "Custom",
        ])
        self.difficulty_combo.currentTextChanged.connect(
            self._difficulty_changed
        )
        settings_layout.addRow(
            self._form_label(
                "Tingkat Kesulitan"
            ),
            self.difficulty_combo,
        )
        
        # INSTRUKSI
        
        self.instruction_input = QLineEdit()
        self.instruction_input.setObjectName(
            "formInput"
        )
        self.instruction_input.setText(
            self.DEFAULT_INSTRUCTION
        )
        self.instruction_input.setPlaceholderText(
            "Tulis instruksi untuk anak..."
        )
        settings_layout.addRow(
            self._form_label(
                "Instruksi"
            ),
            self.instruction_input,
        )
        
        # CUSTOM SETTINGS
        self.custom_card = QFrame()
        self.custom_card.setObjectName(
            "contentCard"
        )
        custom_layout = QFormLayout(
            self.custom_card
        )
        custom_layout.setContentsMargins(
            16,
            16,
            16,
            16,
        )
        custom_layout.setVerticalSpacing(
            12
        )
        custom_layout.setHorizontalSpacing(
            20
        )
        custom_title = QLabel(
            "Pengaturan Custom"
        )
        custom_title.setObjectName(
            "sectionTitle"
        )
        custom_layout.addRow(
            custom_title
        )
        
        # CUSTOM WIDTH
        self.custom_width_spin = QSpinBox()
        self.custom_width_spin.setRange(
            120,
            190,
        )
        self.custom_width_spin.setValue(
            self.DEFAULT_WIDTH
        )
        self.custom_width_spin.setSuffix(
            " mm"
        )
        self.custom_width_spin.setObjectName(
            "formSpinBox"
        )
        custom_layout.addRow(
            self._form_label(
                "Lebar Maze"
            ),
            self.custom_width_spin,
        )
        
        # CUSTOM HEIGHT
        self.custom_height_spin = QSpinBox()
        self.custom_height_spin.setRange(
            180,
            270,
        )
        self.custom_height_spin.setValue(
            self.DEFAULT_HEIGHT
        )
        self.custom_height_spin.setSuffix(
            " mm"
        )
        self.custom_height_spin.setObjectName(
            "formSpinBox"
        )
        custom_layout.addRow(
            self._form_label(
                "Tinggi Maze"
            ),
            self.custom_height_spin,
        )
        
        # CUSTOM CELL SIZE
        self.custom_side_spin = QDoubleSpinBox()
        self.custom_side_spin.setRange(
            4.0,
            20.0,
        )
        self.custom_side_spin.setValue(
            self.DEFAULT_SIDE_LENGTH
        )
        self.custom_side_spin.setSingleStep(
            0.5
        )
        self.custom_side_spin.setDecimals(
            1
        )
        self.custom_side_spin.setSuffix(
            " mm"
        )
        self.custom_side_spin.setObjectName(
            "formSpinBox"
        )
        custom_layout.addRow(
            self._form_label(
                "Ukuran Cell"
            ),
            self.custom_side_spin,
        )
        settings_layout.addRow(
            self.custom_card
        )
        main_layout.addWidget(
            settings_card
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
        asset_layout.setSpacing(
            12
        )
        asset_title = QLabel(
            "Asset Maze"
        )
        asset_title.setObjectName(
            "sectionTitle"
        )
        asset_description = QLabel(
            "Pilih satu asset untuk START dan satu "
            "asset untuk FINISH."
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
        
        # ASSET PREVIEW
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
        
        # PICK BUTTON
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
        # Default:
        # Custom disembunyikan.
        self.custom_card.setVisible(
            False
        )
        return page
    
        # TRACING PAGE
    def _create_tracing_page(self):
        page = QWidget()

        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        # MAIN CARD
        card = QFrame()
        card.setObjectName("contentCard")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(
            24, 24, 24, 24
        )
        card_layout.setSpacing(16)

        # HEADER
        header = QHBoxLayout()

        title = QLabel("Tracing")
        title.setObjectName("sectionTitle")

        header.addWidget(title)
        header.addStretch()

        self.tracing_upload_button = QPushButton(
            "Upload Gambar"
        )
        self.tracing_upload_button.setObjectName(
            "primaryButton"
        )
        self.tracing_upload_button.clicked.connect(
            self._upload_tracing_assets
        )

        header.addWidget(
            self.tracing_upload_button
        )

        card_layout.addLayout(header)

        # DESCRIPTION
        description = QLabel(
            "Pilih gambar tracing dari koleksi aset "
            "atau tambahkan gambar sendiri."
        )
        description.setObjectName("materialInfo")
        description.setWordWrap(True)

        card_layout.addWidget(description)

        # CATEGORY FILTER
        self.tracing_category_combo = QComboBox()
        self.tracing_category_combo.setObjectName(
            "formCombo"
        )

        self.tracing_category_combo.addItem(
            "Semua Kategori",
            None,
        )

        for label, folder in self.TRACING_CATEGORIES.items():
            self.tracing_category_combo.addItem(
                label,
                folder,
            )

        self.tracing_category_combo.currentIndexChanged.connect(
            self._refresh_tracing_assets
        )

        card_layout.addWidget(
            self.tracing_category_combo
        )

        # ASSET COUNT
        self.tracing_asset_count = QLabel(
            "0 gambar"
        )
        self.tracing_asset_count.setObjectName(
            "materialInfo"
        )

        card_layout.addWidget(
            self.tracing_asset_count
        )

        # SCROLL AREA
        self.tracing_scroll = QScrollArea()
        self.tracing_scroll.setWidgetResizable(True)
        self.tracing_scroll.setFrameShape(
            QFrame.Shape.NoFrame
        )

        self.tracing_asset_container = QWidget()

        self.tracing_grid = QGridLayout(
            self.tracing_asset_container
        )
        self.tracing_grid.setContentsMargins(
            4, 4, 4, 4
        )
        self.tracing_grid.setSpacing(14)
        self.tracing_grid.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        self.tracing_scroll.setWidget(
            self.tracing_asset_container
        )

        card_layout.addWidget(
            self.tracing_scroll,
            1,
        )

        layout.addWidget(card, 1)

        return page

        # TRACING ASSET SCANNER
    def _get_tracing_assets(self):
        asset_dir = self.TRACING_ASSET_DIR

        if not asset_dir.exists():
            asset_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

        selected_category = (
            self.tracing_category_combo.currentData()
        )

        assets = []

        for category_folder in self.TRACING_CATEGORIES.values():

            if selected_category and (
                category_folder != selected_category
            ):
                continue

            folder = asset_dir / category_folder

            if not folder.exists():
                continue

            for file_path in folder.rglob("*"):

                if not file_path.is_file():
                    continue

                if (
                    file_path.suffix.lower()
                    not in self.SUPPORTED_IMAGE_FORMATS
                ):
                    continue

                assets.append({
                    "name": file_path.name,
                    "path": file_path,
                    "category": category_folder,
                })

        return sorted(
            assets,
            key=lambda item: item["name"].lower(),
        )

    # TRACING ASSET REFRESH
    def _refresh_tracing_assets(self, *_):

        if not hasattr(self, "tracing_grid"):
            return

        # Hapus widget lama
        while self.tracing_grid.count():

            item = self.tracing_grid.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()

        assets = self._get_tracing_assets()

        self.tracing_asset_count.setText(
            f"{len(assets)} gambar"
        )

        if not assets:

            empty_label = QLabel(
                "Belum ada gambar pada kategori ini."
            )
            empty_label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            empty_label.setObjectName(
                "materialInfo"
            )

            self.tracing_grid.addWidget(
                empty_label, 0, 0
            )

            return

        # Hitung jumlah kolom berdasarkan lebar viewport
        viewport_width = (
            self.tracing_scroll.viewport().width()
        )

        min_card_width = 190
        spacing = self.tracing_grid.horizontalSpacing()

        columns = max(
            1,
            (viewport_width + spacing)
            // (min_card_width + spacing)
        )

        columns = int(columns)

        # Simpan jumlah kolom terakhir
        self._tracing_columns = columns

        for index, asset in enumerate(assets):

            row = index // columns
            column = index % columns

            asset_card = self._create_tracing_asset_card(
                asset
            )

            asset_card.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Fixed,
            )

            self.tracing_grid.addWidget(
                asset_card,
                row,
                column,
            )

        # Ratakan lebar kolom
        for column in range(columns):
            self.tracing_grid.setColumnStretch(
                column, 1
            )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not hasattr(self, "tracing_scroll"):
            return
        if not hasattr(self, "tracing_grid"):
            return
        viewport_width = (
            self.tracing_scroll.viewport().width()
        )
        min_card_width = 190
        spacing = self.tracing_grid.horizontalSpacing()
        columns = max(
            1,
            (viewport_width + spacing)
            // (min_card_width + spacing)
        )
        columns = int(columns)
        if columns != getattr(
            self,
            "_tracing_columns",
            0,
        ):
            self._refresh_tracing_assets()

    # TRACING IMAGE PREVIEW
    def _load_tracing_thumbnail(self, file_path):
        preview_size = QSize(180, 140)
        suffix = file_path.suffix.lower()
        # SVG
        if suffix == ".svg":
            renderer = QSvgRenderer(
                str(file_path)
            )
            if not renderer.isValid():
                return None
            image = QPixmap(preview_size)
            image.fill(Qt.GlobalColor.transparent)
            from PySide6.QtGui import QPainter
            painter = QPainter(image)
            renderer.render(
                painter,
            )
            painter.end()
            return image
        # PNG / JPG
        reader = QImageReader(str(file_path))
        reader.setAutoTransform(True)
        pixmap = QPixmap.fromImage(
            reader.read()
        )
        if pixmap.isNull():
            return None
        return pixmap.scaled(
            preview_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

    # TRACING ASSET CARD
    def _create_tracing_asset_card(self, asset):

        card = QFrame()
        card.setObjectName("filterCard")

        card.setMinimumWidth(0)
        card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(
            10, 10, 10, 10
        )
        card_layout.setSpacing(8)

        # IMAGE
        image_label = QLabel()
        image_label.setMinimumSize(100, 100)
        image_label.setMaximumHeight(160)
        image_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        image_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        pixmap = self._load_tracing_thumbnail(
            asset["path"]
        )

        if pixmap:
            image_label.setPixmap(pixmap)
        else:
            image_label.setText(
                "Preview gagal"
            )

        card_layout.addWidget(
            image_label,
            0,
            Qt.AlignmentFlag.AlignCenter,
        )

        # FILE NAME
        name_label = QLabel(
            asset["name"]
        )
        name_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        name_label.setWordWrap(True)
        name_label.setObjectName(
            "formLabel"
        )

        card_layout.addWidget(name_label)

        # CATEGORY
        category_label = QLabel(
            asset["category"].capitalize()
        )
        category_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        category_label.setObjectName(
            "materialInfo"
        )

        card_layout.addWidget(
            category_label
        )

        # DELETE BUTTON
        delete_button = QPushButton(
            "Hapus"
        )
        delete_button.setObjectName(
            "secondaryButton"
        )

        delete_button.clicked.connect(
            lambda checked=False, path=asset["path"]:
            self._delete_tracing_asset(path)
        )

        card_layout.addWidget(
            delete_button
        )

        return card

    # UPLOAD TRACING ASSETS
    def _upload_tracing_assets(self):

        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Pilih Gambar Tracing",
            "",
            (
                "Image Files (*.png *.jpg *.jpeg *.svg);;"
                "PNG (*.png);;"
                "JPG (*.jpg *.jpeg);;"
                "SVG (*.svg)"
            ),
        )

        if not files:
            return

        # Pilih kategori setelah file dipilih
        categories = list(
            self.TRACING_CATEGORIES.keys()
        )

        category, accepted = QInputDialog.getItem(
            self,
            "Pilih Kategori",
            "Simpan gambar ke kategori:",
            categories,
            0,
            False,
        )

        if not accepted:
            return

        category_folder = (
            self.TRACING_CATEGORIES[category]
        )

        destination = (
            self.TRACING_ASSET_DIR
            / category_folder
        )

        destination.mkdir(
            parents=True,
            exist_ok=True,
        )

        uploaded = 0
        skipped = []

        for file_name in files:

            source = Path(file_name)

            if (
                source.suffix.lower()
                not in self.SUPPORTED_IMAGE_FORMATS
            ):
                skipped.append(source.name)
                continue

            # Validasi konten gambar
            if source.suffix.lower() == ".svg":

                renderer = QSvgRenderer(str(source))

                if not renderer.isValid():
                    skipped.append(source.name)
                    continue

            else:

                reader = QImageReader(str(source))

                if not reader.canRead():
                    skipped.append(source.name)
                    continue

            # Hindari menimpa file yang sudah ada
            target = destination / source.name

            counter = 1

            while target.exists():

                target = destination / (
                    f"{source.stem}_{counter}"
                    f"{source.suffix}"
                )

                counter += 1

            try:

                shutil.copy2(
                    source,
                    target,
                )

                uploaded += 1

            except Exception as error:

                skipped.append(
                    f"{source.name}: {error}"
                )

        # Refresh tampilan
        self._refresh_tracing_assets()

        message = (
            f"Berhasil mengunggah {uploaded} gambar."
        )

        if skipped:
            message += (
                "\n\nGambar yang dilewati:\n"
                + "\n".join(skipped)
            )

        QMessageBox.information(
            self,
            "Upload Selesai",
            message,
        )

    # DELETE TRACING ASSET
    def _delete_tracing_asset(self, file_path):

        confirm = QMessageBox.question(
            self,
            "Hapus Gambar",
            (
                f"Yakin ingin menghapus "
                f"'{file_path.name}'?\n\n"
                "File akan dihapus secara permanen."
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:

            file_path.unlink()

            self._refresh_tracing_assets()

            QMessageBox.information(
                self,
                "Berhasil",
                "Gambar berhasil dihapus.",
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Gagal Menghapus",
                str(error),
            )
    
    # ACTIVITY SWITCH
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

            self._refresh_tracing_assets()

    # DIFFICULTY
    def _difficulty_changed(
        self,
        difficulty,
    ):
        is_custom = (
            difficulty == "Custom"
        )
        self.custom_card.setVisible(
            is_custom
        )
    def _get_maze_settings(self):
        difficulty = (
            self.difficulty_combo.currentText()
        )
        if difficulty == "Custom":
            return {
                "difficulty": "Custom",
                "width_mm": float(
                    self.custom_width_spin.value()
                ),
                "height_mm": float(
                    self.custom_height_spin.value()
                ),
                "side_length_mm": float(
                    self.custom_side_spin.value()
                ),
            }
        preset = self.DIFFICULTY_PRESETS[
            difficulty
        ]
        return {
            "difficulty": difficulty,
            "width_mm": float(
                preset["width"]
            ),
            "height_mm": float(
                preset["height"]
            ),
            "side_length_mm": float(
                preset["side_length"]
            ),
        }
    # HELPER
    def _form_label(
        self,
        text,
    ):
        label = QLabel(
            text
        )
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
        frame.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        layout = QVBoxLayout(
            frame
        )
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
        slot_index = 0 if title == "START" else 1
        frame.mousePressEvent = (
            lambda event, index=slot_index:
            self._open_asset_picker_for_target(index)
        )
        return {
            "frame": frame,
            "svg": svg_widget,
            "status": status_label,
        }
    
    # MATERIAL DATA
    def set_material_data(
        self,
        material_data,
    ):
        self.material_data = dict(
            material_data
        )
        self.instruction_input.setText(
            self.DEFAULT_INSTRUCTION
        )

    # RESET
    def reset_form(self):
        self.material_data = {}
        self.activity_type = "Maze"
        # Activity
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
        # Difficulty
        self.difficulty_combo.blockSignals(
            True
        )
        self.difficulty_combo.setCurrentText(
            "Mudah"
        )
        self.difficulty_combo.blockSignals(
            False
        )
        self.custom_card.setVisible(
            False
        )
        # Maze settings
        self.custom_width_spin.setValue(
            self.DEFAULT_WIDTH
        )
        self.custom_height_spin.setValue(
            self.DEFAULT_HEIGHT
        )
        self.custom_side_spin.setValue(
            self.DEFAULT_SIDE_LENGTH
        )
        self.instruction_input.setText(
            self.DEFAULT_INSTRUCTION
        )
        # Assets
        self.selected_assets = [None, None]
        self.active_asset_target = 0
        self._clear_asset_slot(
            self.start_preview
        )
        self._clear_asset_slot(
            self.finish_preview
        )
        self.preview_button.setEnabled(
            True
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

    # ASSET PICKER
    def _open_asset_picker(self):
        self._open_asset_picker_for_target(0)
    def _open_asset_picker_for_target(self, target_index):
        dialog = AssetPickerDialog(self, item_label="Karakter")
        self.active_asset_target = target_index
        dialog.set_target(
            target_index,
            2,
        )
        dialog.asset_selected.connect(
            self._asset_selected
        )
        dialog.exec()
    def _asset_selected(self, asset_name):
        target_index = self.active_asset_target
        # Jangan izinkan START dan FINISH menggunakan
        # asset yang sama.
        other_index = (
            1
            if target_index == 0
            else 0
        )
        if (
            self.selected_assets[other_index]
            == asset_name
        ):
            QMessageBox.warning(
                self,
                "Asset Duplikat",
                (
                    "START dan FINISH harus "
                    "menggunakan asset yang berbeda."
                ),
            )
            return
        self.selected_assets[target_index] = (
            asset_name
        )
        if target_index == 0:
            self._set_asset_slot(
                self.start_preview,
                asset_name,
            )
        else:
            self._set_asset_slot(
                self.finish_preview,
                asset_name,
            )
        if target_index == 0:
            self.active_asset_target = 1
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
    # PREVIEW
    def _preview(self):
        if self.activity_type != "Maze":
            return
        if (
            self.selected_assets[0] is None
            or self.selected_assets[1] is None
        ):
            QMessageBox.warning(
                self,
                "Asset Belum Lengkap",
                (
                    "Pilih asset START dan FINISH "
                    "terlebih dahulu."
                ),
            )
            return
        maze_settings = (
            self._get_maze_settings()
        )
        instruction = (
            self.instruction_input.text().strip()
        )
        if not instruction:
            instruction = (
                self.DEFAULT_INSTRUCTION
            )
        try:
            maze_generator = MazeGenerator(
                width_mm=(
                    maze_settings["width_mm"]
                ),
                height_mm=(
                    maze_settings["height_mm"]
                ),
                side_length_mm=(
                    maze_settings[
                        "side_length_mm"
                    ]
                ),
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
            # Parent activity
            "activity_type": (
                "Maze / Tracing"
            ),
            # Sub activity
            "sub_activity_type": "Maze",
            "title": title,
            "difficulty": (
                maze_settings["difficulty"]
            ),
            "maze_generator": (
                maze_generator
            ),
            "start_asset": (
                self.selected_assets[0]
            ),
            "finish_asset": (
                self.selected_assets[1]
            ),
            "width_mm": (
                maze_settings["width_mm"]
            ),
            "height_mm": (
                maze_settings["height_mm"]
            ),
            "side_length_mm": (
                maze_settings[
                    "side_length_mm"
                ]
            ),
            "instruction": instruction,
        }
        self.preview_requested.emit(
            maze_data
        )