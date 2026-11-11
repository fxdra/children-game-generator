from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import (
    QFont,
    QImageReader,
    QPainter,
    QPen,
    QPixmap,
)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.services.tracing_pdf import TracingPDF


class TracingCanvas(QWidget):
    """
    Preview Tracing dengan rasio kertas A4 Portrait.
    """

    def __init__(self, tracing_data: dict):
        super().__init__()

        self.tracing_data = tracing_data

        self.setMinimumSize(500, 707)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self.svg_renderer = None
        self.image_pixmap = None

        self._load_image()

    def _load_image(self):
        tracing_asset = self.tracing_data.get(
            "tracing_asset"
        )

        if not tracing_asset:
            raise ValueError(
                "Asset Tracing belum dipilih."
            )

        image_path = tracing_asset["path"]
        suffix = image_path.suffix.lower()

        if suffix == ".svg":
            self.svg_renderer = QSvgRenderer(
                str(image_path)
            )

            if not self.svg_renderer.isValid():
                raise ValueError(
                    "Gagal membaca gambar SVG."
                )

        else:
            reader = QImageReader(
                str(image_path)
            )
            reader.setAutoTransform(True)

            self.image_pixmap = QPixmap.fromImage(
                reader.read()
            )

            if self.image_pixmap.isNull():
                raise ValueError(
                    "Gagal membaca gambar Tracing."
                )

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )
        painter.setRenderHint(
            QPainter.RenderHint.SmoothPixmapTransform
        )

        # RASIO A4 PORTRAIT
        page_width = 595.28
        page_height = 841.89

        scale = min(
            self.width() / page_width,
            self.height() / page_height,
        )

        rendered_width = page_width * scale
        rendered_height = page_height * scale

        page_x = (
            self.width() - rendered_width
        ) / 2

        page_y = (
            self.height() - rendered_height
        ) / 2

        page_rect = QRectF(
            page_x,
            page_y,
            rendered_width,
            rendered_height,
        )

        # WHITE PAPER
        painter.fillRect(
            page_rect,
            Qt.GlobalColor.white,
        )

        # PAGE BORDER
        painter.setPen(
            QPen(Qt.GlobalColor.lightGray, 1)
        )
        painter.drawRect(page_rect)

        # TITLE
        title = self.tracing_data.get(
            "title",
            "Tracing",
        )

        painter.setPen(Qt.GlobalColor.black)

        title_font = QFont()
        title_font.setPointSize(
            max(10, int(18 * scale))
        )
        title_font.setBold(True)

        painter.setFont(title_font)

        margin = 20 * scale

        painter.drawText(
            QRectF(
                page_x + margin,
                page_y + 22 * scale,
                rendered_width - 2 * margin,
                30 * scale,
            ),
            Qt.AlignmentFlag.AlignCenter,
            title,
        )

        # INSTRUCTION
        instruction = self.tracing_data.get(
            "instruction",
            TracingPDF.DEFAULT_INSTRUCTION,
        )

        instruction_font = QFont()
        instruction_font.setPointSize(
            max(8, int(11 * scale))
        )

        painter.setFont(instruction_font)

        painter.drawText(
            QRectF(
                page_x + margin,
                page_y + 48 * scale,
                rendered_width - 2 * margin,
                25 * scale,
            ),
            Qt.AlignmentFlag.AlignCenter,
            instruction,
        )

        # TRACING IMAGE AREA
        image_area = QRectF(
            page_x + margin,
            page_y + 55 * scale,
            rendered_width - 2 * margin,
            rendered_height - 100 * scale,
        )

        self._draw_tracing_image(
            painter,
            image_area,
        )

        # NAME FIELD
        name_y = page_y + rendered_height - 25 * scale

        name_font = QFont()
        name_font.setPointSize(
            max(8, int(10 * scale))
        )

        painter.setFont(name_font)
        painter.setPen(Qt.GlobalColor.black)

        painter.drawText(
            int(page_x + margin),
            int(name_y),
            "Nama:",
        )

        painter.drawLine(
            int(page_x + margin + 18 * scale),
            int(name_y),
            int(page_x + rendered_width - margin),
            int(name_y),
        )

        painter.end()

    def _draw_tracing_image(
        self,
        painter: QPainter,
        target_rect: QRectF,
    ):
        if self.svg_renderer:
            self.svg_renderer.render(
                painter,
                target_rect,
            )
            return

        if self.image_pixmap:
            image_size = self.image_pixmap.size()

            scaled_size = image_size.scaled(
                int(target_rect.width()),
                int(target_rect.height()),
                Qt.AspectRatioMode.KeepAspectRatio,
            )

            image_x = (
                target_rect.center().x()
                - scaled_size.width() / 2
            )

            image_y = (
                target_rect.center().y()
                - scaled_size.height() / 2
            )

            image_rect = QRectF(
                image_x,
                image_y,
                scaled_size.width(),
                scaled_size.height(),
            )

            painter.drawPixmap(
                image_rect,
                self.image_pixmap,
                QRectF(self.image_pixmap.rect()),
            )


class TracingPreviewDialog(QDialog):

    def __init__(
        self,
        tracing_data: dict,
        parent=None,
    ):
        super().__init__(parent)

        self.tracing_data = tracing_data

        self.setWindowTitle(
            "Preview Tracing"
        )

        self.resize(900, 900)

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

        # TRACING CANVAS
        self.canvas = TracingCanvas(
            self.tracing_data
        )

        main_layout.addWidget(
            self.canvas,
            1,
        )

        # FOOTER
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
        title = self.tracing_data.get(
            "title",
            "Tracing",
        )

        safe_title = "".join(
            char
            for char in title
            if char.isalnum()
            or char in (" ", "-", "_")
        ).strip()

        if not safe_title:
            safe_title = "tracing"

        default_path = (
            f"output/pdf/{safe_title}.pdf"
        )

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Simpan Tracing PDF",
            default_path,
            "PDF Files (*.pdf)",
        )

        if not file_path:
            return

        if not file_path.lower().endswith(".pdf"):
            file_path += ".pdf"

        try:
            output_path = TracingPDF.generate(
                self.tracing_data,
                file_path,
            )

            QMessageBox.information(
                self,
                "PDF Berhasil",
                (
                    "Tracing berhasil diekspor.\n\n"
                    f"File:\n{output_path}"
                ),
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Gagal Membuat PDF",
                (
                    "Terjadi kesalahan saat "
                    "membuat PDF Tracing.\n\n"
                    f"{error}"
                ),
            )
