"""PDF export for Numerasi Maze worksheets."""
from io import BytesIO
from pathlib import Path
import re

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF

from app.services.numerasi_maze_renderer import NumerasiMazeRenderer


class NumerasiMazePDF:
    OUTPUT_DIR = Path(__file__).resolve().parents[2] / "output" / "pdf"

    @classmethod
    def export(
        cls,
        puzzle,
        title: str,
        instruction: str | None = None,
        character_asset: str | None = None,
    ) -> Path:
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        drawing = svg2rlg(BytesIO(
            NumerasiMazeRenderer(puzzle, character_asset=character_asset).render(title, instruction)
        ))
        if drawing is None:
            raise RuntimeError("SVG Numerasi Maze gagal dikonversi ke PDF.")
        page_width, page_height = A4
        safe = re.sub(r'[<>:"/\\|?*]+', '-', (title or "Numerasi Maze").strip()) or "Numerasi Maze"
        output = cls.OUTPUT_DIR / f"{safe} - {puzzle.subtype}.pdf"
        counter = 2
        while output.exists():
            output = cls.OUTPUT_DIR / f"{safe} - {puzzle.subtype} ({counter}).pdf"
            counter += 1
        pdf = canvas.Canvas(str(output), pagesize=A4)
        max_w, max_h = page_width - 24 * mm, page_height - 58 * mm
        scale = min(max_w / drawing.width, max_h / drawing.height)
        pdf.saveState()
        pdf.translate((page_width - drawing.width * scale) / 2, (page_height - drawing.height * scale) / 2 - 3 * mm)
        pdf.scale(scale, scale)
        renderPDF.draw(drawing, pdf, 0, 0)
        pdf.restoreState()
        pdf.setFont("Helvetica", 9)
        pdf.drawString(18 * mm, 12 * mm, "Nama:")
        pdf.line(32 * mm, 11.5 * mm, page_width - 18 * mm, 11.5 * mm)
        pdf.save()
        return output
