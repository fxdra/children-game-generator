from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas



class TracingPDF:

    DEFAULT_INSTRUCTION = (
        "Tebalkan garis putus-putus pada gambar berikut."
    )

    SUPPORTED_FORMATS = {
        ".svg",
        ".png",
        ".jpg",
        ".jpeg",
    }

    @staticmethod
    def generate(
        tracing_data: dict,
        output_path: str,
    ):
        output_file = Path(output_path)

        # Validasi teks tracing
        tracing_text = str(
            tracing_data.get("tracing_text", "")
        ).strip()

        if not tracing_text:
            raise ValueError(
                "Angka atau pola Tracing belum diisi."
            )
        
        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        pdf = canvas.Canvas(
            str(output_file),
            pagesize=A4,
        )

        page_width, page_height = A4

        try:
            TracingPDF._draw_header(
                pdf,
                tracing_data,
                page_width,
                page_height,
            )

            TracingPDF._draw_tracing_text(
                pdf,
                tracing_text,
                page_width,
                page_height,
            )

            TracingPDF._draw_name_field(
                pdf,
                page_width,
            )

            pdf.showPage()
            pdf.save()

        except Exception:
            pdf.save()
            raise

        return str(output_file)

    @staticmethod
    def _draw_header(
        pdf,
        tracing_data,
        page_width,
        page_height,
    ):
        title = tracing_data.get(
            "title",
            "Tracing",
        )

        instruction = tracing_data.get(
            "instruction",
            TracingPDF.DEFAULT_INSTRUCTION,
        )

        pdf.setFont(
            "Helvetica-Bold",
            18,
        )

        pdf.drawCentredString(
            page_width / 2,
            page_height - 30 * mm,
            title,
        )

        pdf.setFont(
            "Helvetica",
            11,
        )

        pdf.drawCentredString(
            page_width / 2,
            page_height - 43 * mm,
            instruction,
        )


    @staticmethod
    def _draw_tracing_text(
        pdf,
        tracing_text,
        page_width,
        page_height,
    ):
        target = str(tracing_text).strip()

        # UKURAN FONT
        font_size = 76
        max_width = page_width * 0.78

        while font_size > 30 and pdf.stringWidth(
            target,
            "Helvetica-Bold",
            font_size,
        ) > max_width:
            font_size -= 2

        text_width = pdf.stringWidth(
            target,
            "Helvetica-Bold",
            font_size,
        )

        # DEBUG: GAMBAR TEKS LANGSUNG KE CANVAS
        pdf.saveState()

        pdf.setFont(
            "Helvetica-Bold",
            font_size,
        )

        pdf.setFillColor(
            colors.HexColor("#8995A5")
        )

        # DRAWING TRACING TEXT
        pdf.saveState()

        pdf.setStrokeColor(
            colors.HexColor("#8995A5")
        )

        pdf.setLineWidth(1.2)
        pdf.setDash(1.5, 2.5)

        text = pdf.beginText()

        text.setTextOrigin(
            (page_width - text_width) / 2,
            page_height - 155 * mm,
        )

        text.setFont(
            "Helvetica-Bold",
            font_size,
        )

        text.setTextRenderMode(1)

        text.textLine(target)

        pdf.drawText(text)

        pdf.restoreState()

        pdf.restoreState()

        # GARIS PANDUAN
        guide_y = page_height - 165 * mm

        pdf.setStrokeColor(
            colors.HexColor("#B8C0CC")
        )

        pdf.setLineWidth(0.8)
        pdf.setDash(2, 3)

        pdf.line(
            25 * mm,
            guide_y,
            page_width - 25 * mm,
            guide_y,
        )

        pdf.setDash()

        # PETUNJUK
        pdf.setFillColor(
            colors.HexColor("#667085")
        )

        pdf.setFont(
            "Helvetica",
            10,
        )

        pdf.drawCentredString(
            page_width / 2,
            page_height - 180 * mm,
            "Telusuri angka mengikuti garis panduan.",
        )

    @staticmethod
    def _draw_name_field(
        pdf,
        page_width,
    ):
        margin = 20 * mm
        name_y = 25 * mm

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
