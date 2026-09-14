from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class WorksheetEditor(QWidget):
    back_requested = Signal()
    preview_requested = Signal(dict)

    def __init__(self):
        super().__init__()

        self.setObjectName("worksheetEditor")

        self.material_data = {}

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(36, 32, 36, 32)
        main_layout.setSpacing(20)

        # =========================
        # HEADER
        # =========================

        title = QLabel("Editor Worksheet")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Susun isi worksheet sebelum melihat preview dan mencetak."
        )
        subtitle.setObjectName("pageSubtitle")

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        # =========================
        # MATERIAL INFO
        # =========================

        info_card = QFrame()
        info_card.setObjectName("contentCard")

        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(24, 20, 24, 20)
        info_layout.setSpacing(8)

        self.material_info = QLabel()
        self.material_info.setObjectName("materialInfo")

        info_layout.addWidget(self.material_info)

        main_layout.addWidget(info_card)

        # =========================
        # WORKSHEET FORM
        # =========================

        worksheet_card = QFrame()
        worksheet_card.setObjectName("contentCard")

        form_layout = QFormLayout(worksheet_card)
        form_layout.setContentsMargins(24, 24, 24, 24)
        form_layout.setHorizontalSpacing(24)
        form_layout.setVerticalSpacing(18)

        # Activity title
        self.activity_title_input = QLineEdit()
        self.activity_title_input.setPlaceholderText(
            "Contoh: Hitung Apelnya"
        )
        self.activity_title_input.setObjectName("formInput")

        form_layout.addRow(
            self._create_label("Judul Aktivitas"),
            self.activity_title_input,
        )

        # Instruction
        self.instruction_input = QTextEdit()
        self.instruction_input.setPlaceholderText(
            "Contoh: Hitung jumlah apel, lalu lingkari angka yang benar."
        )
        self.instruction_input.setObjectName("formTextEdit")
        self.instruction_input.setMinimumHeight(100)

        form_layout.addRow(
            self._create_label("Instruksi"),
            self.instruction_input,
        )

        # Worksheet type
        self.worksheet_type_combo = QComboBox()
        self.worksheet_type_combo.setObjectName("formCombo")

        self.worksheet_type_combo.addItems([
            "Menghitung",
            "Mencocokkan",
            "Memilih Jawaban",
            "Mewarnai",
            "Menarik Garis",
            "Menghubungkan Titik",
            "Menulis / Tracing",
        ])

        form_layout.addRow(
            self._create_label("Jenis Worksheet"),
            self.worksheet_type_combo,
        )

        # Question
        self.question_input = QTextEdit()
        self.question_input.setPlaceholderText(
            "Contoh: Ada berapa apel?"
        )
        self.question_input.setObjectName("formTextEdit")
        self.question_input.setMinimumHeight(80)

        form_layout.addRow(
            self._create_label("Pertanyaan"),
            self.question_input,
        )

        # Answer
        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText(
            "Contoh: 3"
        )
        self.answer_input.setObjectName("formInput")

        form_layout.addRow(
            self._create_label("Jawaban Benar"),
            self.answer_input,
        )

        main_layout.addWidget(worksheet_card)

        # =========================
        # FOOTER
        # =========================

        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(12)

        back_button = QPushButton("← Kembali")
        back_button.setObjectName("secondaryButton")
        back_button.setCursor(Qt.PointingHandCursor)

        preview_button = QPushButton("Preview Worksheet →")
        preview_button.setObjectName("primaryButton")
        preview_button.setCursor(Qt.PointingHandCursor)

        back_button.clicked.connect(self.back_requested.emit)
        preview_button.clicked.connect(self._preview)

        footer_layout.addWidget(back_button)
        footer_layout.addStretch()
        footer_layout.addWidget(preview_button)

        main_layout.addLayout(footer_layout)

    def _create_label(self, text: str):
        label = QLabel(text)
        label.setObjectName("formLabel")
        return label

    def set_material_data(self, material_data: dict):
        self.material_data = material_data

        self.material_info.setText(
            f"<b>{material_data['title']}</b>  •  "
            f"{material_data['category']}  •  "
            f"{material_data['age']}  •  "
            f"{material_data['activity_type']}"
        )

        self.activity_title_input.setText(
            material_data["title"]
        )

    def _preview(self):
        activity_title = self.activity_title_input.text().strip()
        instruction = self.instruction_input.toPlainText().strip()
        question = self.question_input.toPlainText().strip()
        answer = self.answer_input.text().strip()

        worksheet_data = {
            **self.material_data,
            "activity_title": activity_title,
            "instruction": instruction,
            "worksheet_type": self.worksheet_type_combo.currentText(),
            "question": question,
            "answer": answer,
        }

        self.preview_requested.emit(worksheet_data)

    def reset_form(self):
        self.material_data = {}

        self.material_info.clear()
        self.activity_title_input.clear()
        self.instruction_input.clear()
        self.question_input.clear()
        self.answer_input.clear()

        self.worksheet_type_combo.setCurrentIndex(0)