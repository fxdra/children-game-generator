from io import BytesIO
from pathlib import Path
import re

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF

from app.services.maze_renderer import MazeRenderer


class MazePDF:
    """
    Export Maze GameAnak menjadi PDF A4.

    Tugas class ini:
    - membuat maze SVG melalui MazeRenderer
    - menempatkan maze ke halaman A4
    - menambahkan judul
    - menambahkan instruksi
    - menambahkan garis nama
    - menyimpan PDF ke output/pdf

    Tidak menangani:
    - Maze generation
    - Asset Picker
    - PySide6
    """

    OUTPUT_DIR = (
        Path(__file__).resolve().parents[2]
        / "output"
        / "pdf"
    )

    DEFAULT_TITLE = "MAZE"

    DEFAULT_INSTRUCTION = (
        "Bantu karakter menemukan jalan menuju tujuan!"
    )

    @classmethod
    def export(
        cls,
        maze_generator,
        start_asset: str | None = None,
        finish_asset: str | None = None,
        title: str = DEFAULT_TITLE,
        instruction: str = DEFAULT_INSTRUCTION,
    ) -> Path:
        """
        Export maze menjadi PDF A4.

        Args:
            maze_generator:
                Instance MazeGenerator yang sudah di-generate.

            start_asset:
                Nama asset OpenMoji untuk START.

            finish_asset:
                Nama asset OpenMoji untuk FINISH.

            title:
                Judul worksheet.

            instruction:
                Instruksi untuk anak.

        Returns:
            Path file PDF yang berhasil dibuat.
        """

        cls.OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        renderer = MazeRenderer(
            maze_generator,
            start_asset=start_asset,
            finish_asset=finish_asset,
        )

        result = renderer.render()

        svg_data = result["svg_data"]

        drawing = svg2rlg(
            BytesIO(svg_data)
        )

        if drawing is None:
            raise RuntimeError(
                "SVG maze gagal dikonversi ke PDF."
            )

        page_width, page_height = A4

        filename = cls._build_filename(title)
        output_path = cls._get_unique_path(filename)

        pdf = canvas.Canvas(
            str(output_path),
            pagesize=A4,
        )

        # ==================================================
        # TITLE
        # ==================================================

        pdf.setFont(
            "Helvetica-Bold",
            22,
        )

        pdf.drawCentredString(
            page_width / 2,
            page_height - 30 * mm,
            title.upper(),
        )

        # ==================================================
        # INSTRUCTION
        # ==================================================

        pdf.setFont(
            "Helvetica",
            10,
        )

        pdf.drawCentredString(
            page_width / 2,
            page_height - 39 * mm,
            instruction,
        )

        # ==================================================
        # MAZE
        # ==================================================

        maze_area_left = 15 * mm
        maze_area_right = page_width - 15 * mm

        maze_area_top = page_height - 48 * mm
        maze_area_bottom = 27 * mm

        available_width = (
            maze_area_right - maze_area_left
        )

        available_height = (
            maze_area_top - maze_area_bottom
        )

        original_width = drawing.width
        original_height = drawing.height

        if original_width <= 0 or original_height <= 0:
            raise RuntimeError(
                "Ukuran drawing maze tidak valid."
            )

        scale_x = (
            available_width / original_width
        )

        scale_y = (
            available_height / original_height
        )

        scale = min(
            scale_x,
            scale_y,
        )

        draw_width = original_width * scale
        draw_height = original_height * scale

        draw_x = (
            page_width - draw_width
        ) / 2

        draw_y = (
            maze_area_bottom
            + (
                available_height
                - draw_height
            ) / 2
        )

        pdf.saveState()

        pdf.translate(
            draw_x,
            draw_y,
        )

        pdf.scale(
            scale,
            scale,
        )

        renderPDF.draw(
            drawing,
            pdf,
            0,
            0,
        )

        pdf.restoreState()

        # ==================================================
        # NAME
        # ==================================================

        name_y = 14 * mm

        pdf.setFont(
            "Helvetica",
            10,
        )

        pdf.drawString(
            20 * mm,
            name_y,
            "Nama:",
        )

        pdf.line(
            35 * mm,
            name_y - 1,
            page_width - 20 * mm,
            name_y - 1,
        )

        # ==================================================
        # SAVE
        # ==================================================

        pdf.save()

        return output_path

    @staticmethod
    def _build_filename(title: str) -> str:
        """
        Membuat nama file aman untuk Windows.
        """

        title = title.strip()

        if not title:
            title = MazePDF.DEFAULT_TITLE

        safe_title = re.sub(
            r'[<>:"/\\|?*]+',
            "-",
            title,
        )

        safe_title = re.sub(
            r"\s+",
            " ",
            safe_title,
        ).strip()

        if not safe_title:
            safe_title = MazePDF.DEFAULT_TITLE

        return f"{safe_title}.pdf"

    @classmethod
    def _get_unique_path(
        cls,
        filename: str,
    ) -> Path:
        """
        Jika file sudah ada, tambahkan (2), (3), dst.
        """

        path = cls.OUTPUT_DIR / filename

        if not path.exists():
            return path

        stem = path.stem
        suffix = path.suffix

        counter = 2

        while True:
            candidate = (
                cls.OUTPUT_DIR
                / f"{stem} ({counter}){suffix}"
            )

            if not candidate.exists():
                return candidate

            counter += 1