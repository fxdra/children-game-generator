"""PDF export for Meat Fighter-backed Number Path worksheets."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
import re

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg

from app.services.number_path_renderer import NumberPathRenderer


class NumberPathPDF:
    OUTPUT_DIR = Path(__file__).resolve().parents[2] / "output" / "pdf"

    @classmethod
    def export(
        cls,
        maze,
        title: str = "Number Path",
        instruction: str | None = None,
        difficulty: str = "Mudah",
        start_asset: str | None = None,
        finish_asset: str | None = None,
    ) -> Path:
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        svg_data = NumberPathRenderer(
            maze,
            difficulty=difficulty,
            start_asset=start_asset,
            finish_asset=finish_asset,
        ).render(title, instruction)
        drawing = svg2rlg(BytesIO(svg_data))
        if drawing is None:
            raise RuntimeError("SVG Number Path gagal dikonversi ke PDF.")

        page_width, page_height = A4
        safe = re.sub(r'[<>:"/\\|?*]+', "-", (title or "Number Path").strip()) or "Number Path"
        output = cls.OUTPUT_DIR / f"{safe} - Number Path.pdf"
        counter = 2
        while output.exists():
            output = cls.OUTPUT_DIR / f"{safe} - Number Path ({counter}).pdf"
            counter += 1

        pdf = canvas.Canvas(str(output), pagesize=A4)
        max_w, max_h = page_width - 24 * mm, page_height - 58 * mm
        scale = min(max_w / drawing.width, max_h / drawing.height)
        pdf.saveState()
        pdf.translate(
            (page_width - drawing.width * scale) / 2,
            (page_height - drawing.height * scale) / 2 - 3 * mm,
        )
        pdf.scale(scale, scale)
        renderPDF.draw(drawing, pdf, 0, 0)
        pdf.restoreState()
        pdf.setFont("Helvetica", 9)
        pdf.drawString(18 * mm, 12 * mm, "Nama:")
        pdf.line(32 * mm, 11.5 * mm, page_width - 18 * mm, 11.5 * mm)
        pdf.save()
        return output
