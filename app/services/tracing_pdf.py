from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg


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

        # Validasi data gambar
        tracing_asset = tracing_data.get("tracing_asset")

        if not tracing_asset:
            raise ValueError(
                "Gambar belum dipilih."
            )

        image_path = Path(tracing_asset["path"])

        if not image_path.exists():
            raise FileNotFoundError(
                f"Gambar Tracing tidak ditemukan: {image_path}"
            )

        if image_path.suffix.lower() not in TracingPDF.SUPPORTED_FORMATS:
            raise ValueError(
                "Format gambar tidak didukung."
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

            TracingPDF._draw_tracing_image(
                pdf,
                image_path,
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
    def _draw_tracing_image(
        pdf,
        image_path,
        page_width,
        page_height,
    ):
        # Area gambar
        margin = 20 * mm

        available_width = page_width - (2 * margin)

        image_bottom = 45 * mm
        image_top = page_height - 55 * mm

        available_height = image_top - image_bottom

        suffix = image_path.suffix.lower()

        if suffix == ".svg":
            TracingPDF._draw_svg(
                pdf,
                image_path,
                margin,
                image_bottom,
                available_width,
                available_height,
            )

        else:
            TracingPDF._draw_raster(
                pdf,
                image_path,
                margin,
                image_bottom,
                available_width,
                available_height,
            )

    @staticmethod
    def _draw_svg(
        pdf,
        image_path,
        x,
        y,
        available_width,
        available_height,
    ):
        drawing = svg2rlg(
            str(image_path)
        )

        if drawing is None:
            raise ValueError(
                "Gagal membaca file SVG Tracing."
            )

        if drawing.width <= 0 or drawing.height <= 0:
            raise ValueError(
                "Ukuran SVG tidak valid."
            )

        scale = min(
            available_width / drawing.width,
            available_height / drawing.height,
        )

        rendered_width = drawing.width * scale
        rendered_height = drawing.height * scale

        center_x = (
            x + available_width / 2
        )

        center_y = (
            y + available_height / 2
        )

        pdf.saveState()

        pdf.translate(
            center_x - rendered_width / 2,
            center_y - rendered_height / 2,
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

    @staticmethod
    def _draw_raster(
        pdf,
        image_path,
        x,
        y,
        available_width,
        available_height,
    ):
        image = ImageReader(
            str(image_path)
        )

        image_width, image_height = image.getSize()

        if image_width <= 0 or image_height <= 0:
            raise ValueError(
                "Ukuran gambar Tracing tidak valid."
            )

        scale = min(
            available_width / image_width,
            available_height / image_height,
        )

        rendered_width = image_width * scale
        rendered_height = image_height * scale

        image_x = (
            x + (available_width - rendered_width) / 2
        )

        image_y = (
            y + (available_height - rendered_height) / 2
        )

        pdf.drawImage(
            image,
            image_x,
            image_y,
            width=rendered_width,
            height=rendered_height,
            preserveAspectRatio=True,
            mask="auto",
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
