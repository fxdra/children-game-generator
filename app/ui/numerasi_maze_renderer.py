from xml.sax.saxutils import escape


class NumerasiMazeRenderer:
    CELL = 78
    MARGIN = 34
    HEADER = 105

    def __init__(self, puzzle):
        self.puzzle = puzzle

    def render(self, title: str | None = None, instruction: str | None = None) -> bytes:
        p = self.puzzle
        display_title = title or p.subtype.upper()
        display_instruction = instruction or p.instruction
        width = self.MARGIN * 2 + p.columns * self.CELL
        height = self.HEADER + self.MARGIN + p.rows * self.CELL + self.MARGIN
        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            '<rect width="100%" height="100%" fill="#FFFFFF"/>',
            f'<text x="{width/2}" y="42" text-anchor="middle" font-family="Arial" font-size="25" font-weight="700" fill="#172033">{escape(display_title.upper())}</text>',
            f'<text x="{width/2}" y="75" text-anchor="middle" font-family="Arial" font-size="14" fill="#455468">{escape(display_instruction)}</text>',
        ]
        for r, line in enumerate(p.cells):
            for c, value in enumerate(line):
                x = self.MARGIN + c * self.CELL
                y = self.HEADER + r * self.CELL
                parts.append(f'<rect x="{x+3}" y="{y+3}" width="{self.CELL-6}" height="{self.CELL-6}" rx="12" fill="#F8FAFC" stroke="#64748B" stroke-width="2"/>')
                font_size = 18 if len(value) > 3 else 25
                parts.append(f'<text x="{x+self.CELL/2}" y="{y+self.CELL/2+font_size/3}" text-anchor="middle" font-family="Arial" font-size="{font_size}" font-weight="700" fill="#172033">{escape(value)}</text>')
        parts.append('</svg>')
        return ''.join(parts).encode('utf-8')
