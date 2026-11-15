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
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class WorksheetEditor(QWidget):
    back_requested = Signal()
    preview_requested = Signal(dict)

    WORKSHEET_TYPES = [
        "Menghitung",
        "Memilih Jawaban",
        "Menulis / Tracing",
    ]

    def __init__(self):
        super().__init__()

        self.setObjectName("worksheetEditor")
        self.material_data = {}
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(36, 32, 36, 32)
        main_layout.setSpacing(20)

        title = QLabel("Editor Worksheet")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Susun soal Numerasi, pilihan jawaban, atau latihan menulis angka."
        )
        subtitle.setObjectName("pageSubtitle")

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        info_card = QFrame()
        info_card.setObjectName("contentCard")
        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(24, 20, 24, 20)
        info_layout.setSpacing(8)

        self.material_info = QLabel()
        self.material_info.setObjectName("materialInfo")
        info_layout.addWidget(self.material_info)
        main_layout.addWidget(info_card)

        worksheet_card = QFrame()
        worksheet_card.setObjectName("contentCard")

        form_layout = QFormLayout(worksheet_card)
        form_layout.setContentsMargins(24, 24, 24, 24)
        form_layout.setHorizontalSpacing(24)
        form_layout.setVerticalSpacing(18)

        self.activity_title_input = QLineEdit()
        self.activity_title_input.setPlaceholderText("Contoh: Petualangan Angka")
        self.activity_title_input.setObjectName("formInput")
        form_layout.addRow(
            self._create_label("Judul Aktivitas"),
            self.activity_title_input,
        )

        self.instruction_input = QTextEdit()
        self.instruction_input.setPlaceholderText(
            "Contoh: Perhatikan soal, lalu kerjakan dengan teliti."
        )
        self.instruction_input.setObjectName("formTextEdit")
        self.instruction_input.setMinimumHeight(85)
        form_layout.addRow(
            self._create_label("Instruksi"),
            self.instruction_input,
        )

        self.worksheet_type_combo = QComboBox()
        self.worksheet_type_combo.setObjectName("formCombo")
        self.worksheet_type_combo.addItems(self.WORKSHEET_TYPES)
        self.worksheet_type_combo.currentTextChanged.connect(
            self._update_type_fields
        )
        form_layout.addRow(
            self._create_label("Jenis Worksheet"),
            self.worksheet_type_combo,
        )

        self.question_input = QTextEdit()
        self.question_input.setPlaceholderText(
            "Contoh: Berapa hasil dari 2 + 1?"
        )
        self.question_input.setObjectName("formTextEdit")
        self.question_input.setMinimumHeight(75)
        form_layout.addRow(
            self._create_label("Pertanyaan / Perintah"),
            self.question_input,
        )

        self.answer_label = self._create_label("Jawaban Benar")
        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("Contoh: 3")
        self.answer_input.setObjectName("formInput")
        form_layout.addRow(self.answer_label, self.answer_input)

        self.options_label = self._create_label("Pilihan Jawaban")
        self.options_input = QLineEdit()
        self.options_input.setPlaceholderText("Pisahkan dengan koma. Contoh: 2, 3, 4, 5")
        self.options_input.setObjectName("formInput")
        form_layout.addRow(self.options_label, self.options_input)

        self.tracing_label = self._create_label("Angka untuk Tracing")
        self.tracing_input = QLineEdit()
        self.tracing_input.setPlaceholderText("Contoh: 1 2 3")
        self.tracing_input.setObjectName("formInput")
        form_layout.addRow(self.tracing_label, self.tracing_input)

        main_layout.addWidget(worksheet_card)

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

        self._update_type_fields(self.worksheet_type_combo.currentText())

    def _create_label(self, text: str):
        label = QLabel(text)
        label.setObjectName("formLabel")
        return label

    def _update_type_fields(self, worksheet_type: str):
        is_choice = worksheet_type == "Memilih Jawaban"
        is_tracing = worksheet_type == "Menulis / Tracing"
        is_counting = worksheet_type == "Menghitung"

        self.answer_label.setText(
            "Jawaban Benar" if is_choice else "Jumlah / Jawaban"
        )
        self.answer_label.setVisible(not is_tracing)
        self.answer_input.setVisible(not is_tracing)

        self.options_label.setVisible(is_choice)
        self.options_input.setVisible(is_choice)

        self.tracing_label.setVisible(is_tracing)
        self.tracing_input.setVisible(is_tracing)

        if is_counting:
            self.question_input.setPlaceholderText(
                "Contoh: Ada berapa apel?"
            )
            self.answer_input.setPlaceholderText("Masukkan jumlah objek")
        elif is_choice:
            self.question_input.setPlaceholderText(
                "Contoh: Berapa hasil dari 2 + 1?"
            )
            self.answer_input.setPlaceholderText("Jawaban benar, contoh: 3")
        else:
            self.question_input.setPlaceholderText(
                "Contoh: Tebalkan angka berikut."
            )

    def set_material_data(self, material_data: dict):
        self.material_data = dict(material_data or {})

        title = self.material_data.get("title", "")
        category = self.material_data.get("category", "")
        age = self.material_data.get("age", "")
        activity_type = self.material_data.get("activity_type", "Worksheet")

        self.material_info.setText(
            f"<b>{title}</b>  •  {category}  •  {age}  •  {activity_type}"
        )
        self.activity_title_input.setText(title)

    def _preview(self):
        activity_title = self.activity_title_input.text().strip()
        instruction = self.instruction_input.toPlainText().strip()
        question = self.question_input.toPlainText().strip()
        worksheet_type = self.worksheet_type_combo.currentText()

        if not activity_title:
            QMessageBox.warning(self, "Data Belum Lengkap", "Judul aktivitas wajib diisi.")
            self.activity_title_input.setFocus()
            return

        if not question:
            QMessageBox.warning(
                self,
                "Data Belum Lengkap",
                "Pertanyaan atau perintah aktivitas wajib diisi.",
            )
            self.question_input.setFocus()
            return

        worksheet_data = {
            **self.material_data,
            "activity_title": activity_title,
            "instruction": instruction or "Kerjakan aktivitas berikut.",
            "worksheet_type": worksheet_type,
            "question": question,
        }

        if worksheet_type == "Menulis / Tracing":
            tracing_text = self.tracing_input.text().strip()
            if not tracing_text:
                QMessageBox.warning(
                    self,
                    "Data Belum Lengkap",
                    "Isi angka atau pola yang akan ditelusuri.",
                )
                self.tracing_input.setFocus()
                return
            worksheet_data["tracing_text"] = tracing_text
        else:
            answer = self.answer_input.text().strip()
            if not answer:
                QMessageBox.warning(
                    self,
                    "Data Belum Lengkap",
                    "Jawaban atau jumlah wajib diisi.",
                )
                self.answer_input.setFocus()
                return
            worksheet_data["answer"] = answer

        if worksheet_type == "Memilih Jawaban":
            raw_options = self.options_input.text().strip()
            options = [item.strip() for item in raw_options.split(",") if item.strip()]
            if len(options) < 2:
                QMessageBox.warning(
                    self,
                    "Pilihan Belum Lengkap",
                    "Masukkan minimal dua pilihan jawaban, pisahkan dengan koma.",
                )
                self.options_input.setFocus()
                return
            if len(options) > 4:
                QMessageBox.warning(
                    self,
                    "Terlalu Banyak Pilihan",
                    "Untuk template worksheet ini, maksimal empat pilihan jawaban.",
                )
                self.options_input.setFocus()
                return
            if len(set(options)) != len(options):
                QMessageBox.warning(
                    self,
                    "Pilihan Duplikat",
                    "Setiap pilihan jawaban harus berbeda.",
                )
                self.options_input.setFocus()
                return
            if answer not in options:
                QMessageBox.warning(
                    self,
                    "Jawaban Tidak Ada",
                    "Jawaban benar harus tercantum di dalam pilihan jawaban.",
                )
                self.answer_input.setFocus()
                return
            worksheet_data["options"] = options

        if worksheet_type == "Menghitung":
            try:
                count = int(worksheet_data["answer"])
            except ValueError:
                QMessageBox.warning(
                    self,
                    "Jumlah Tidak Valid",
                    "Jumlah objek harus berupa angka bulat.",
                )
                self.answer_input.setFocus()
                return
            if count < 1:
                QMessageBox.warning(
                    self,
                    "Jumlah Tidak Valid",
                    "Jumlah objek minimal 1.",
                )
                self.answer_input.setFocus()
                return

        self.preview_requested.emit(worksheet_data)

    def reset_form(self):
        self.material_data = {}
        self.material_info.clear()
        self.activity_title_input.clear()
        self.instruction_input.clear()
        self.question_input.clear()
        self.answer_input.clear()
        self.options_input.clear()
        self.tracing_input.clear()
        self.worksheet_type_combo.setCurrentIndex(0)
        self._update_type_fields(self.worksheet_type_combo.currentText())
