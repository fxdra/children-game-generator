from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg

from app.services.openmoji_asset import OpenMojiAssetService


class WorksheetPDFService:

    @staticmethod
    def generate(
        worksheet_data: dict,
        output_path: str,
    ):
        output_file = Path(output_path)
        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        pdf = canvas.Canvas(
            str(output_file),
            pagesize=A4,
        )

        page_width, page_height = A4

        # =========================
        # MARGIN
        # =========================

        margin = 20 * mm

        # =========================
        # TITLE
        # =========================

        title = worksheet_data.get(
            "activity_title",
            "Worksheet",
        )

        pdf.setFont(
            "Helvetica-Bold",
            18,
        )

        pdf.drawCentredString(
            page_width / 2,
            page_height - 35 * mm,
            title,
        )

        # =========================
        # INSTRUCTION
        # =========================

        instruction = worksheet_data.get(
            "instruction",
            "Kerjakan aktivitas berikut.",
        )

        pdf.setFont(
            "Helvetica",
            11,
        )

        pdf.drawCentredString(
            page_width / 2,
            page_height - 48 * mm,
            instruction,
        )

        # =========================
        # ACTIVITY
        # =========================

        worksheet_type = worksheet_data.get(
            "worksheet_type",
            "Menghitung",
        )

        if worksheet_type == "Menghitung":
            WorksheetPDFService._draw_counting(
                pdf,
                worksheet_data,
                page_width,
                page_height,
            )

        else:
            pdf.setFont(
                "Helvetica-Bold",
                14,
            )

            pdf.drawCentredString(
                page_width / 2,
                page_height / 2,
                f"Preview {worksheet_type}",
            )

        # =========================
        # NAME
        # =========================

        name_y = 30 * mm

        pdf.setFont(
            "Helvetica",
            10,
        )

        pdf.drawString(
            margin,
            name_y,
            "Nama:",
        )

        pdf.line(
            margin + 18 * mm,
            name_y,
            page_width - margin,
            name_y,
        )

        pdf.showPage()
        pdf.save()

    @staticmethod
    def _draw_counting(
        pdf,
        worksheet_data,
        page_width,
        page_height,
    ):
        # =========================
        # NUMBER OF OBJECTS
        # =========================

        try:
            correct_answer = int(
                worksheet_data.get(
                    "answer",
                    "3",
                )
            )
        except (TypeError, ValueError):
            correct_answer = 3

        # Batasi untuk template pertama.
        object_count = max(
            1,
            min(correct_answer, 10),
        )

        # =========================
        # OBJECTS
        # =========================

        center_x = page_width / 2
        object_y = page_height - 115 * mm

        object_size = 16 * mm
        spacing = 8 * mm

        total_width = (
            object_count * object_size
            + (object_count - 1) * spacing
        )

        start_x = (
            center_x
            - total_width / 2
        )

        for index in range(object_count):
            x = (
                start_x
                + index
                * (object_size + spacing)
            )

            WorksheetPDFService._draw_openmoji(
                pdf,
                x,
                object_y,
                object_size,
            )

        # =========================
        # QUESTION
        # =========================

        question = worksheet_data.get(
            "question",
            "Ada berapa apel?",
        )

        pdf.setFont(
            "Helvetica-Bold",
            13,
        )

        pdf.drawCentredString(
            center_x,
            page_height - 160 * mm,
            question,
        )

        # =========================
        # ANSWER OPTIONS
        # =========================

        options = WorksheetPDFService._build_options(
            correct_answer
        )

        option_y = page_height - 195 * mm

        option_width = 35 * mm
        gap = 15 * mm

        total_width = (
            len(options) * option_width
            + (len(options) - 1) * gap
        )

        start_x = (
            center_x
            - total_width / 2
        )

        pdf.setFont(
            "Helvetica-Bold",
            12,
        )

        for index, option in enumerate(options):
            x = (
                start_x
                + index
                * (option_width + gap)
            )

            circle_x = x
            circle_y = option_y

            pdf.setLineWidth(1.5)

            pdf.circle(
                circle_x,
                circle_y,
                5 * mm,
            )

            pdf.drawString(
                circle_x + 9 * mm,
                circle_y - 3.5 * mm,
                str(option),
            )

    @staticmethod
    def _build_options(
        correct_answer: int,
    ):
        """
        Membuat pilihan jawaban sederhana
        berdasarkan jawaban benar.
        """

        options = [
            correct_answer - 1,
            correct_answer,
            correct_answer + 1,
        ]

        # Pastikan tidak ada angka <= 0.
        options = [
            max(1, value)
            for value in options
        ]

        # Hilangkan duplikat.
        result = []

        for value in options:
            if value not in result:
                result.append(value)

        return result

    @staticmethod
    def _draw_openmoji(
        pdf,
        x,
        y,
        size,
    ):
        svg_path = OpenMojiAssetService.get_asset(
            "apple",
            "color",
        )

        drawing = svg2rlg(
            str(svg_path)
        )

        if drawing is None:
            raise ValueError(
                "Gagal membaca SVG OpenMoji."
            )

        if drawing.width <= 0 or drawing.height <= 0:
            raise ValueError(
                "Ukuran SVG OpenMoji tidak valid."
            )

        # Pertahankan rasio asli SVG
        scale = min(
            size / drawing.width,
            size / drawing.height,
        )

        pdf.saveState()

        pdf.translate(
            x,
            y,
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