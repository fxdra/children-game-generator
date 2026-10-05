from pathlib import Path

import xml.etree.ElementTree as ET

from app.services.maze_generator import MazeGenerator


class MazeRenderer:
    """
    Renderer maze untuk GameAnak.

    Tugas class ini:
    - membaca RoomGrid dari MazeGenerator
    - menggambar dinding maze
    - menampilkan START dan FINISH
    - menghasilkan SVG di memory

    Tidak menangani:
    - PDF
    - PySide6
    - asset picker
    """

    BASE_DIR = (
        Path(__file__).resolve().parents[2]
        / "assets"
        / "openmoji"
    )

    COLOR_DIR = BASE_DIR / "color" / "svg"

    def __init__(
        self,
        maze_generator: MazeGenerator,
        start_asset: str | None = None,
        finish_asset: str | None = None,
    ):
        self.maze_generator = maze_generator
        self.start_asset = start_asset
        self.finish_asset = finish_asset

    def render(self) -> dict:
        """
        Render maze menjadi SVG.

        Returns:
            dict:
                {
                    "svg_data": bytes,
                    "width_mm": float,
                    "height_mm": float,
                    "start_location": RoomLocation,
                    "finish_location": RoomLocation,
                }
        """

        generator = self.maze_generator.generator

        if generator is None:
            raise RuntimeError(
                "Maze belum dibuat. "
                "Panggil maze_generator.generate() terlebih dahulu."
            )

        room_grid = self.maze_generator.get_room_grid()

        room_count = room_grid.size

        columns = room_count.width
        rows = room_count.height

        cell_size = self.maze_generator.side_length_mm

        width = columns * cell_size
        height = rows * cell_size

        svg = ET.Element(
            "svg",
            {
                "xmlns": "http://www.w3.org/2000/svg",
                "width": f"{width}mm",
                "height": f"{height}mm",
                "viewBox": f"0 0 {width} {height}",
            },
        )

        # Background
        ET.SubElement(
            svg,
            "rect",
            {
                "x": "0",
                "y": "0",
                "width": str(width),
                "height": str(height),
                "fill": "white",
            },
        )

        # Maze walls
        self._draw_walls(
            svg,
            room_grid,
            columns,
            rows,
            cell_size,
        )

        # Outer boundary
        self._draw_outer_walls(
            svg,
            columns,
            rows,
            cell_size,
        )

        # START
        self._draw_endpoint(
            svg,
            self.maze_generator.get_start_room(),
            self.start_asset,
            columns,
            rows,
            cell_size,
        )

        # FINISH
        self._draw_endpoint(
            svg,
            self.maze_generator.get_finish_room(),
            self.finish_asset,
            columns,
            rows,
            cell_size,
        )

        svg_data = ET.tostring(
            svg,
            encoding="utf-8",
            xml_declaration=True,
        )

        return {
            "svg_data": svg_data,
            "width_mm": width,
            "height_mm": height,
            "start_location": self.maze_generator.get_start_room().location,
            "finish_location": self.maze_generator.get_finish_room().location,
        }

    def _draw_walls(
        self,
        svg,
        room_grid,
        columns,
        rows,
        cell_size,
    ):
        """
        Menggambar dinding maze.

        Setiap RoomConnection hanya diproses sekali.
        """

        drawn_walls = set()

        for connection in room_grid.get_all_connections():
            if not connection.is_closed:
                continue

            # Ambil kedua sisi connection.
            room_a = connection.a.room
            wall_a = connection.a.wall

            room_b = connection.b.room
            wall_b = connection.b.wall

            # Identitas dinding dibuat berdasarkan koordinat
            # dan arah supaya tidak menggambar dua kali.
            wall_key_a = (
                room_a.location.x,
                room_a.location.y,
                wall_a.direction.value,
            )

            wall_key_b = (
                room_b.location.x,
                room_b.location.y,
                wall_b.direction.value,
            )

            wall_key = tuple(
                sorted(
                    (
                        wall_key_a,
                        wall_key_b,
                    )
                )
            )

            if wall_key in drawn_walls:
                continue

            drawn_walls.add(wall_key)

            self._draw_wall(
                svg,
                wall_a,
                columns,
                rows,
                cell_size,
            )

    def _draw_wall(
        self,
        svg,
        wall,
        columns,
        rows,
        cell_size,
    ):
        """
        Menggambar satu dinding.
        """

        x = wall.location.x * cell_size
        y = wall.location.y * cell_size

        direction = wall.direction.name

        if direction == "NORTH":
            x1 = x
            y1 = y
            x2 = x + cell_size
            y2 = y

        elif direction == "EAST":
            x1 = x + cell_size
            y1 = y
            x2 = x + cell_size
            y2 = y + cell_size

        elif direction == "SOUTH":
            x1 = x
            y1 = y + cell_size
            x2 = x + cell_size
            y2 = y + cell_size

        elif direction == "WEST":
            x1 = x
            y1 = y
            x2 = x
            y2 = y + cell_size

        else:
            return

        ET.SubElement(
            svg,
            "line",
            {
                "x1": str(x1),
                "y1": str(y1),
                "x2": str(x2),
                "y2": str(y2),
                "stroke": "#172033",
                "stroke-width": "1.2",
                "stroke-linecap": "round",
            },
        )

    def _draw_outer_walls(
        self,
        svg,
        columns,
        rows,
        cell_size,
    ):
        """
        Menggambar batas luar maze.

        START berada di pojok kiri atas.
        FINISH berada di pojok kanan bawah.

        Area START dan FINISH dibuat sebagai
        entrance / exit.
        """

        width = columns * cell_size
        height = rows * cell_size

        start_room = self.maze_generator.get_start_room()
        finish_room = self.maze_generator.get_finish_room()

        start_x = start_room.location.x * cell_size
        start_y = start_room.location.y * cell_size

        finish_x = finish_room.location.x * cell_size
        finish_y = finish_room.location.y * cell_size

        stroke = {
            "stroke": "#172033",
            "stroke-width": "1.2",
            "stroke-linecap": "round",
        }

        # ==================================================
        # TOP
        # START berada di pojok kiri atas.
        # Buka cell START.
        # ==================================================

        ET.SubElement(
            svg,
            "line",
            {
                "x1": str(start_x + cell_size),
                "y1": "0",
                "x2": str(width),
                "y2": "0",
                **stroke,
            },
        )

        # ==================================================
        # LEFT
        # START berada di pojok kiri atas.
        # Buka cell START.
        # ==================================================

        ET.SubElement(
            svg,
            "line",
            {
                "x1": "0",
                "y1": str(start_y + cell_size),
                "x2": "0",
                "y2": str(height),
                **stroke,
            },
        )

        # ==================================================
        # RIGHT
        # FINISH berada di pojok kanan bawah.
        # Buka cell FINISH.
        # ==================================================

        ET.SubElement(
            svg,
            "line",
            {
                "x1": str(width),
                "y1": "0",
                "x2": str(width),
                "y2": str(finish_y),
                **stroke,
            },
        )

        # ==================================================
        # BOTTOM
        # FINISH berada di pojok kanan bawah.
        # Buka cell FINISH.
        # ==================================================

        ET.SubElement(
            svg,
            "line",
            {
                "x1": "0",
                "y1": str(height),
                "x2": str(finish_x),
                "y2": str(height),
                **stroke,
            },
        )
        
    def _draw_endpoint(
        self,
        svg,
        room,
        asset_name,
        columns,
        rows,
        cell_size,
    ):
        """
        Menggambar asset START/FINISH.

        Untuk tahap awal, jika asset belum diberikan,
        endpoint tetap ditampilkan sebagai lingkaran.
        """

        cx = (
            room.location.x * cell_size
            + cell_size / 2
        )

        cy = (
            room.location.y * cell_size
            + cell_size / 2
        )

        radius = cell_size * 0.28

        if asset_name:
            self._draw_asset(
                svg,
                asset_name,
                cx,
                cy,
                cell_size,
            )
            return

        ET.SubElement(
            svg,
            "circle",
            {
                "cx": str(cx),
                "cy": str(cy),
                "r": str(radius),
                "fill": "#F8F9FB",
                "stroke": "#2F6FED",
                "stroke-width": "1.2",
            },
        )

    def _draw_asset(
        self,
        svg,
        asset_name,
        cx,
        cy,
        cell_size,
    ):
        """
        Menampilkan OpenMoji Color dengan cara
        meng-embed elemen SVG langsung ke dalam
        SVG maze.

        Cara ini kompatibel dengan:
        - browser
        - QSvgWidget
        - svglib / ReportLab
        """

        filename = asset_name

        if not filename.lower().endswith(".svg"):
            filename = f"{filename}.svg"

        asset_path = self.COLOR_DIR / filename

        if not asset_path.exists():
            raise FileNotFoundError(
                f"Asset OpenMoji tidak ditemukan: {asset_path}"
            )

        # OpenMoji umumnya menggunakan viewBox 72 x 72.
        asset_svg = ET.parse(asset_path).getroot()

        view_box = asset_svg.get("viewBox")

        if not view_box:
            raise ValueError(
                f"OpenMoji tidak memiliki viewBox: {asset_path}"
            )

        _, _, view_width, view_height = map(
            float,
            view_box.split(),
        )

        size = cell_size * 0.9

        scale_x = size / view_width
        scale_y = size / view_height

        x = cx - size / 2
        y = cy - size / 2

        asset_group = ET.SubElement(
            svg,
            "g",
            {
                "transform": (
                    f"translate({x} {y}) "
                    f"scale({scale_x} {scale_y})"
                ),
            },
        )

        # Copy seluruh isi OpenMoji ke dalam group.
        for child in asset_svg:
            asset_group.append(child)
