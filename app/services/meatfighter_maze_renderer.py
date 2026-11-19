"""Faithful Python/SVG port of Meat Fighter's src/render/maze-renderer.ts.

The wall and solution geometry follows generateWallPaths() and
generateSolutionPaths() from the upstream TypeScript implementation.
Only the output adapter differs: this module writes SVG rather than using
node-canvas to write SVG/PNG/PDF.
"""
from __future__ import annotations

import math
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Any

from app.services.maze_graph_processor import Maze


@dataclass(frozen=True)
class _Point:
    x: float
    y: float


@dataclass(frozen=True)
class _Segment:
    kind: str
    start: _Point
    end: _Point
    control: _Point | None = None
    radius: float = 0.0


class _PathBuilder:
    """Direct equivalent of the source PathOptimizer drawing API.

    The upstream optimizer only joins/merges compatible segments. Keeping
    source segments as separate SVG subpaths preserves the same geometry.
    """
    def __init__(self) -> None:
        self.cursor = _Point(0.0, 0.0)
        self.segments: list[_Segment] = []

    def move_to(self, x: float, y: float) -> None:
        self.cursor = _Point(float(x), float(y))

    def line_to(self, x: float, y: float) -> None:
        point = _Point(float(x), float(y))
        self.segments.append(_Segment("line", self.cursor, point))
        self.cursor = point

    def arc_to(self, x1: float, y1: float, x2: float, y2: float, radius: float) -> None:
        p1, p2 = _Point(float(x1), float(y1)), _Point(float(x2), float(y2))
        self.segments.append(_Segment("arc", self.cursor, p2, p1, float(radius)))
        self.cursor = p2

    def paths(self) -> list[_Segment]:
        result = self.segments
        self.cursor = _Point(0.0, 0.0)
        self.segments = []
        return result


