from pathlib import Path
import re

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg

from app.services.coloring_renderer import ColoringRenderer


class ColoringPDF:

    BASE_DIR = (
        Path(__file__).resolve().parents[2]
    )

    OUTPUT_DIR = (
        BASE_DIR
        / "output"
        / "pdf"
    )

    @staticmethod
    def _safe_filename(text: str) -> str:
        """
        Membersihkan nama file agar aman digunakan
        sebagai nama file Windows.
        """

        text = text.strip()

        if not text:
            return "coloring"

        text = re.sub(
            r'[<>:"/\\|?*]',
            "",
            text,
        )

        text = re.sub(
            r"\s+",
            "-",
            text,
        )

        return text

    @classmethod
    def _get_output_path(
        cls,
        title: str,
    ) -> Path:
        """
        Membuat nama file PDF otomatis.

        Jika file sudah ada:
        coloring.pdf
        coloring (2).pdf
        coloring (3).pdf
        """

        cls.OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        safe_title = cls._safe_filename(
            title
        )

        if not safe_title:
            safe_title = "coloring"

        base_name = safe_title

        output_path = (
            cls.OUTPUT_DIR
            / f"{base_name}.pdf"
        )

        counter = 2

        while output_path.exists():

            output_path = (
                cls.OUTPUT_DIR
                / f"{base_name} ({counter}).pdf"
            )

            counter += 1

        return output_path

    @staticmethod
    def _draw_svg_contain(
        pdf_canvas,
        drawing,
        x: float,
        y: float,
        width: float,
        height: float,
    ):
        """
        Menggambar SVG ke dalam area tertentu
        dengan mempertahankan aspect ratio.
        """

        if drawing is None:
            return

        if not drawing.width or not drawing.height:
            return

        scale_x = width / drawing.width
        scale_y = height / drawing.height

        scale = min(
            scale_x,
            scale_y,
        )

        final_width = (
            drawing.width * scale
        )

        final_height = (
            drawing.height * scale
        )

        offset_x = (
            x
            + (width - final_width) / 2
        )

        offset_y = (
            y
            + (height - final_height) / 2
        )

        pdf_canvas.saveState()

        pdf_canvas.translate(
            offset_x,
            offset_y,
        )

        pdf_canvas.scale(
            scale,
            scale,
        )

        renderPDF.draw(
            drawing,
            pdf_canvas,
            0,
            0,
        )

        pdf_canvas.restoreState()

    @classmethod
    def export(
        cls,
        coloring_data: dict,
    ) -> Path:
        """
        Membuat worksheet Coloring PDF A4
        dengan 3 asset dalam satu halaman.

        coloring_data minimal berisi:

        {
            "assets": [
                "1F336",
                "1F34E",
                "1F408",
            ]
        }

        Optional:
            "title"
        """

        filenames = coloring_data.get(
            "assets",
            [],
        )

        if len(filenames) != 3:
            raise ValueError(
                "Coloring membutuhkan tepat 3 asset."
            )

        # =================================================
        # VALIDASI ASSET
        # =================================================

        drawings = []

        for filename in filenames:

            color_path = (
                ColoringRenderer.get_color_path(
                    filename
                )
            )

            black_path = (
                ColoringRenderer.get_black_path(
                    filename
                )
            )

            if not color_path.exists():
                raise FileNotFoundError(
                    f"Color SVG tidak ditemukan: "
                    f"{color_path}"
                )

            if not black_path.exists():
                raise FileNotFoundError(
                    f"Black SVG tidak ditemukan: "
                    f"{black_path}"
                )

            color_drawing = svg2rlg(
                str(color_path)
            )

            black_drawing = svg2rlg(
                str(black_path)
            )

            drawings.append(
                {
                    "color": color_drawing,
                    "black": black_drawing,
                }
            )

        # =================================================
        # OUTPUT
        # =================================================

        title = coloring_data.get(
            "title",
            "coloring",
        )

        output_path = cls._get_output_path(
            title
        )

        # =================================================
        # A4
        # =================================================

        page_width, page_height = A4

        pdf = canvas.Canvas(
            str(output_path),
            pagesize=A4,
        )

        # =================================================
        # BACKGROUND
        # =================================================

        pdf.setFillColorRGB(
            1,
            1,
            1,
        )

        pdf.rect(
            0,
            0,
            page_width,
            page_height,
            fill=1,
            stroke=0,
        )

        # =================================================
        # TITLE
        # =================================================

        pdf.setFillColorRGB(
            23 / 255,
            32 / 255,
            51 / 255,
        )

        pdf.setFont(
            "Helvetica-Bold",
            22,
        )

        pdf.drawCentredString(
            page_width / 2,
            page_height - 36,
            "MEWARNAI",
        )

        # =================================================
        # 3 ROWS
        # =================================================

        row_height = 250

        row_top = page_height - 40

        for index, drawing_data in enumerate(
            drawings
        ):

            row_y_top = (
                row_top
                - index * row_height
            )

            # =================================================
            # LABEL
            # =================================================

            label_y = (
                row_y_top - 12
            )

            pdf.setFont(
                "Helvetica-Bold",
                11,
            )

            pdf.drawCentredString(
                127,
                label_y,
                "CONTOH",
            )

            pdf.drawCentredString(
                378,
                label_y,
                "WARNAI",
            )

            # =================================================
            # IMAGE AREA
            # =================================================

            image_top = (
                row_y_top - 28
            )

            image_bottom = (
                row_y_top
                - row_height
                + 30
            )

            image_height = (
                image_top
                - image_bottom
            )

            # -------------------------------------------------
            # COLOR
            # -------------------------------------------------

            cls._draw_svg_contain(
                pdf,
                drawing_data["color"],
                x=65,
                y=image_bottom,
                width=125,
                height=image_height,
            )

            # -------------------------------------------------
            # BLACK
            # -------------------------------------------------

            cls._draw_svg_contain(
                pdf,
                drawing_data["black"],
                x=285,
                y=image_bottom,
                width=185,
                height=image_height,
            )

            # =================================================
            # SEPARATOR
            # =================================================

            if index < 2:

                separator_y = (
                    image_bottom - 6
                )

                pdf.setStrokeColorRGB(
                    220 / 255,
                    225 / 255,
                    232 / 255,
                )

                pdf.setLineWidth(
                    0.7
                )

                pdf.line(
                    55,
                    separator_y,
                    page_width - 55,
                    separator_y,
                )

        # =================================================
        # INSTRUCTION
        # =================================================

        pdf.setFillColorRGB(
            23 / 255,
            32 / 255,
            51 / 255,
        )

        pdf.setFont(
            "Helvetica",
            12,
        )

        pdf.drawCentredString(
            page_width / 2,
            45,
            "Warnai gambar sesuai contoh.",
        )

        # =================================================
        # NAME
        # =================================================

        pdf.setFont(
            "Helvetica",
            11,
        )

        name_x = 52
        name_y = 32

        pdf.drawString(
            name_x,
            name_y,
            "Nama:",
        )

        pdf.line(
            92,
            name_y - 2,
            395,
            name_y - 2,
        )

        # =================================================
        # FINISH
        # =================================================

        pdf.showPage()
        pdf.save()

        return output_path