import math

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QPainterPath,
    QPen,
)
from PySide6.QtSvg import QSvgRenderer
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
from app.services.openmoji_asset import OpenMojiAssetService


class WorksheetCanvas(QWidget):
    """Canvas preview worksheet dengan rasio A4 Portrait."""

    def __init__(self, worksheet_data: dict):
        super().__init__()
        self.worksheet_data = worksheet_data
        self.setMinimumSize(500, 707)
        self.setAttribute(Qt.WA_StyledBackground, True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), Qt.white)

        width = self.width()
        height = self.height()
        margin_x = width * 0.08
        margin_top = height * 0.07
        content_width = width - (margin_x * 2)

        title = self.worksheet_data.get("activity_title", "Worksheet")
        painter.setPen(Qt.black)

        title_font = QFont()
        title_font.setPointSize(max(14, int(width * 0.025)))
        title_font.setBold(True)
        painter.setFont(title_font)
        painter.drawText(
            int(margin_x), int(margin_top), int(content_width), 45,
            Qt.AlignCenter, title,
        )

        instruction = self.worksheet_data.get(
            "instruction", "Kerjakan aktivitas berikut."
        )
        instruction_font = QFont()
        instruction_font.setPointSize(max(9, int(width * 0.017)))
        painter.setFont(instruction_font)
        painter.drawText(
            int(margin_x), int(margin_top + 65),
            int(content_width), 55,
            Qt.AlignCenter | Qt.TextWordWrap, instruction,
        )

        worksheet_type = self.worksheet_data.get("worksheet_type", "Menghitung")
        if worksheet_type == "Menghitung":
            self._draw_counting_activity(painter, width, height)
        elif worksheet_type == "Memilih Jawaban":
            self._draw_choice_activity(painter, width, height)
        elif worksheet_type == "Menulis / Tracing":
            self._draw_tracing_activity(painter, width, height)
        else:
            self._draw_generic_activity(painter, width, height, worksheet_type)

        name_y = height * 0.90
        name_font = QFont()
        name_font.setPointSize(max(9, int(width * 0.016)))
        painter.setFont(name_font)
        painter.setPen(Qt.black)
        painter.drawText(
            int(margin_x), int(name_y), 70, 30, Qt.AlignLeft, "Nama:"
        )
        painter.drawLine(
            int(margin_x + 65), int(name_y + 24),
            int(width - margin_x), int(name_y + 24),
        )
        painter.end()

    def _draw_counting_activity(self, painter, width, height):
        center_x = width / 2
        apple_y = height * 0.39
        apple_size = width * 0.075
        spacing = width * 0.055

        try:
            correct_answer = int(self.worksheet_data.get("answer", "3"))
        except (TypeError, ValueError):
            correct_answer = 3
        object_count = max(1, correct_answer)

        apple_path = OpenMojiAssetService.get_asset("apple", "color")
        renderer = QSvgRenderer(str(apple_path))

        if object_count <= 6:
            total_width = apple_size * object_count + spacing * (object_count - 1)
            start_x = center_x - total_width / 2

            positions = [
                (start_x + index * (apple_size + spacing), apple_y)
                for index in range(object_count)
            ]

        else:
            # Grid otomatis untuk jumlah apel di atas 6.
            area_left = width * 0.10
            area_top = height * 0.27
            area_width = width * 0.80
            area_height = height * 0.25

            columns = max(
                1,
                math.ceil(math.sqrt(object_count * area_width / area_height))
            )
            rows = math.ceil(object_count / columns)

            cell_width = area_width / columns
            cell_height = area_height / rows

            apple_size = min(
                cell_width * 0.72,
                cell_height * 0.72
            )

            positions = []

            for index in range(object_count):
                column = index % columns
                row = index // columns

                x = area_left + column * cell_width + (cell_width - apple_size) / 2
                y = area_top + row * cell_height + (cell_height - apple_size) / 2

                positions.append((x, y))

        for x, y in positions:
            renderer.render(painter, QRectF(x, y, apple_size, apple_size))

        question_y = 0.56
        options_y = 0.67
        self._draw_question(painter, width, height, y_ratio=question_y)
        options = self._build_counting_options(correct_answer)
        self._draw_options(painter, width, height, options, y_ratio=options_y)

    def _draw_choice_activity(self, painter, width, height):
        self._draw_question(painter, width, height, y_ratio=0.43)
        options = self.worksheet_data.get("options", [])
        self._draw_options(painter, width, height, options, y_ratio=0.57)

    def _draw_tracing_activity(self, painter, width, height):
        self._draw_question(painter, width, height, y_ratio=0.39)

        target = str(self.worksheet_data.get("tracing_text", "1 2 3")).strip()
        if not target:
            target = "1 2 3"

        font = QFont("Arial", max(52, int(width * 0.16)))
        font.setBold(True)
        painter.setFont(font)
        metrics = painter.fontMetrics()
        text_width = metrics.horizontalAdvance(target)
        # Keep long sequences within the printable canvas.
        while text_width > width * 0.78 and font.pointSize() > 28:
            font.setPointSize(font.pointSize() - 2)
            painter.setFont(font)
            metrics = painter.fontMetrics()
            text_width = metrics.horizontalAdvance(target)

        painter.setFont(font)
        path = QPainterPath()
        baseline_y = height * 0.66
        path.addText(
            (width - text_width) / 2,
            baseline_y,
            font,
            target,
        )

        dotted_pen = QPen(
            QColor("#8995A5"),
            max(1.5, width * 0.004),
            Qt.DotLine,
            Qt.RoundCap,
            Qt.RoundJoin,
        )
        painter.setPen(dotted_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

        guide_y = height * 0.70
        painter.setPen(QPen(QColor("#B8C0CC"), 1, Qt.DashLine))
        painter.drawLine(int(width * 0.14), int(guide_y), int(width * 0.86), int(guide_y))

        hint_font = QFont()
        hint_font.setPointSize(max(9, int(width * 0.015)))
        painter.setFont(hint_font)
        painter.setPen(QColor("#667085"))
        painter.drawText(
            0, int(height * 0.77), width, 30,
            Qt.AlignCenter, "Telusuri angka mengikuti garis titik-titik.",
        )

    def _draw_question(self, painter, width, height, y_ratio):
        question = self.worksheet_data.get("question", "")
        question_font = QFont()
        question_font.setPointSize(max(10, int(width * 0.019)))
        question_font.setBold(True)
        painter.setFont(question_font)
        painter.setPen(Qt.black)
        painter.drawText(
            int(width * 0.08), int(height * y_ratio),
            int(width * 0.84), 70,
            Qt.AlignCenter | Qt.TextWordWrap, question,
        )

    def _draw_options(self, painter, width, height, options, y_ratio):
        if not options:
            return

        center_x = width / 2
        option_y = height * y_ratio
        count = len(options)
        option_width = min(width * 0.19, width * 0.72 / count)
        gap = width * 0.035
        total_width = option_width * count + gap * (count - 1)
        start_x = center_x - total_width / 2

        option_font = QFont()
        option_font.setPointSize(max(10, int(width * 0.019)))
        option_font.setBold(True)
        painter.setFont(option_font)

        for index, option in enumerate(options):
            x = start_x + index * (option_width + gap)
            circle_size = width * 0.045
            painter.setPen(QPen(Qt.black, 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(
                int(x), int(option_y), int(circle_size), int(circle_size)
            )
            painter.drawText(
                int(x + circle_size + 8), int(option_y),
                int(option_width), int(circle_size),
                Qt.AlignLeft | Qt.AlignVCenter, str(option),
            )

    @staticmethod
    def _build_counting_options(correct_answer):
        candidates = [correct_answer - 1, correct_answer, correct_answer + 1]
        result = []
        for value in candidates:
            value = max(1, value)
            if value not in result:
                result.append(value)
        return result

    def _draw_generic_activity(self, painter, width, height, worksheet_type):
        painter.setPen(Qt.black)
        font = QFont()
        font.setPointSize(max(10, int(width * 0.018)))
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(
            0, int(height * 0.48), width, 40,
            Qt.AlignCenter, f"Preview {worksheet_type}",
        )


class WorksheetPreviewDialog(QDialog):
    def __init__(self, worksheet_data: dict, parent=None):
        super().__init__(parent)
        self.worksheet_data = worksheet_data
        self.setWindowTitle("Preview Worksheet")
        self.resize(900, 800)
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        self.canvas = WorksheetCanvas(self.worksheet_data)
        main_layout.addWidget(self.canvas, 1, Qt.AlignCenter)

        footer_layout = QHBoxLayout()
        footer_layout.addStretch()

        export_button = QPushButton("Export PDF")
        export_button.setObjectName("primaryButton")
        export_button.clicked.connect(self._export_pdf)
        footer_layout.addWidget(export_button)

        close_button = QPushButton("Tutup")
        close_button.setObjectName("secondaryButton")
        close_button.clicked.connect(self.close)
        footer_layout.addWidget(close_button)

        main_layout.addLayout(footer_layout)

    def _export_pdf(self):
        title = self.worksheet_data.get("activity_title", "worksheet")
        safe_title = "".join(
            char for char in title if char.isalnum() or char in (" ", "-", "_")
        ).strip() or "worksheet"
        default_path = f"output/pdf/{safe_title}.pdf"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Simpan Worksheet PDF",
            default_path,
            "PDF Files (*.pdf)",
        )
        if not file_path:
            return

        try:
            WorksheetPDFService.generate(self.worksheet_data, file_path)
            QMessageBox.information(
                self, "Berhasil",
                f"Worksheet berhasil disimpan:\n{file_path}",
            )
        except Exception as error:
            QMessageBox.critical(
                self, "Gagal Export PDF",
                f"Terjadi kesalahan saat membuat PDF:\n{error}",
            )
