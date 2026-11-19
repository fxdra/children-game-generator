from __future__ import annotations

import random
import xml.etree.ElementTree as ET
from pathlib import Path

from app.services.meatfighter_maze_renderer import MeatFighterMazeRenderer
from app.services.openmoji_asset import OpenMojiAssetService


class NumberPathRenderer:
    SVG_NS = "http://www.w3.org/2000/svg"
    PAGE_WIDTH_MM = 210.0
    PAGE_HEIGHT_MM = 297.0
    CELL_SIZE_MM = 5.6
    TARGETS = {"Mudah": 10, "Sedang": 15, "Sulit": 20}
    DECOYS = {"Mudah": 3, "Sedang": 5, "Sulit": 8}

    def __init__(
        self,
        maze,
        difficulty: str = "Mudah",
        start_asset: str | None = None,
        finish_asset: str | None = None,
        seed: int | None = 0,
    ) -> None:
        self.maze = maze
        self.difficulty = difficulty if difficulty in self.TARGETS else "Mudah"
        self.start_asset = start_asset
        self.finish_asset = finish_asset
        self.seed = seed
        self.random = random.Random(seed)

    def render(self, title: str = "Number Path", instruction: str | None = None) -> bytes:
        maze = self.maze
        if not maze.solution or maze.start is None or maze.finish is None:
            raise ValueError("Maze Meat Fighter belum memiliki jalur solusi.")

        target_count = self.TARGETS[self.difficulty]
        labels = self._build_number_labels(target_count)
        cell_size = self.CELL_SIZE_MM
        maze_width = maze.width * cell_size
        maze_height = maze.height * cell_size
        if maze_width > self.PAGE_WIDTH_MM - 16 or maze_height > 205:
            raise ValueError("Ukuran maze tidak muat pada halaman A4.")

        offset_x = (self.PAGE_WIDTH_MM - maze_width) / 2
        offset_y = 76.0
        if offset_y + maze_height > 270:
            offset_y = 270.0 - maze_height

        rendered = MeatFighterMazeRenderer(
            maze,
            cell_size_mm=cell_size,
            show_solution=False,
            wall_color="#172033",
            background="#FFFFFF",
            line_width=0.58,
        ).render()
        maze_svg = ET.fromstring(rendered["svg_data"])

        root = ET.Element(
            f"{{{self.SVG_NS}}}svg",
            {
                "width": "210mm",
                "height": "297mm",
                "viewBox": "0 0 210 297",
                "version": "1.1",
            },
        )
        self._element(root, "rect", {
            "x": "0", "y": "0", "width": "210", "height": "297", "fill": "#FFFFFF"
        })
        self._element(root, "rect", {
            "x": "7", "y": "7", "width": "196", "height": "283",
            "rx": "2", "fill": "none", "stroke": "#CBD5E1", "stroke-width": "0.45",
        })
        self._text(root, 105, 25, title, 7, bold=True, fill="#172033")
        default_instruction = (
            f"Mulai dari START. Cari angka 1 sampai {target_count} secara berurutan hingga FINISH."
        )
        self._text(root, 105, 34, instruction or default_instruction, 3.7, fill="#475569")

        group = ET.SubElement(root, f"{{{self.SVG_NS}}}g", {
            "transform": f"translate({offset_x:.3f} {offset_y:.3f})"
        })
        for child in list(maze_svg):
            group.append(child)

        for x, y, value, _is_target in labels:
            cx = offset_x + (x + 0.5) * cell_size
            cy = offset_y + (y + 0.5) * cell_size

            # Ukuran angka disesuaikan dengan lebar lorong.
            font_size = 3.4 if value < 10 else 2.8

            self._text(
                root,
                cx,
                cy + font_size * 0.32,
                str(value),
                font_size,
                bold=True,
                fill="#111827",
                stroke="#FFFFFF",
                stroke_width="0.25",
            )

        self._draw_endpoint(root, maze.start, "START", self.start_asset, "#2563EB", offset_x, offset_y)
        self._draw_endpoint(root, maze.finish, "FINISH", self.finish_asset, "#16A34A", offset_x, offset_y)
        return ET.tostring(root, encoding="utf-8", xml_declaration=True)

    def _build_number_labels(self, target_count: int) -> list[tuple[int, int, int, bool]]:
        # Re-seed per render so preview and PDF export use identical labels.
        self.random = random.Random(self.seed)
        maze = self.maze
        solution = list(maze.solution)
        if len(solution) < target_count + 2:
            raise ValueError(
                f"Jalur solusi terlalu pendek: perlu minimal {target_count + 2} node, "
                f"tersedia {len(solution)}."
            )

        endpoints = {maze.start, maze.finish}
        candidates = []
        seen_cells: set[tuple[int, int]] = set()
        for node in solution:
            cell = node.cell
            point = (cell.x, cell.y)
            if node in endpoints or point in seen_cells or not cell.white:
                continue
            is_crossing = bool(list(cell.lower.neighbors())) and bool(list(cell.upper.neighbors()))
            if is_crossing:
                continue
            seen_cells.add(point)
            candidates.append((node, point))


        if len(candidates) < target_count:
            raise ValueError("Tidak cukup sel jalur solusi untuk menempatkan angka target.")

        # Spread target positions along the solution order, retaining the Node
        # sequence rather than reconstructing a route from x/y coordinates.
        if target_count == 1:
            chosen = [candidates[len(candidates) // 2]]
        else:
            indexes = [round(i * (len(candidates) - 1) / (target_count - 1)) for i in range(target_count)]
            chosen = [candidates[index] for index in indexes]

        values = list(range(1, target_count + 1))
        labels = [(point[0], point[1], value, True) for (_, point), value in zip(chosen, values)]
        occupied = {(x, y) for x, y, _, _ in labels}
        occupied.update((maze.start.cell.x, maze.start.cell.y) for _ in [0])
        occupied.add((maze.finish.cell.x, maze.finish.cell.y))

        decoy_cells = []
        for row in maze.cells:
            for cell in row:
                point = (cell.x, cell.y)
                is_crossing = bool(list(cell.lower.neighbors())) and bool(list(cell.upper.neighbors()))
                if cell.white and point not in occupied and not is_crossing:
                    decoy_cells.append(point)
        decoy_count = self.DECOYS[self.difficulty]
        if len(decoy_cells) < decoy_count:
            raise ValueError(
                f"Tidak cukup sel aman untuk angka pengecoh: "
                f"dibutuhkan {decoy_count}, tersedia {len(decoy_cells)}."
            )
        if len(decoy_cells) < decoy_count:
            raise ValueError("Tidak cukup sel kosong untuk menempatkan angka pengecoh.")
        for x, y in self.random.sample(decoy_cells, decoy_count):
            labels.append((x, y, self.random.randint(1, target_count), False))
        return labels

    def _draw_endpoint(self, root, node, label, asset_name, color, ox, oy):
        cell_size = self.CELL_SIZE_MM
        cx = ox + (node.cell.x + 0.5) * cell_size
        cy = oy + (node.cell.y + 0.5) * cell_size
        if asset_name:
            icon = self._load_asset_svg(asset_name)
            if icon is not None:
                icon.set("x", f"{cx - 2.35:.3f}")
                icon.set("y", f"{cy - 2.35:.3f}")
                icon.set("width", "4.7")
                icon.set("height", "4.7")
                root.append(icon)
        # Put callout just outside the maze edge nearest the endpoint.
        x, y = node.cell.x, node.cell.y
        maze_w, maze_h = self.maze.width * cell_size, self.maze.height * cell_size
        if x == 0:
            tx, ty, anchor = ox - 1.5, cy + 1.1, "end"
        elif x == self.maze.width - 1:
            tx, ty, anchor = ox + maze_w + 1.5, cy + 1.1, "start"
        elif y == 0:
            tx, ty, anchor = cx, oy - 2.0, "middle"
        else:
            tx, ty, anchor = cx, oy + maze_h + 5.0, "middle"
        self._text(root, tx, ty, label, 3.3, bold=True, fill=color, anchor=anchor)

    def _load_asset_svg(self, asset_name: str):
        if not asset_name:
            return None

        try:
            path = OpenMojiAssetService.get_asset(asset_name, "color")

            if not path:
                return None

            path = Path(path)

            if not path.is_file():
                return None

            source = ET.fromstring(path.read_bytes())

            view_box = source.attrib.get("viewBox", "0 0 72 72")

            wrapper = ET.Element(
                f"{{{self.SVG_NS}}}svg",
                {"viewBox": view_box}
            )

            for child in list(source):
                wrapper.append(child)

            return wrapper

        except (OSError, ET.ParseError, TypeError, ValueError):
            return None

    @classmethod
    def _element(cls, parent, tag, attributes):
        return ET.SubElement(parent, f"{{{cls.SVG_NS}}}{tag}", attributes)

    @classmethod
    def _text(cls, parent, x, y, value, size, bold=False, fill="#111827", anchor="middle", stroke=None, stroke_width=None):
        attrs = {
            "x": f"{x:.3f}", "y": f"{y:.3f}", "text-anchor": anchor,
            "font-family": "DejaVu Sans, Arial, sans-serif", "font-size": f"{size:.2f}",
            "font-weight": "700" if bold else "400", "fill": fill,
        }
        if stroke:
            attrs.update({"paint-order": "stroke", "stroke": stroke, "stroke-width": str(stroke_width or 0.4), "stroke-linejoin": "round"})
        node = ET.SubElement(parent, f"{{{cls.SVG_NS}}}text", attrs)
        node.text = str(value)
        return node
