from PySide6.QtCore import Qt, Signal
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


class MaterialEditor(QWidget):
    back_requested = Signal()
    setup_completed = Signal(dict)

    def __init__(self):
        super().__init__()

        self.setObjectName("materialEditor")

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(36, 32, 36, 32)
        main_layout.setSpacing(24)

        # =========================
        # HEADER
        # =========================

        title = QLabel("Buat Materi")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Tentukan informasi dasar sebelum membuat aktivitas."
        )
        subtitle.setObjectName("pageSubtitle")

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        # =========================
        # FORM CARD
        # =========================

        form_card = QFrame()
        form_card.setObjectName("contentCard")

        form_layout = QFormLayout(form_card)
        form_layout.setContentsMargins(28, 28, 28, 28)
        form_layout.setHorizontalSpacing(24)
        form_layout.setVerticalSpacing(18)

        # Judul
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText(
            "Contoh: Mengenal Angka 1–5"
        )
        self.title_input.setObjectName("formInput")

        form_layout.addRow(
            self._create_label("Judul Materi"),
            self.title_input,
        )

        # Kategori
        self.category_combo = QComboBox()
        self.category_combo.setObjectName("formCombo")

        self.category_combo.addItems([
            "Numerasi",
            "Bahasa",
            "Warna",
            "Bentuk",
            "Hewan",
            "Motorik",
            "Puzzle",
            "Aktivitas Dunia Nyata",
        ])

        form_layout.addRow(
            self._create_label("Kategori"),
            self.category_combo,
        )

        # Usia
        self.age_combo = QComboBox()
        self.age_combo.setObjectName("formCombo")

        self.age_combo.addItems([
            "3 Tahun",
            "4 Tahun",
            "5 Tahun",
            "6 Tahun",
            "7 Tahun",
        ])

        self.age_combo.setCurrentText("5 Tahun")

        form_layout.addRow(
            self._create_label("Target Usia"),
            self.age_combo,
        )

        # Jenis aktivitas
        self.activity_combo = QComboBox()
        self.activity_combo.setObjectName("formCombo")

        self.activity_combo.addItems([
            "Worksheet",
            "Flashcard",
            "Matching Card",
            "Maze",
            "Tracing",
            "Coloring",
            "Puzzle",
            "Board Game",
            "Quest",
            "Certificate",
        ])

        form_layout.addRow(
            self._create_label("Jenis Aktivitas"),
            self.activity_combo,
        )

        main_layout.addWidget(form_card)

        main_layout.addStretch()

        # =========================
        # FOOTER BUTTON
        # =========================

        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(12)

        cancel_button = QPushButton("Batal")
        cancel_button.setObjectName("secondaryButton")
        cancel_button.setCursor(Qt.PointingHandCursor)

        continue_button = QPushButton("Lanjutkan  →")
        continue_button.setObjectName("primaryButton")
        continue_button.setCursor(Qt.PointingHandCursor)

        cancel_button.clicked.connect(self.back_requested.emit)
        continue_button.clicked.connect(self._continue)

        footer_layout.addStretch()
        footer_layout.addWidget(cancel_button)
        footer_layout.addWidget(continue_button)

        main_layout.addLayout(footer_layout)

    def _create_label(self, text: str):
        label = QLabel(text)
        label.setObjectName("formLabel")
        return label

    def _continue(self):
        title = self.title_input.text().strip()

        if not title:
            QMessageBox.warning(
                self,
                "Data Belum Lengkap",
                "Judul materi harus diisi.",
            )

            self.title_input.setFocus()
            return

        material_data = {
            "title": title,
            "category": self.category_combo.currentText(),
            "age": self.age_combo.currentText(),
            "activity_type": self.activity_combo.currentText(),
        }

        self.setup_completed.emit(material_data)

    def reset_form(self):
        self.title_input.clear()
        self.category_combo.setCurrentIndex(0)
        self.age_combo.setCurrentText("5 Tahun")
        self.activity_combo.setCurrentIndex(0)