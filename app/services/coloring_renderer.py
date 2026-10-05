from pathlib import Path
import xml.etree.ElementTree as ET


class ColoringRenderer:
    BASE_DIR = (
        Path(__file__).resolve().parents[2]
        / "assets"
        / "openmoji"
    )

    COLOR_DIR = BASE_DIR / "color" / "svg"
    BLACK_DIR = BASE_DIR / "black" / "svg"

    @classmethod
    def get_color_path(cls, filename: str) -> Path:
        path = Path(filename)

        if path.suffix.lower() != ".svg":
            filename = f"{filename}.svg"

        return cls.COLOR_DIR / filename

    @classmethod
    def get_black_path(cls, filename: str) -> Path:
        path = Path(filename)

        if path.suffix.lower() != ".svg":
            filename = f"{filename}.svg"

        return cls.BLACK_DIR / filename
    
    @classmethod
    def validate_pair(cls, filename: str) -> bool:
        color_path = cls.get_color_path(filename)
        black_path = cls.get_black_path(filename)

        return (
            color_path.exists()
            and black_path.exists()
        )

    @classmethod
    def extract_colors(cls, filename: str) -> list[str]:
        color_path = cls.get_color_path(filename)

        if not color_path.exists():
            raise FileNotFoundError(
                f"Color SVG tidak ditemukan: {color_path}"
            )

        root = ET.parse(color_path).getroot()

        colors = set()

        for element in root.iter():
            fill = element.attrib.get("fill")

            if not fill:
                continue

            fill = fill.lower()

            if fill in {
                "none",
                "transparent",
            }:
                continue

            colors.add(fill)

        return sorted(colors)

    @classmethod
    def analyze(cls, filename: str) -> dict:
        """
        Menganalisis pasangan OpenMoji Color + Black.

        Tidak menggunakan hardcode jumlah path,
        polyline, line, atau struktur emoji tertentu.
        """

        if not cls.validate_pair(filename):
            raise FileNotFoundError(
                f"Pasangan OpenMoji tidak lengkap: {filename}"
            )

        color_path = cls.get_color_path(filename)
        black_path = cls.get_black_path(filename)

        color_root = ET.parse(color_path).getroot()

        color_elements = list(color_root.iter())

        color_element_types = set()
        color_regions = []
        color_line_elements = []

        for element in color_elements:
            tag = element.tag.split("}")[-1]

            if tag == "svg":
                continue

            color_element_types.add(tag)

            fill = element.attrib.get("fill")
            stroke = element.attrib.get("stroke")

            # Region berwarna
            if fill and fill.lower() not in {
                "none",
                "transparent",
            }:
                color_regions.append(
                    {
                        "tag": tag,
                        "fill": fill.lower(),
                        "attributes": dict(element.attrib),
                    }
                )

            # Elemen garis / outline
            if (
                stroke
                and stroke.lower() not in {
                    "none",
                    "transparent",
                }
            ):
                color_line_elements.append(
                    {
                        "tag": tag,
                        "stroke": stroke.lower(),
                        "attributes": dict(element.attrib),
                    }
                )

        black_root = ET.parse(black_path).getroot()

        black_elements = list(black_root.iter())

        black_element_types = set()
        black_line_elements = []
        black_line_groups = []

        for element in black_elements:
            tag = element.tag.split("}")[-1]

            if tag == "svg":
                continue

            black_element_types.add(tag)

            stroke = element.attrib.get("stroke")
            fill = element.attrib.get("fill")

            # Elemen visual yang menggunakan stroke
            if (
                stroke
                and stroke.lower() not in {
                    "none",
                    "transparent",
                }
            ):
                black_line_elements.append(
                    {
                        "tag": tag,
                        "stroke": stroke.lower(),
                        "attributes": dict(element.attrib),
                    }
                )

            # Group yang memiliki indikasi line
            if tag == "g":
                element_id = element.attrib.get("id")

                if (
                    element_id
                    and "line" in element_id.lower()
                ):
                    black_line_groups.append(
                        element_id
                    )

        colors = cls.extract_colors(filename)

        has_black_lines = len(black_line_elements) > 0
        has_color_regions = len(color_regions) > 0

        supported = has_black_lines

        return {
            "filename": filename,

            "color_path": color_path,
            "black_path": black_path,

            "colors": colors,
            "color_count": len(colors),

            "color_element_types": sorted(
                color_element_types
            ),
            "color_region_count": len(
                color_regions
            ),
            "color_line_element_count": len(
                color_line_elements
            ),

            "black_element_types": sorted(
                black_element_types
            ),
            "black_line_groups": black_line_groups,
            "black_line_element_count": len(
                black_line_elements
            ),

            "has_color_regions": has_color_regions,
            "has_black_lines": has_black_lines,

            "supported": supported,
        }

    @staticmethod
    def _copy_svg_element(element):
        """
        Copy elemen SVG dan menghilangkan namespace XML
        dari tag maupun atributnya.
        """

        tag = element.tag.split("}")[-1]

        attributes = {}

        for key, value in element.attrib.items():
            clean_key = key.split("}")[-1]
            attributes[clean_key] = value

        copied = ET.Element(
            tag,
            attributes,
        )

        copied.text = element.text
        copied.tail = element.tail

        for child in element:
            copied.append(
                ColoringRenderer._copy_svg_element(child)
            )

        return copied

    @classmethod
    def render_coloring(cls, filename: str) -> dict:
        """
        Membuat prototype worksheet Coloring dalam format SVG.

        Layout:
        - Color SVG = gambar referensi kecil
        - Black SVG = gambar target mewarnai besar
        """

        analysis = cls.analyze(filename)

        if not analysis["supported"]:
            raise ValueError(
                f"Asset tidak mendukung Coloring: {filename}"
            )

        color_path = analysis["color_path"]
        black_path = analysis["black_path"]

        # Parse SVG sumber
        color_root = ET.parse(
            color_path
        ).getroot()

        black_root = ET.parse(
            black_path
        ).getroot()

        # A4 portrait
        page_width = 794
        page_height = 1123

        svg = ET.Element(
            "svg",
            {
                "xmlns": "http://www.w3.org/2000/svg",
                "width": str(page_width),
                "height": str(page_height),
                "viewBox": f"0 0 {page_width} {page_height}",
            },
        )

        # Background
        ET.SubElement(
            svg,
            "rect",
            {
                "x": "0",
                "y": "0",
                "width": str(page_width),
                "height": str(page_height),
                "fill": "#FFFFFF",
            },
        )

        # Judul
        title = ET.SubElement(
            svg,
            "text",
            {
                "x": "397",
                "y": "65",
                "text-anchor": "middle",
                "font-family": "Arial",
                "font-size": "32",
                "font-weight": "bold",
                "fill": "#172033",
            },
        )

        title.text = "MEWARNAI"

        # Label
        example_label = ET.SubElement(
            svg,
            "text",
            {
                "x": "200",
                "y": "120",
                "text-anchor": "middle",
                "font-family": "Arial",
                "font-size": "19",
                "font-weight": "bold",
                "fill": "#172033",
            },
        )

        example_label.text = "CONTOH"

        coloring_label = ET.SubElement(
            svg,
            "text",
            {
                "x": "560",
                "y": "120",
                "text-anchor": "middle",
                "font-family": "Arial",
                "font-size": "19",
                "font-weight": "bold",
                "fill": "#172033",
            },
        )

        coloring_label.text = "WARNAI"


        # COLOR — reference kecil
        color_group = ET.SubElement(
            svg,
            "g",
            {
                "transform": (
                    "translate(100 165) "
                    "scale(2.2)"
                )
            },
        )

        for element in color_root:
            color_group.append(
                cls._copy_svg_element(element)
            )

        # BLACK — target mewarnai
        black_group = ET.SubElement(
            svg,
            "g",
            {
                "transform": (
                    "translate(330 145) "
                    "scale(5.8)"
                ),
            },
        )

        for element in black_root:
            black_group.append(
                cls._copy_svg_element(element)
            )

        # Instruksi
        instruction = ET.SubElement(
            svg,
            "text",
            {
                "x": "397",
                "y": "820",
                "text-anchor": "middle",
                "font-family": "Arial",
                "font-size": "20",
                "fill": "#172033",
            },
        )

        instruction.text = (
            "Warnai gambar sesuai contoh."
        )


        # Nama
        name_label = ET.SubElement(
            svg,
            "text",
            {
                "x": "80",
                "y": "900",
                "font-family": "Arial",
                "font-size": "18",
                "fill": "#172033",
            },
        )

        name_label.text = "Nama:"

        ET.SubElement(
            svg,
            "line",
            {
                "x1": "140",
                "y1": "900",
                "x2": "520",
                "y2": "900",
                "stroke": "#172033",
                "stroke-width": "1",
            },
        )


        # Namespace
        ET.register_namespace(
            "",
            "http://www.w3.org/2000/svg",
        )

        # Simpan
        svg_data = ET.tostring(
            svg,
            encoding="utf-8",
            xml_declaration=True,
        )

        return {
            "filename": filename,
            "svg_data": svg_data,
            "color_path": color_path,
            "black_path": black_path,
        }

    @classmethod
    def render_coloring_sheet(
        cls,
        filenames: list[str],
    ) -> dict:
        """
        Membuat worksheet Coloring A4
        dengan 3 asset dalam satu halaman.

        Setiap asset terdiri dari:
        - Color SVG sebagai contoh
        - Black SVG sebagai gambar untuk diwarnai

        Hasil SVG dibuat di memory.
        Tidak membuat file SVG ke disk.
        """

        if len(filenames) != 3:
            raise ValueError(
                "Coloring membutuhkan tepat 3 asset."
            )

        analyses = []

        for filename in filenames:

            analysis = cls.analyze(
                filename
            )

            if not analysis["supported"]:
                raise ValueError(
                    f"Asset tidak mendukung Coloring: "
                    f"{filename}"
                )

            analyses.append(
                analysis
            )

        # =================================================
        # A4 PORTRAIT
        # =================================================

        page_width = 794
        page_height = 1123

        svg = ET.Element(
            "svg",
            {
                "xmlns": (
                    "http://www.w3.org/2000/svg"
                ),
                "width": str(page_width),
                "height": str(page_height),
                "viewBox": (
                    f"0 0 "
                    f"{page_width} "
                    f"{page_height}"
                ),
            },
        )

        # =================================================
        # BACKGROUND
        # =================================================

        ET.SubElement(
            svg,
            "rect",
            {
                "x": "0",
                "y": "0",
                "width": str(page_width),
                "height": str(page_height),
                "fill": "#FFFFFF",
            },
        )

        # =================================================
        # TITLE
        # =================================================

        title = ET.SubElement(
            svg,
            "text",
            {
                "x": "397",
                "y": "48",
                "text-anchor": "middle",
                "font-family": "Arial",
                "font-size": "30",
                "font-weight": "bold",
                "fill": "#172033",
            },
        )

        title.text = "MEWARNAI"

        # =================================================
        # LAYOUT
        # =================================================

        # Setiap row mendapat ruang sekitar 315 px.
        row_height = 315

        row_start_y = 75

        for index, analysis in enumerate(
            analyses
        ):

            color_path = analysis[
                "color_path"
            ]

            black_path = analysis[
                "black_path"
            ]

            color_root = ET.parse(
                color_path
            ).getroot()

            black_root = ET.parse(
                black_path
            ).getroot()

            row_y = (
                row_start_y
                + index * row_height
            )

            # =================================================
            # ROW LABEL
            # =================================================

            example_label = ET.SubElement(
                svg,
                "text",
                {
                    "x": "170",
                    "y": str(row_y + 22),
                    "text-anchor": "middle",
                    "font-family": "Arial",
                    "font-size": "15",
                    "font-weight": "bold",
                    "fill": "#172033",
                },
            )

            example_label.text = "CONTOH"

            coloring_label = ET.SubElement(
                svg,
                "text",
                {
                    "x": "555",
                    "y": str(row_y + 22),
                    "text-anchor": "middle",
                    "font-family": "Arial",
                    "font-size": "15",
                    "font-weight": "bold",
                    "fill": "#172033",
                },
            )

            coloring_label.text = "WARNAI"

            # =================================================
            # COLOR REFERENCE
            # =================================================

            color_group = ET.SubElement(
                svg,
                "g",
                {
                    "transform": (
                        f"translate(115 "
                        f"{row_y + 40}) "
                        "scale(1.45)"
                    )
                },
            )

            for element in color_root:

                color_group.append(
                    cls._copy_svg_element(
                        element
                    )
                )

            # =================================================
            # BLACK TARGET
            # =================================================

            black_group = ET.SubElement(
                svg,
                "g",
                {
                    "transform": (
                        f"translate(385 "
                        f"{row_y + 35}) "
                        "scale(3.6)"
                    )
                },
            )

            for element in black_root:

                black_group.append(
                    cls._copy_svg_element(
                        element
                    )
                )

            # =================================================
            # SEPARATOR
            # =================================================

            if index < 2:

                ET.SubElement(
                    svg,
                    "line",
                    {
                        "x1": "55",
                        "y1": str(
                            row_y + 292
                        ),
                        "x2": "739",
                        "y2": str(
                            row_y + 292
                        ),
                        "stroke": "#DCE1E8",
                        "stroke-width": "1",
                    },
                )

        # =================================================
        # INSTRUCTION
        # =================================================

        instruction = ET.SubElement(
            svg,
            "text",
            {
                "x": "397",
                "y": "1015",
                "text-anchor": "middle",
                "font-family": "Arial",
                "font-size": "17",
                "fill": "#172033",
            },
        )

        instruction.text = (
            "Warnai gambar sesuai contoh."
        )

        # =================================================
        # NAME
        # =================================================

        name_label = ET.SubElement(
            svg,
            "text",
            {
                "x": "70",
                "y": "1065",
                "font-family": "Arial",
                "font-size": "16",
                "fill": "#172033",
            },
        )

        name_label.text = "Nama:"

        ET.SubElement(
            svg,
            "line",
            {
                "x1": "125",
                "y1": "1065",
                "x2": "500",
                "y2": "1065",
                "stroke": "#172033",
                "stroke-width": "1",
            },
        )

        # =================================================
        # SVG DATA
        # =================================================

        ET.register_namespace(
            "",
            "http://www.w3.org/2000/svg",
        )

        svg_data = ET.tostring(
            svg,
            encoding="utf-8",
            xml_declaration=True,
        )

        return {
            "filenames": list(filenames),
            "svg_data": svg_data,
            "analyses": analyses,
        }