class MeatFighterMazeRenderer:
    """Render the Meat Fighter two-layer maze using upstream wall geometry."""

    SVG_NS = "http://www.w3.org/2000/svg"

    def __init__(
        self,
        maze: Maze,
        cell_size_mm: float = 6.0,
        show_solution: bool = False,
        wall_color: str = "#172033",
        solution_color: str = "#E53935",
        background: str = "#FFFFFF",
        line_width_frac: float = 0.15,
        passage_width_frac: float = 0.70,
        rounded_corners: bool = True,
        line_width: float | None = None,
    ) -> None:
        if cell_size_mm <= 0:
            raise ValueError("cell_size_mm harus lebih besar dari 0")
        if not 0 < passage_width_frac <= 1:
            raise ValueError("passage_width_frac harus berada pada rentang (0, 1]")
        if line_width_frac < 0 or line_width_frac > 1:
            raise ValueError("line_width_frac harus berada pada rentang 0–1")
        if line_width is not None and line_width <= 0:
            raise ValueError("line_width harus lebih besar dari 0")
        self.maze = maze
        self.cell_size_mm = float(cell_size_mm)
        self.show_solution = bool(show_solution)
        self.wall_color = wall_color
        self.solution_color = solution_color
        self.background = background
        # Upstream uses lineWidthFrac * cellSize. The legacy line_width
        # argument is retained as an absolute-width compatibility override.
        self.line_width_frac = (
            float(line_width) / self.cell_size_mm
            if line_width is not None else float(line_width_frac)
        )
        self.passage_width_frac = float(passage_width_frac)
        self.rounded_corners = bool(rounded_corners)

    def render(self) -> dict[str, Any]:
        maze = self.maze
        if maze.width < 1 or maze.height < 1:
            raise ValueError("Maze kosong atau memiliki ukuran tidak valid")

        cell = self.cell_size_mm
        width, height = maze.width * cell, maze.height * cell
        svg = ET.Element(
            f"{{{self.SVG_NS}}}svg",
            {
                "width": f"{width:g}mm",
                "height": f"{height:g}mm",
                "viewBox": f"0 0 {width:g} {height:g}",
                "version": "1.1",
            },
        )
        ET.SubElement(svg, f"{{{self.SVG_NS}}}rect", {
            "x": "0", "y": "0", "width": f"{width:g}",
            "height": f"{height:g}", "fill": self.background,
        })

        margin = (1.0 - self.passage_width_frac) / 2.0
        if self.show_solution:
            solution_segments = self._generate_solution_paths(maze, cell, margin)
            self._render_segments(svg, solution_segments, self.solution_color)
        wall_segments = self._generate_wall_paths(maze, cell, margin)
        self._render_segments(svg, wall_segments, self.wall_color)

        data = ET.tostring(svg, encoding="utf-8", xml_declaration=True)
        return {
            "svg_data": data,
            "width_mm": width,
            "height_mm": height,
            "start_location": self._location(maze.start),
            "finish_location": self._location(maze.finish),
        }

    @staticmethod
    def _location(node: Any) -> dict[str, int] | None:
        if node is None:
            return None
        return {"x": node.cell.x, "y": node.cell.y}

    @staticmethod
    def _generate_solution_paths(maze: Maze, cell_size: float, margin_frac: float) -> list[_Segment]:
        c = _PathBuilder()
        d0 = margin_frac * cell_size
        d1 = (1.0 - margin_frac) * cell_size
        dm = cell_size / 2.0

        for i in range(maze.height - 1, -1, -1):
            oy = i * cell_size
            for j in range(maze.width - 1, -1, -1):
                ox = j * cell_size
                cell = maze.cells[i][j]

                if cell.upper.north2 is not None:
                    c.move_to(ox + dm, oy)
                    c.line_to(ox + dm, oy + cell_size)
                elif cell.upper.east2 is not None:
                    c.move_to(ox, oy + dm)
                    c.line_to(ox + cell_size, oy + dm)

                if cell.upper.north is not None and cell.lower.east2 is not None:
                    c.move_to(ox, oy + dm)
                    c.line_to(ox + d0, oy + dm)
                    c.move_to(ox + d1, oy + dm)
                    c.line_to(ox + cell_size, oy + dm)
                elif cell.upper.east is not None and cell.lower.north2 is not None:
                    c.move_to(ox + dm, oy)
                    c.line_to(ox + dm, oy + d0)
                    c.move_to(ox + dm, oy + d1)
                    c.line_to(ox + dm, oy + cell_size)
                else:
                    lower = cell.lower
                    value = (
                        (0b1000 if lower.north2 is not None else 0)
                        | (0b0100 if lower.east2 is not None else 0)
                        | (0b0010 if lower.south2 is not None else 0)
                        | (0b0001 if lower.west2 is not None else 0)
                    )
                    if value == 0b1100:
                        c.move_to(ox + dm, oy)
                        c.arc_to(ox + dm, oy + dm, ox + cell_size, oy + dm, dm)
                    elif value == 0b0110:
                        c.move_to(ox + cell_size, oy + dm)
                        c.arc_to(ox + dm, oy + dm, ox + dm, oy + cell_size, dm)
                    elif value == 0b0011:
                        c.move_to(ox + dm, oy + cell_size)
                        c.arc_to(ox + dm, oy + dm, ox, oy + dm, dm)
                    elif value == 0b1001:
                        c.move_to(ox, oy + dm)
                        c.arc_to(ox + dm, oy + dm, ox + dm, oy, dm)
                    elif value == 0b1010:
                        c.move_to(ox + dm, oy)
                        c.line_to(ox + dm, oy + cell_size)
                    elif value == 0b0101:
                        c.move_to(ox, oy + dm)
                        c.line_to(ox + cell_size, oy + dm)
        return c.paths()

    @staticmethod
    def _generate_wall_paths(maze: Maze, cell_size: float, margin_frac: float) -> list[_Segment]:
        c = _PathBuilder()
        d0 = margin_frac * cell_size
        d1 = (1.0 - margin_frac) * cell_size
        dm = cell_size / 2.0
        r0 = (d1 - d0) / 2.0

        for i in range(maze.height - 1, -1, -1):
            oy = i * cell_size
            for j in range(maze.width - 1, -1, -1):
                ox = j * cell_size
                cell = maze.cells[i][j]

                if cell.upper.north is not None:
                    c.move_to(ox + d0, oy)
                    c.line_to(ox + d0, oy + cell_size)
                    c.move_to(ox + d1, oy)
                    c.line_to(ox + d1, oy + cell_size)
                    c.move_to(ox, oy + d0)
                    c.line_to(ox + d0, oy + d0)
                    c.move_to(ox, oy + d1)
                    c.line_to(ox + d0, oy + d1)
                    c.move_to(ox + d1, oy + d0)
                    c.line_to(ox + cell_size, oy + d0)
                    c.move_to(ox + d1, oy + d1)
                    c.line_to(ox + cell_size, oy + d1)
                elif cell.upper.east is not None:
                    c.move_to(ox, oy + d0)
                    c.line_to(ox + cell_size, oy + d0)
                    c.move_to(ox, oy + d1)
                    c.line_to(ox + cell_size, oy + d1)
                    c.move_to(ox + d0, oy)
                    c.line_to(ox + d0, oy + d0)
                    c.move_to(ox + d1, oy)
                    c.line_to(ox + d1, oy + d0)
                    c.move_to(ox + d0, oy + d1)
                    c.line_to(ox + d0, oy + cell_size)
                    c.move_to(ox + d1, oy + d1)
                    c.line_to(ox + d1, oy + cell_size)
                else:
                    lower = cell.lower
                    value = (
                        (0b1000 if lower.north is not None else 0)
                        | (0b0100 if lower.east is not None else 0)
                        | (0b0010 if lower.south is not None else 0)
                        | (0b0001 if lower.west is not None else 0)
                    )

                    if value == 0b1000:
                        c.move_to(ox + d0, oy)
                        c.line_to(ox + d0, oy + dm)
                        c.arc_to(ox + d0, oy + d1, ox + dm, oy + d1, r0)
                        c.arc_to(ox + d1, oy + d1, ox + d1, oy + dm, r0)
                        c.line_to(ox + d1, oy)
                    elif value == 0b0100:
                        c.move_to(ox + cell_size, oy + d0)
                        c.line_to(ox + dm, oy + d0)
                        c.arc_to(ox + d0, oy + d0, ox + d0, oy + dm, r0)
                        c.arc_to(ox + d0, oy + d1, ox + dm, oy + d1, r0)
                        c.line_to(ox + cell_size, oy + d1)
                    elif value == 0b0010:
                        c.move_to(ox + d0, oy + cell_size)
                        c.line_to(ox + d0, oy + dm)
                        c.arc_to(ox + d0, oy + d0, ox + dm, oy + d0, r0)
                        c.arc_to(ox + d1, oy + d0, ox + d1, oy + dm, r0)
                        c.line_to(ox + d1, oy + cell_size)
                    elif value == 0b0001:
                        c.move_to(ox, oy + d0)
                        c.line_to(ox + dm, oy + d0)
                        c.arc_to(ox + d1, oy + d0, ox + d1, oy + dm, r0)
                        c.arc_to(ox + d1, oy + d1, ox + dm, oy + d1, r0)
                        c.line_to(ox, oy + d1)
                    elif value == 0b1100:
                        c.move_to(ox + d0, oy)
                        c.arc_to(ox + d0, oy + d1, ox + cell_size, oy + d1, d1)
                        c.move_to(ox + d1, oy)
                        c.arc_to(ox + d1, oy + d0, ox + cell_size, oy + d0, d0)
                    elif value == 0b0110:
                        c.move_to(ox + d0, oy + cell_size)
                        c.arc_to(ox + d0, oy + d0, ox + cell_size, oy + d0, d1)
                        c.move_to(ox + d1, oy + cell_size)
                        c.arc_to(ox + d1, oy + d1, ox + cell_size, oy + d1, d0)
                    elif value == 0b0011:
                        c.move_to(ox + d1, oy + cell_size)
                        c.arc_to(ox + d1, oy + d0, ox, oy + d0, d1)
                        c.move_to(ox + d0, oy + cell_size)
                        c.arc_to(ox + d0, oy + d1, ox, oy + d1, d0)
                    elif value == 0b1001:
                        c.move_to(ox + d1, oy)
                        c.arc_to(ox + d1, oy + d1, ox, oy + d1, d1)
                        c.move_to(ox + d0, oy)
                        c.arc_to(ox + d0, oy + d0, ox, oy + d0, d0)
                    elif value == 0b1101:
                        c.move_to(ox, oy + d1)
                        c.line_to(ox + cell_size, oy + d1)
                        c.move_to(ox + d1, oy)
                        c.arc_to(ox + d1, oy + d0, ox + cell_size, oy + d0, d0)
                        c.move_to(ox + d0, oy)
                        c.arc_to(ox + d0, oy + d0, ox, oy + d0, d0)
                    elif value == 0b1110:
                        c.move_to(ox + d0, oy)
                        c.line_to(ox + d0, oy + cell_size)
                        c.move_to(ox + d1, oy)
                        c.arc_to(ox + d1, oy + d0, ox + cell_size, oy + d0, d0)
                        c.move_to(ox + d1, oy + cell_size)
                        c.arc_to(ox + d1, oy + d1, ox + cell_size, oy + d1, d0)
                    elif value == 0b0111:
                        c.move_to(ox, oy + d0)
                        c.line_to(ox + cell_size, oy + d0)
                        c.move_to(ox + d1, oy + cell_size)
                        c.arc_to(ox + d1, oy + d1, ox + cell_size, oy + d1, d0)
                        c.move_to(ox + d0, oy + cell_size)
                        c.arc_to(ox + d0, oy + d1, ox, oy + d1, d0)
                    elif value == 0b1011:
                        c.move_to(ox + d1, oy)
                        c.line_to(ox + d1, oy + cell_size)
                        c.move_to(ox + d0, oy + cell_size)
                        c.arc_to(ox + d0, oy + d1, ox, oy + d1, d0)
                        c.move_to(ox + d0, oy)
                        c.arc_to(ox + d0, oy + d0, ox, oy + d0, d0)
                    elif value == 0b1111:
                        c.move_to(ox + d1, oy)
                        c.arc_to(ox + d1, oy + d0, ox + cell_size, oy + d0, d0)
                        c.move_to(ox + d1, oy + cell_size)
                        c.arc_to(ox + d1, oy + d1, ox + cell_size, oy + d1, d0)
                        c.move_to(ox + d0, oy + cell_size)
                        c.arc_to(ox + d0, oy + d1, ox, oy + d1, d0)
                        c.move_to(ox + d0, oy)
                        c.arc_to(ox + d0, oy + d0, ox, oy + d0, d0)
                    elif value == 0b1010:
                        c.move_to(ox + d0, oy)
                        c.line_to(ox + d0, oy + cell_size)
                        c.move_to(ox + d1, oy)
                        c.line_to(ox + d1, oy + cell_size)
                    elif value == 0b0101:
                        c.move_to(ox, oy + d0)
                        c.line_to(ox + cell_size, oy + d0)
                        c.move_to(ox, oy + d1)
                        c.line_to(ox + cell_size, oy + d1)
        return c.paths()

    @staticmethod
    def _arc_to_svg(segment: _Segment) -> str:
        """Convert Canvas arcTo(p1,p2,r) to an SVG circular A command."""
        p0, p1, p2 = segment.start, segment.control, segment.end
        assert p1 is not None
        r = segment.radius
        if r <= 0:
            return f"L {p2.x:g} {p2.y:g}"

        v1x, v1y = p0.x - p1.x, p0.y - p1.y
        v2x, v2y = p2.x - p1.x, p2.y - p1.y
        l1, l2 = math.hypot(v1x, v1y), math.hypot(v2x, v2y)
        if l1 == 0 or l2 == 0:
            return f"L {p2.x:g} {p2.y:g}"
        u1x, u1y, u2x, u2y = v1x / l1, v1y / l1, v2x / l2, v2y / l2
        dot = max(-1.0, min(1.0, u1x * u2x + u1y * u2y))
        theta = math.acos(dot)
        if theta < 1e-8 or abs(math.pi - theta) < 1e-8:
            return f"L {p2.x:g} {p2.y:g}"
        tangent = r / math.tan(theta / 2.0)
        tangent = min(tangent, l1, l2)
        t1x, t1y = p1.x + u1x * tangent, p1.y + u1y * tangent
        t2x, t2y = p1.x + u2x * tangent, p1.y + u2y * tangent
        cross = u1x * u2y - u1y * u2x
        sweep = 0 if cross > 0 else 1
        return (
            f"L {t1x:g} {t1y:g} "
            f"A {r:g} {r:g} 0 0 {sweep} {t2x:g} {t2y:g} "
            f"L {p2.x:g} {p2.y:g}"
        )

    def _render_segments(self, svg: ET.Element, segments: list[_Segment], color: str) -> None:
        for segment in segments:
            d = f"M {segment.start.x:g} {segment.start.y:g} "
            if segment.kind == "line":
                d += f"L {segment.end.x:g} {segment.end.y:g}"
            else:
                d += self._arc_to_svg(segment)
            ET.SubElement(svg, f"{{{self.SVG_NS}}}path", {
                "d": d,
                "fill": "none",
                "stroke": color,
                "stroke-width": f"{self.line_width_frac * self.cell_size_mm:g}",
                "stroke-linecap": "round" if self.rounded_corners else "square",
                "stroke-linejoin": "round" if self.rounded_corners else "miter",
            })
