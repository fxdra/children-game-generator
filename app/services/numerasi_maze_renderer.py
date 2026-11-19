"""Render Numerasi Maze worksheets as SVG."""
from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET

from app.services.openmoji_asset import OpenMojiAssetService


class NumerasiMazeRenderer:
    WIDTH = 800
    HEIGHT = 1000

    def __init__(self, puzzle, character_asset: str | None = None):
        self.puzzle = puzzle
        self.character_asset = character_asset

    def render(self, title: str | None = None, instruction: str | None = None) -> bytes:
        p = self.puzzle
        display_title = title or p.subtype.upper()
        display_instruction = instruction or p.instruction
        if p.subtype == "Number Path":
            return self._render_number_path(display_title, display_instruction)
        return self._render_grid(display_title, display_instruction)

    def _render_number_path(self, title, instruction) -> bytes:
        points = self.puzzle.route_points
        if len(points) < 2:
            raise ValueError("Jalur Number Path belum terbentuk.")
        route_d = self._smooth_path(points)
        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="210mm" height="297mm" viewBox="0 0 {self.WIDTH} {self.HEIGHT}">',
            # Clean white worksheet background.
            '<rect x="0" y="0" width="800" height="1000" fill="#FFFFFF"/>',

            # Subtle worksheet border.
            '<rect x="18" y="18" width="764" height="964" rx="8" fill="none" stroke="#CBD5E1" stroke-width="2"/>',

            # Header.
            f'<text x="400" y="55" text-anchor="middle" font-family="Arial" font-size="30" font-weight="700" fill="#172033">{escape(title)}</text>',
            f'<text x="400" y="88" text-anchor="middle" font-family="Arial" font-size="17" fill="#475569">{escape(instruction)}</text>',
            # Dark outline first, then broad white road ribbon.
            f'<path d="{route_d}" fill="none" stroke="#202020" stroke-width="{getattr(self.puzzle, "road_width", 112.0):g}" stroke-linecap="round" stroke-linejoin="round"/>',
            f'<path d="{route_d}" fill="none" stroke="#FFFFFF" stroke-width="{getattr(self.puzzle, "road_width", 112.0) - 8:g}" stroke-linecap="round" stroke-linejoin="round"/>',
        ]
        labels = getattr(self.puzzle, "number_labels", ())
        if labels:
            for x, y, value, is_target in labels:
                font_size = 34 if value < 10 else 30
                # White halo keeps digits legible against the road without
                # turning them into dotted tracing glyphs.
                parts.append(
                    f'<text x="{x:.1f}" y="{y + 11:.1f}" text-anchor="middle" '
                    f'font-family="Arial" font-size="{font_size}" font-weight="700" '
                    f'fill="#111111">{value}</text>'
                )
        else:
            # Compatibility with older NumerasiMaze objects.
            for index, (x, y) in enumerate(self.puzzle.number_positions, start=1):
                font_size = 34 if index < 10 else 30
                parts.append(
                    f'<text x="{x:.1f}" y="{y + 11:.1f}" text-anchor="middle" '
                    f'font-family="Arial" font-size="{font_size}" font-weight="700" fill="#111111">{index}</text>'
                )


        start_x, start_y = points[0]
        finish_x, finish_y = points[-1]

        start_label_y = (
            start_y - 65 if start_y > 220 else start_y + 110
        )
        finish_label_y = (
            finish_y + 90 if finish_y < 800 else finish_y - 65
        )

        parts.extend([
            f'<text x="{start_x:.1f}" y="{start_label_y:.1f}" text-anchor="middle" font-family="Arial" font-size="24" font-weight="700" fill="#15803D">START</text>',
            f'<circle cx="{start_x:.1f}" cy="{start_y:.1f}" r="8" fill="#FFFFFF" stroke="#15803D" stroke-width="4"/>',
            f'<text x="{finish_x:.1f}" y="{finish_label_y:.1f}" text-anchor="middle" font-family="Arial" font-size="24" font-weight="700" fill="#DC2626">FINISH</text>',
            f'<circle cx="{finish_x:.1f}" cy="{finish_y:.1f}" r="8" fill="#FFFFFF" stroke="#DC2626" stroke-width="4"/>',
        ])
        icon_markup = self._character_svg_markup()
        if icon_markup:
            # Inline the OpenMoji SVG so both Qt preview and PDF export can render it.
            parts.append(icon_markup)
        parts.append('</svg>')
        return ''.join(parts).encode('utf-8')

    @staticmethod
    def _smooth_path(points):
        # Round line joins/caps create the smooth ribbon appearance while the
        # path itself remains deterministic and easy to sample for numbering.
        return "M " + " L ".join(
            f"{x:.1f} {y:.1f}" for x, y in points
        )

    def _character_svg_markup(self):
        if not self.character_asset:
            return None
        asset_path = OpenMojiAssetService.get_asset(self.character_asset, "color")
        root = ET.fromstring(Path(asset_path).read_bytes())
        children = "".join(ET.tostring(child, encoding="unicode") for child in list(root))
        view_box = root.attrib.get("viewBox", "0 0 72 72")
        return (
            f'<svg x="28" y="98" width="76" height="76" viewBox="{escape(view_box)}">'
            f'{children}</svg>'
        )

    def _render_grid(self, title, instruction) -> bytes:
        p = self.puzzle
        cell = 78
        margin = 34
        header = 105
        width = margin * 2 + p.columns * cell
        height = header + margin + p.rows * cell + margin
        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            '<rect width="100%" height="100%" fill="#FFFFFF"/>',
            f'<text x="{width/2}" y="42" text-anchor="middle" font-family="Arial" font-size="25" font-weight="700" fill="#172033">{escape(title.upper())}</text>',
            f'<text x="{width/2}" y="75" text-anchor="middle" font-family="Arial" font-size="14" fill="#455468">{escape(instruction)}</text>',
        ]
        for r, line in enumerate(p.cells):
            for c, value in enumerate(line):
                x = margin + c * cell
                y = header + r * cell
                parts.append(f'<rect x="{x+3}" y="{y+3}" width="{cell-6}" height="{cell-6}" rx="12" fill="#F8FAFC" stroke="#64748B" stroke-width="2"/>')
                font_size = 18 if len(value) > 3 else 25
                parts.append(f'<text x="{x+cell/2}" y="{y+cell/2+font_size/3}" text-anchor="middle" font-family="Arial" font-size="{font_size}" font-weight="700" fill="#172033">{escape(value)}</text>')
        parts.append('</svg>')
        return ''.join(parts).encode('utf-8')
