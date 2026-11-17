from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
    QComboBox, QSpinBox, QLineEdit, QPushButton, QMessageBox, QScrollArea
)

from app.services.openmoji_asset import OpenMojiAssetService
from app.ui.asset_picker import AssetPickerDialog


class NumerasiMatchingCardEditor(QWidget):
    back_requested = Signal()
    preview_requested = Signal(dict)

    MODES = [
        "Angka ↔ Jumlah benda",
        "Angka ↔ Nama bilangan",
        "Operasi hitung ↔ Hasil",
    ]

    def __init__(self):
        super().__init__()
        self.material_data = {}
        self.pair_inputs = []
        self._setup_ui()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 26, 32, 26)
        root.setSpacing(14)

        heading = QLabel("Editor Numerasi — Matching Card")
        heading.setObjectName("pageTitle")
        root.addWidget(heading)
        subtitle = QLabel("Buat kartu pasangan angka, jumlah benda, nama bilangan, atau operasi hitung.")
        subtitle.setObjectName("pageSubtitle")
        root.addWidget(subtitle)

        self.material_info = QLabel("Belum ada materi")
        self.material_info.setWordWrap(True)
        root.addWidget(self.material_info)

        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Mode Matching:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(self.MODES)
        self.mode_combo.currentTextChanged.connect(self._update_mode)
        mode_row.addWidget(self.mode_combo, 1)
        root.addLayout(mode_row)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.rows_widget = QWidget()
        self.rows_layout = QVBoxLayout(self.rows_widget)
        self.rows_layout.setSpacing(10)
        self.scroll.setWidget(self.rows_widget)
        root.addWidget(self.scroll, 1)

        self._create_pair_rows()

        footer = QHBoxLayout()
        footer.setContentsMargins(0, 10, 0, 0)
        footer.setSpacing(12)

        back = QPushButton("← Kembali")
        back.setObjectName("numerasiBackButton")
        back.setMinimumHeight(40)
        back.setCursor(Qt.PointingHandCursor)
        back.clicked.connect(self.back_requested.emit)
        footer.addWidget(back)
        footer.addStretch()

        preview = QPushButton("Preview Matching Card")
        preview.setObjectName("numerasiPreviewButton")
        preview.setMinimumHeight(40)
        preview.setCursor(Qt.PointingHandCursor)
        preview.clicked.connect(self._preview)
        footer.addWidget(preview)
        root.addLayout(footer)

        self.setStyleSheet("""
            QPushButton#numerasiBackButton {
                background-color: #E2E8F0;
                color: #1E293B;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 8px 18px;
                font-weight: 600;
            }
            QPushButton#numerasiBackButton:hover {
                background-color: #CBD5E1;
            }
            QPushButton#numerasiPreviewButton {
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 8px 18px;
                font-weight: 600;
            }
            QPushButton#numerasiPreviewButton:hover {
                background-color: #1D4ED8;
            }
        """)

    def _create_pair_rows(self):
        for i in range(5):
            frame = QFrame()
            frame.setObjectName("contentCard")
            grid = QGridLayout(frame)
            grid.addWidget(QLabel(f"Pasangan {i + 1}"), 0, 0, 1, 3)

            number = QSpinBox()
            number.setRange(1, 20)
            number.setValue(i + 1)
            number.setToolTip("Jumlah benda dibatasi 1–20 agar kartu tetap terbaca.")

            asset = QPushButton("Pilih ilustrasi")
            asset.setMinimumWidth(150)
            asset.clicked.connect(lambda checked=False, idx=i: self._open_asset_picker(idx))

            word = QLineEdit()
            word.setPlaceholderText("Nama bilangan, contoh: lima")
            question = QLineEdit()
            question.setPlaceholderText("Operasi, contoh: 3 + 2")
            answer = QLineEdit()
            answer.setPlaceholderText("Hasil, contoh: 5")

            grid.addWidget(QLabel("Angka / nilai:"), 1, 0)
            grid.addWidget(number, 1, 1)
            grid.addWidget(QLabel("Ilustrasi:"), 2, 0)
            grid.addWidget(asset, 2, 1)
            grid.addWidget(QLabel("Nama bilangan:"), 3, 0)
            grid.addWidget(word, 3, 1, 1, 2)
            grid.addWidget(QLabel("Operasi:"), 4, 0)
            grid.addWidget(question, 4, 1)
            grid.addWidget(QLabel("Hasil:"), 4, 2)
            grid.addWidget(answer, 5, 1, 1, 2)

            self.rows_layout.addWidget(frame)
            self.pair_inputs.append({
                "frame": frame, "number": number, "asset": asset,
                "word": word, "question": question, "answer": answer,
            })
        self._update_mode(self.mode_combo.currentText())

    def _update_mode(self, mode):
        for row in self.pair_inputs:
            is_quantity = mode == self.MODES[0]
            is_word = mode == self.MODES[1]
            row["number"].setVisible(True)
            row["asset"].setVisible(is_quantity)
            row["word"].setVisible(is_word)
            row["question"].setVisible(not is_quantity and not is_word)
            row["answer"].setVisible(not is_quantity and not is_word)
            layout = row["frame"].layout()
            for pos in range(layout.count()):
                widget = layout.itemAt(pos).widget()
                if isinstance(widget, QLabel):
                    text = widget.text()
                    widget.setVisible(
                        text.startswith("Pasangan") or
                        text == "Angka / nilai:" or
                        (text == "Ilustrasi:" and is_quantity) or
                        (text == "Nama bilangan:" and is_word) or
                        (text == "Operasi:" and not is_quantity and not is_word) or
                        (text == "Hasil:" and not is_quantity and not is_word)
                    )

    def _open_asset_picker(self, pair_index):
        dialog = AssetPickerDialog(self, item_label="gambar")
        dialog.set_target(pair_index, len(self.pair_inputs))

        # target_index dibaca saat signal dikirim, sebelum picker maju ke pasangan berikutnya.
        dialog.asset_selected.connect(
            lambda asset_name, picker=dialog:
            self._set_asset(picker.target_index, asset_name)
        )
        dialog.exec()

    def _set_asset(self, pair_index, asset_name):
        if not 0 <= pair_index < len(self.pair_inputs):
            return

        button = self.pair_inputs[pair_index]["asset"]
        button.setProperty("asset_name", asset_name)
        path = OpenMojiAssetService.get_asset(asset_name, "color")
        renderer = QSvgRenderer(str(path))
        pixmap = QPixmap(48, 48)
        pixmap.fill(Qt.transparent)
        from PySide6.QtGui import QPainter
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        button.setIcon(QIcon(pixmap))
        button.setIconSize(pixmap.size())
        # Keep the editor button visual-only too; do not show the Unicode filename.
        button.setText("")
        button.setToolTip("Ilustrasi dipilih")

    def set_material_data(self, material_data):
        self.material_data = dict(material_data)
        self.material_info.setText(
            f"{material_data.get('title', 'Materi')} • "
            f"{material_data.get('category', 'Numerasi')} • "
            f"{material_data.get('age', '')} • "
            f"{material_data.get('activity_type', 'Matching Card')}"
        )

    def reset_form(self):
        self.material_data = {}
        self.mode_combo.setCurrentIndex(0)
        for index, row in enumerate(self.pair_inputs, start=1):
            row["number"].setValue(index)
            row["asset"].setProperty("asset_name", None)
            row["asset"].setIcon(QIcon())
            row["asset"].setText("Pilih ilustrasi")
            row["asset"].setToolTip("")
            row["word"].clear()
            row["question"].clear()
            row["answer"].clear()

    def _preview(self):
        mode = self.mode_combo.currentText()
        pairs = []
        for index, row in enumerate(self.pair_inputs, start=1):
            if mode == self.MODES[0]:
                asset = row["asset"].property("asset_name")
                if not asset:
                    QMessageBox.warning(self, "Data Belum Lengkap", f"Pilih ilustrasi untuk pasangan {index}.")
                    return
                number = row["number"].value()
                pairs.append({"number": number, "asset": asset, "quantity": number})
            elif mode == self.MODES[1]:
                word = row["word"].text().strip()
                if not word:
                    QMessageBox.warning(self, "Data Belum Lengkap", f"Isi nama bilangan untuk pasangan {index}.")
                    return
                pairs.append({"number": row["number"].value(), "word": word})
            else:
                question = row["question"].text().strip()
                answer = row["answer"].text().strip()
                if not question or not answer:
                    QMessageBox.warning(self, "Data Belum Lengkap", f"Isi operasi dan hasil untuk pasangan {index}.")
                    return
                pairs.append({"question": question, "answer": answer})

        self.preview_requested.emit({**self.material_data, "matching_mode": mode, "pairs": pairs})
