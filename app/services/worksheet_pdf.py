from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm


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

            WorksheetPDFService._draw_apple(
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
    def _draw_apple(
        pdf,
        x,
        y,
        size,
    ):
        pdf.setLineWidth(1.2)

        # =========================
        # APPLE BODY
        # =========================

        radius = size * 0.28

        pdf.circle(
            x + size * 0.32,
            y + size * 0.30,
            radius,
        )

        pdf.circle(
            x + size * 0.68,
            y + size * 0.30,
            radius,
        )

        # =========================
        # STEM
        # =========================

        pdf.line(
            x + size * 0.50,
            y + size * 0.55,
            x + size * 0.55,
            y + size * 0.85,
        )

        # =========================
        # LEAF
        # =========================

        pdf.ellipse(
            x + size * 0.52,
            y + size * 0.70,
            x + size * 0.80,
            y + size * 0.86,
        )