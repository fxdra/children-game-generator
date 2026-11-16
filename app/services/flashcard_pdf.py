from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QMarginsF, QRectF
from PySide6.QtGui import QPageLayout, QPageSize, QPainter
from PySide6.QtGui import QPdfWriter

from app.services.flashcard_renderer import NumberCardRenderer
from app.services.flashcard_service import NumberCardService


class NumberCardPDFService:
    """Ekspor Kartu Pintar Angka ke PDF menggunakan renderer preview yang sama."""

    @classmethod
    def export(
        cls,
        output_path: str | Path,
        start_number: int = NumberCardService.MIN_NUMBER,
        end_number: int = NumberCardService.MAX_NUMBER,
        title: str = NumberCardRenderer.DEFAULT_TITLE,
    ) -> Path:
        """Buat PDF A4 portrait dan kembalikan path file hasil ekspor."""
        pages = NumberCardService.create_pages(
            start_number=start_number,
            end_number=end_number,
        )

        output_file = Path(output_path).expanduser()
        if output_file.suffix.lower() != ".pdf":
            output_file = output_file.with_suffix(".pdf")

        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Gunakan 96 DPI agar ukuran koordinat dan font QPainter sejalan
        # dengan preview QWidget pada logical DPI desktop yang umum.
        writer = QPdfWriter(str(output_file))
        writer.setResolution(96)
        writer.setPageLayout(
            QPageLayout(
                QPageSize(QPageSize.A4),
                QPageLayout.Portrait,
                QMarginsF(0, 0, 0, 0),
                QPageLayout.Millimeter,
            )
        )

        painter = QPainter()
        if not painter.begin(writer):
            raise RuntimeError(
                f"Tidak dapat memulai proses pembuatan PDF: {output_file}"
            )

        try:
            page_rect = QRectF(
                0,
                0,
                writer.width(),
                writer.height(),
            )

            for page_index, cards in enumerate(pages):
                if page_index > 0 and not writer.newPage():
                    raise RuntimeError(
                        f"Gagal membuat halaman PDF ke-{page_index + 1}."
                    )

                NumberCardRenderer.draw_page(
                    painter=painter,
                    page_rect=page_rect,
                    cards=cards,
                    title=title,
                )
        finally:
            painter.end()

        if not output_file.exists() or output_file.stat().st_size == 0:
            raise RuntimeError(
                f"File PDF tidak berhasil dibuat: {output_file}"
            )

        return output_file