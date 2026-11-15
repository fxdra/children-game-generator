import math

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg

from app.services.openmoji_asset import OpenMojiAssetService


class WorksheetPDFService:
    @staticmethod
    def generate(worksheet_data: dict, output_path: str):
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        pdf = canvas.Canvas(str(output_file), pagesize=A4)
        page_width, page_height = A4
        margin = 20 * mm

        title = worksheet_data.get("activity_title", "Worksheet")
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawCentredString(page_width / 2, page_height - 35 * mm, title)

        instruction = worksheet_data.get(
            "instruction", "Kerjakan aktivitas berikut."
        )
        pdf.setFont("Helvetica", 11)
        WorksheetPDFService._draw_centered_wrapped(
            pdf, instruction, page_width / 2, page_height - 48 * mm,
            page_width - (2 * margin), 14,
        )

        worksheet_type = worksheet_data.get("worksheet_type", "Menghitung")
        if worksheet_type == "Menghitung":
            WorksheetPDFService._draw_counting(
                pdf, worksheet_data, page_width, page_height
            )
        elif worksheet_type == "Memilih Jawaban":
            WorksheetPDFService._draw_choice(
                pdf, worksheet_data, page_width, page_height
            )
        elif worksheet_type == "Menulis / Tracing":
            WorksheetPDFService._draw_tracing(
                pdf, worksheet_data, page_width, page_height
            )
        else:
            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawCentredString(
                page_width / 2, page_height / 2, f"Preview {worksheet_type}"
            )

        name_y = 30 * mm
        pdf.setFont("Helvetica", 10)
        pdf.drawString(margin, name_y, "Nama:")
        pdf.line(margin + 18 * mm, name_y, page_width - margin, name_y)
        pdf.showPage()
        pdf.save()

    @staticmethod
    def _draw_counting(pdf, worksheet_data, page_width, page_height):
        try:
            correct_answer = int(worksheet_data.get("answer", "3"))
        except (TypeError, ValueError):
            correct_answer = 3
        object_count = max(1, correct_answer)

        center_x = page_width / 2
        object_size = 16 * mm
        spacing = 8 * mm

        if object_count <= 6:
            object_y = page_height - 115 * mm
            total_width = object_count * object_size + (object_count - 1) * spacing
            start_x = center_x - total_width / 2

            positions = [
                (start_x + index * (object_size + spacing), object_y)
                for index in range(object_count)
            ]

            question_y = page_height - 160 * mm
            options_y = page_height - 195 * mm

        else:
            # Grid otomatis agar seluruh apel berada di area cetak.
            area_width = 160 * mm
            area_height = 60 * mm
            area_left = center_x - area_width / 2
            area_top = page_height - 75 * mm

            columns = max(
                1,
                math.ceil(math.sqrt(object_count * area_width / area_height))
            )
            rows = math.ceil(object_count / columns)

            cell_width = area_width / columns
            cell_height = area_height / rows

            object_size = min(
                16 * mm,
                cell_width * 0.72,
                cell_height * 0.72
            )

            positions = []

            for index in range(object_count):
                column = index % columns
                row = index // columns

                x = area_left + column * cell_width + (cell_width - object_size) / 2
                y = area_top - (row + 1) * cell_height + (cell_height - object_size) / 2

                positions.append((x, y))

            question_y = page_height - 160 * mm
            options_y = page_height - 185 * mm

        for x, y in positions:
            WorksheetPDFService._draw_openmoji(pdf, x, y, object_size)

        question = worksheet_data.get("question", "Ada berapa apel?")
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawCentredString(center_x, question_y, question)

        options = WorksheetPDFService._build_options(correct_answer)
        WorksheetPDFService._draw_choice_options(
            pdf, options, center_x, options_y
        )

    @staticmethod
    def _draw_choice(pdf, worksheet_data, page_width, page_height):
        question = worksheet_data.get("question", "")
        pdf.setFont("Helvetica-Bold", 15)
        WorksheetPDFService._draw_centered_wrapped(
            pdf, question, page_width / 2, page_height - 105 * mm,
            page_width - 2 * 25 * mm, 20,
        )

        options = worksheet_data.get("options") or []
        WorksheetPDFService._draw_choice_options(
            pdf, options, page_width / 2, page_height - 155 * mm
        )

    @staticmethod
    def _draw_choice_options(pdf, options, center_x, y):
        if not options:
            return

        count = len(options)
        option_width = 35 * mm
        gap = 12 * mm
        total_width = count * option_width + (count - 1) * gap
        start_x = center_x - total_width / 2

        pdf.setFont("Helvetica-Bold", 12)
        for index, option in enumerate(options):
            x = start_x + index * (option_width + gap)
            circle_x = x + 5 * mm
            pdf.setLineWidth(1.5)
            pdf.circle(circle_x, y, 5 * mm)
            pdf.drawString(circle_x + 9 * mm, y - 3.5 * mm, str(option))

    @staticmethod
    def _draw_tracing(pdf, worksheet_data, page_width, page_height):
        question = worksheet_data.get("question", "Telusuri angka berikut.")
        pdf.setFont("Helvetica-Bold", 14)
        WorksheetPDFService._draw_centered_wrapped(
            pdf, question, page_width / 2, page_height - 105 * mm,
            page_width - 2 * 25 * mm, 18,
        )

        target = str(worksheet_data.get("tracing_text", "1 2 3")).strip() or "1 2 3"
        font_size = 76
        max_width = page_width * 0.78
        while font_size > 30 and pdf.stringWidth(
            target, "Helvetica-Bold", font_size
        ) > max_width:
            font_size -= 2

        text = pdf.beginText()
        text.setTextOrigin(
            (page_width - pdf.stringWidth(target, "Helvetica-Bold", font_size)) / 2,
            page_height - 155 * mm,
        )
        text.setFont("Helvetica-Bold", font_size)
        text.setStrokeColor(colors.HexColor("#8995A5"))
        text.setFillColor(colors.white)
        text.setTextRenderMode(1)  # outline only
        pdf.saveState()
        pdf.setDash(1.5, 2.5)
        pdf.drawText(text)
        pdf.restoreState()

        guide_y = page_height - 165 * mm
        pdf.setStrokeColor(colors.HexColor("#B8C0CC"))
        pdf.setDash(2, 3)
        pdf.line(25 * mm, guide_y, page_width - 25 * mm, guide_y)
        pdf.setDash()
        pdf.setFillColor(colors.HexColor("#667085"))
        pdf.setFont("Helvetica", 10)
        pdf.drawCentredString(
            page_width / 2, page_height - 180 * mm,
            "Telusuri angka mengikuti garis panduan.",
        )

    @staticmethod
    def _draw_centered_wrapped(pdf, text, center_x, top_y, max_width, leading):
        words = str(text).split()
        if not words:
            return
        lines = []
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if current and pdf.stringWidth(candidate, pdf._fontname, pdf._fontsize) > max_width:
                lines.append(current)
                current = word
            else:
                current = candidate
        if current:
            lines.append(current)

        for index, line in enumerate(lines):
            pdf.drawCentredString(center_x, top_y - index * leading, line)

    @staticmethod
    def _build_options(correct_answer: int):
        candidates = [correct_answer - 1, correct_answer, correct_answer + 1]
        result = []
        for value in candidates:
            value = max(1, value)
            if value not in result:
                result.append(value)
        return result

    @staticmethod
    def _draw_openmoji(pdf, x, y, size):
        svg_path = OpenMojiAssetService.get_asset("apple", "color")
        drawing = svg2rlg(str(svg_path))
        if drawing is None:
            raise ValueError("Gagal membaca SVG OpenMoji.")
        if drawing.width <= 0 or drawing.height <= 0:
            raise ValueError("Ukuran SVG OpenMoji tidak valid.")

        scale = min(size / drawing.width, size / drawing.height)
        pdf.saveState()
        pdf.translate(x, y)
        pdf.scale(scale, scale)
        renderPDF.draw(drawing, pdf, 0, 0)
        pdf.restoreState()
