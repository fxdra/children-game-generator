from pathlib import Path
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
    QInputDialog,
    QMessageBox,
)

from app.services.openmoji_asset import OpenMojiAssetService

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("dashboard")

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(36, 32, 36, 32)
        main_layout.setSpacing(24)

        # Header
        header_layout = QHBoxLayout()

        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)

        title = QLabel("Dashboard")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Buat dan kelola materi edukasi anak dengan mudah."
        )
        subtitle.setObjectName("pageSubtitle")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        main_layout.addLayout(header_layout)

        # Statistics
        stats_layout = QGridLayout()
        stats_layout.setHorizontalSpacing(16)
        stats_layout.setVerticalSpacing(16)

        # Folder output
        OUTPUT_DIR = Path(__file__).resolve().parents[2] / "output"

        materi_count = sum(
            1 for file in OUTPUT_DIR.rglob("*")
            if file.is_file()
        ) if OUTPUT_DIR.exists() else 0

        stats_layout.addWidget(
            self._create_stat_card(
                "Materi",
                str(materi_count),
                "Materi edukasi yang dibuat",
            ),
            0,
            0,
        )

        # Folder templates
        TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates"

        template_count = sum(
            1 for file in TEMPLATES_DIR.rglob("*")
            if file.is_file()
        ) if TEMPLATES_DIR.exists() else 0

        stats_layout.addWidget(
            self._create_stat_card(
                "Template",
                str(template_count),
                "Template yang tersedia",
            ),
            0,
            1,
        )

        # Folder assets
        ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets"
        IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg", ".webp"}

        asset_count = sum(
            1 for file in ASSETS_DIR.rglob("*")
            if file.is_file() and file.suffix.lower() in IMAGE_EXTENSIONS
        ) if ASSETS_DIR.exists() else 0

        stats_layout.addWidget(
            self._create_stat_card(
                "Asset",
                str(asset_count),
                "Ilustrasi, Gambar dan Ikon",
            ),
            0,
            2,
        )

        main_layout.addLayout(stats_layout)

        # Recent materials
        recent_frame = QFrame()
        recent_frame.setObjectName("contentCard")

        recent_layout = QVBoxLayout(recent_frame)
        recent_layout.setContentsMargins(24, 24, 24, 24)
        recent_layout.setSpacing(12)

        recent_title = QLabel("Materi Terakhir")
        recent_title.setObjectName("sectionTitle")

        recent_layout.addWidget(recent_title)

        # Folder output
        output_dir = Path(__file__).resolve().parents[2] / "output"

        if output_dir.exists():
            output_files = [
                file for file in output_dir.rglob("*")
                if file.is_file()
            ]

            # Urutkan berdasarkan waktu modifikasi terbaru
            output_files.sort(
                key=lambda file: file.stat().st_mtime,
                reverse=True,
            )

            recent_files = output_files[:5]

            if recent_files:
                for file in recent_files:
                    file_frame = QFrame()
                    file_layout = QVBoxLayout(file_frame)
                    file_layout.setContentsMargins(0, 6, 0, 6)
                    file_layout.setSpacing(3)

                    file_name = QLabel(file.name)
                    file_name.setObjectName("sectionTitle")
                    file_name.setCursor(Qt.CursorShape.PointingHandCursor)

                    file_name.mouseDoubleClickEvent = (
                        lambda event, path=file, label=file_name:
                        self.rename_output_file(path, label)
                    )

                    modified = datetime.fromtimestamp(
                        file.stat().st_mtime
                    ).strftime("%d/%m/%Y %H:%M")

                    file_info = QLabel(
                        f"{file.suffix.upper().replace('.', '')} • {modified}"
                    )
                    file_info.setObjectName("emptyText")

                    file_layout.addWidget(file_name)
                    file_layout.addWidget(file_info)

                    recent_layout.addWidget(file_frame)
            else:
                recent_description = QLabel(
                    "Belum ada materi. Buat materi pertama untuk memulai."
                )
                recent_description.setObjectName("emptyText")
                recent_layout.addWidget(recent_description)
        else:
            recent_description = QLabel(
                "Folder output belum tersedia."
            )
            recent_description.setObjectName("emptyText")
            recent_layout.addWidget(recent_description)

        recent_layout.addStretch()

        main_layout.addWidget(recent_frame, 1)

    def _create_stat_card(
        self,
        title: str,
        value: str,
        description: str,
    ):
        card = QFrame()
        card.setObjectName("statCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(6)

        title_label = QLabel(title)
        title_label.setObjectName("statTitle")

        value_label = QLabel(value)
        value_label.setObjectName("statValue")

        description_label = QLabel(description)
        description_label.setObjectName("statDescription")

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(description_label)

        return card
    
    def rename_output_file(self, file_path, name_label):
        file_path = Path(file_path)

        new_name, accepted = QInputDialog.getText(
            self,
            "Rename Materi",
            "Nama tugas baru:",
            text=file_path.stem,
        )

        if not accepted:
            return

        new_name = new_name.strip()

        if not new_name:
            QMessageBox.warning(
                self,
                "Nama Tidak Valid",
                "Nama tugas tidak boleh kosong.",
            )
            return

        # Hindari karakter yang tidak valid pada nama file Windows.
        invalid_chars = '<>:"/\\|?*'
        if any(char in new_name for char in invalid_chars):
            QMessageBox.warning(
                self,
                "Nama Tidak Valid",
                "Nama mengandung karakter yang tidak diperbolehkan.",
            )
            return

        new_path = file_path.with_name(
            new_name + file_path.suffix
        )

        if new_path.exists():
            QMessageBox.warning(
                self,
                "Rename Gagal",
                "File dengan nama tersebut sudah tersedia.",
            )
            return

        try:
            file_path.rename(new_path)
            name_label.setText(new_path.name)

            QMessageBox.information(
                self,
                "Berhasil",
                "Nama materi berhasil diperbarui.",
            )

        except OSError as error:
            QMessageBox.critical(
                self,
                "Rename Gagal",
                f"Tidak dapat mengubah nama file.\n\n{error}",
            )