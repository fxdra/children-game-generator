from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.services.worksheet_pdf import WorksheetPDFService


class WorksheetCanvas(QWidget):
    """
    Canvas preview worksheet dengan rasio A4 Portrait.
    """

    def __init__(self, worksheet_data: dict):
        super().__init__()

        self.worksheet_data = worksheet_data

        # Rasio A4 Portrait
        self.setMinimumSize(500, 707)

        self.setAttribute(Qt.WA_StyledBackground, True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # =========================
        # CANVAS
        # =========================

        painter.fillRect(
            self.rect(),
            Qt.white,
        )

        width = self.width()
        height = self.height()

        # =========================
        # MARGIN
        # =========================

        margin_x = width * 0.08
        margin_top = height * 0.07

        content_width = width - (margin_x * 2)

        # =========================
        # TITLE
        # =========================

        title = self.worksheet_data.get(
            "activity_title",
            "Worksheet",
        )

        painter.setPen(Qt.black)

        title_font = QFont()
        title_font.setPointSize(
            max(14, int(width * 0.025))
        )
        title_font.setBold(True)

        painter.setFont(title_font)

        painter.drawText(
            int(margin_x),
            int(margin_top),
            int(content_width),
            45,
            Qt.AlignCenter,
            title,
        )

        # =========================
        # INSTRUCTION
        # =========================

        instruction = self.worksheet_data.get(
            "instruction",
            "Kerjakan aktivitas berikut.",
        )

        instruction_font = QFont()
        instruction_font.setPointSize(
            max(9, int(width * 0.017))
        )

        painter.setFont(instruction_font)

        painter.drawText(
            int(margin_x),
            int(margin_top + 65),
            int(content_width),
            50,
            Qt.AlignCenter,
            instruction,
        )

        # =========================
        # ACTIVITY
        # =========================

        worksheet_type = self.worksheet_data.get(
            "worksheet_type",
            "Menghitung",
        )

        if worksheet_type == "Menghitung":
            self._draw_counting_activity(
                painter,
                width,
                height,
            )

        else:
            self._draw_generic_activity(
                painter,
                width,
                height,
                worksheet_type,
            )

        # =========================
        # NAME
        # =========================

        name_y = height * 0.90

        name_font = QFont()
        name_font.setPointSize(
            max(9, int(width * 0.016))
        )

        painter.setFont(name_font)
        painter.setPen(Qt.black)

        painter.drawText(
            int(margin_x),
            int(name_y),
            70,
            30,
            Qt.AlignLeft,
            "Nama:",
        )

        painter.drawLine(
            int(margin_x + 65),
            int(name_y + 24),
            int(width - margin_x),
            int(name_y + 24),
        )

        painter.end()

    def _draw_counting_activity(
        self,
        painter: QPainter,
        width: int,
        height: int,
    ):
        # =========================
        # OBJECTS
        # =========================

        center_x = width / 2
        apple_y = height * 0.43

        apple_size = width * 0.075
        spacing = width * 0.055

        total_width = (
            (apple_size * 3)
            + (spacing * 2)
        )

        start_x = center_x - (total_width / 2)

        for index in range(3):
            x = (
                start_x
                + index * (apple_size + spacing)
            )

            self._draw_apple(
                painter,
                x,
                apple_y,
                apple_size,
            )

        # =========================
        # QUESTION
        # =========================

        question = self.worksheet_data.get(
            "question",
            "Ada berapa apel?",
        )

        question_font = QFont()
        question_font.setPointSize(
            max(10, int(width * 0.019))
        )
        question_font.setBold(True)

        painter.setFont(question_font)
        painter.setPen(Qt.black)

        painter.drawText(
            0,
            int(height * 0.55),
            width,
            40,
            Qt.AlignCenter,
            question,
        )

        # =========================
        # ANSWER OPTIONS
        # =========================

        option_y = height * 0.66

        options = ["2", "3", "4"]

        option_width = width * 0.16
        gap = width * 0.04

        total_options_width = (
            option_width * 3
            + gap * 2
        )

        start_x = (
            center_x
            - total_options_width / 2
        )

        option_font = QFont()
        option_font.setPointSize(
            max(10, int(width * 0.019))
        )
        option_font.setBold(True)

        painter.setFont(option_font)

        for index, option in enumerate(options):
            x = (
                start_x
                + index * (option_width + gap)
            )

            circle_size = width * 0.045

            painter.setPen(
                QPen(Qt.black, 2)
            )

            painter.drawEllipse(
                int(x),
                int(option_y),
                int(circle_size),
                int(circle_size),
            )

            painter.drawText(
                int(x + circle_size + 8),
                int(option_y),
                int(option_width),
                int(circle_size),
                Qt.AlignLeft | Qt.AlignVCenter,
                option,
            )

    def _draw_apple(
        self,
        painter: QPainter,
        x: float,
        y: float,
        size: float,
    ):
        # Body
        painter.setPen(
            QPen(Qt.black, 2)
        )

        painter.setBrush(Qt.white)

        painter.drawEllipse(
            int(x),
            int(y + size * 0.20),
            int(size * 0.55),
            int(size * 0.65),
        )

        painter.drawEllipse(
            int(x + size * 0.35),
            int(y + size * 0.20),
            int(size * 0.55),
            int(size * 0.65),
        )

        # Stem
        painter.drawLine(
            int(x + size * 0.52),
            int(y + size * 0.22),
            int(x + size * 0.58),
            int(y),
        )

        # Leaf
        painter.drawEllipse(
            int(x + size * 0.53),
            int(y),
            int(size * 0.30),
            int(size * 0.14),
        )

    def _draw_generic_activity(
        self,
        painter: QPainter,
        width: int,
        height: int,
        worksheet_type: str,
    ):
        painter.setPen(Qt.black)

        font = QFont()
        font.setPointSize(
            max(10, int(width * 0.018))
        )
        font.setBold(True)

        painter.setFont(font)

        painter.drawText(
            0,
            int(height * 0.48),
            width,
            40,
            Qt.AlignCenter,
            f"Preview {worksheet_type}",
        )


class WorksheetPreviewDialog(QDialog):

    def __init__(
        self,
        worksheet_data: dict,
        parent=None,
    ):
        super().__init__(parent)

        self.worksheet_data = worksheet_data

        self.setWindowTitle(
            "Preview Worksheet"
        )

        self.resize(900, 800)

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            20,
            20,
            20,
            20,
        )

        main_layout.setSpacing(16)

        # =========================
        # WORKSHEET
        # =========================

        self.canvas = WorksheetCanvas(
            self.worksheet_data
        )

        main_layout.addWidget(
            self.canvas,
            1,
            Qt.AlignCenter,
        )

        # =========================
        # FOOTER
        # =========================

        footer_layout = QHBoxLayout()

        footer_layout.addStretch()

        export_button = QPushButton(
            "Export PDF"
        )

        export_button.setObjectName(
            "primaryButton"
        )

        export_button.clicked.connect(
            self._export_pdf
        )

        footer_layout.addWidget(
            export_button
        )

        close_button = QPushButton(
            "Tutup"
        )

        close_button.setObjectName(
            "secondaryButton"
        )

        close_button.clicked.connect(
            self.close
        )

        footer_layout.addWidget(
            close_button
        )

        main_layout.addLayout(
            footer_layout
        )

    def _export_pdf(self):
        title = self.worksheet_data.get(
            "activity_title",
            "worksheet",
        )

        safe_title = "".join(
            char
            for char in title
            if char.isalnum()
            or char in (
                " ",
                "-",
                "_",
            )
        ).strip()

        if not safe_title:
            safe_title = "worksheet"

        default_path = (
            f"output/pdf/{safe_title}.pdf"
        )

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Simpan Worksheet PDF",
            default_path,
            "PDF Files (*.pdf)",
        )

        if not file_path:
            return

        try:
            WorksheetPDFService.generate(
                self.worksheet_data,
                file_path,
            )

            QMessageBox.information(
                self,
                "PDF Berhasil",
                (
                    "Worksheet berhasil dibuat.\n\n"
                    f"File:\n{file_path}"
                ),
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Gagal Membuat PDF",
                (
                    "Terjadi kesalahan saat "
                    "membuat PDF.\n\n"
                    f"{error}"
                ),
            )