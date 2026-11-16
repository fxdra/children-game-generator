from pathlib import Path
from random import Random

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF

from app.services.openmoji_asset import OpenMojiAssetService


class NumerasiMatchingCardPDFService:
    @classmethod
    def build_cards(cls, matching_data):
        mode = matching_data.get("matching_mode")
        pairs = matching_data.get("pairs", [])
        left, right = [], []
        for index, pair in enumerate(pairs, start=1):
            if mode == "Angka ↔ Jumlah benda":
                left.append({"pair_index": index, "type": "number", "text": str(pair["number"])})
                right.append({"pair_index": index, "type": "quantity", "asset": pair["asset"], "quantity": int(pair["quantity"])})
            elif mode == "Angka ↔ Nama bilangan":
                left.append({"pair_index": index, "type": "number", "text": str(pair["number"])})
                right.append({"pair_index": index, "type": "word", "text": pair["word"]})
            elif mode == "Operasi hitung ↔ Hasil":
                left.append({"pair_index": index, "type": "question", "text": pair["question"]})
                right.append({"pair_index": index, "type": "answer", "text": pair["answer"]})
            else:
                raise ValueError(f"Mode matching tidak dikenal: {mode}")
        Random().shuffle(right)
        # Susun dua kolom: soal di kiri dan pasangan jawaban/ilustrasi di kanan.
        # Lingkaran di sisi dalam setiap kotak menjadi titik awal/akhir garis anak.
        return left + right

    @classmethod
    def export(cls, matching_data, output_path):
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        pdf = canvas.Canvas(str(output_path), pagesize=A4)
        page_w, page_h = A4
        title = matching_data.get("title", "Numerasi Matching Card")
        pdf.setFont("Helvetica-Bold", 17)
        pdf.drawCentredString(page_w / 2, page_h - 34, title[:70])

        cards = cls.build_cards(matching_data)
        margin_x, top, bottom = 34, 62, 34
        rows = max(1, min(6, (len(cards) + 1) // 2))
        row_gap = 13
        row_h = (page_h - top - bottom - row_gap * (rows - 1)) / rows
        box_w = page_w * 0.34
        box_h = row_h * 0.68
        left_x = margin_x
        right_x = page_w - margin_x - box_w
        circle_r = 5

        for i, card in enumerate(cards):
            col = 0 if i < rows else 1
            row = i if col == 0 else i - rows
            y_center = page_h - top - row * (row_h + row_gap) - row_h / 2
            x = left_x if col == 0 else right_x
            y = y_center - box_h / 2
            pdf.setLineWidth(1)
            pdf.roundRect(x, y, box_w, box_h, 7, stroke=1, fill=0)
            cls._draw_card(pdf, x, y, box_w, box_h, card)

            # Titik koneksi berada di sisi yang menghadap kolom pasangan.
            circle_x = x + box_w + 15 if col == 0 else x - 15
            pdf.circle(circle_x, y_center, circle_r, stroke=1, fill=0)

        pdf.save()
        return output_path

    @classmethod
    def _draw_card(cls, pdf, x, y, width, height, card):
        kind = card["type"]
        if kind == "quantity":
            count = max(1, min(int(card["quantity"]), 20))
            asset_path = OpenMojiAssetService.get_asset(card["asset"], "color")
            drawing = svg2rlg(str(asset_path))
            cols = min(5, count)
            rows = (count + cols - 1) // cols
            cell_w = (width - 16) / cols
            cell_h = (height - 16) / rows
            scale = min(cell_w / drawing.width, cell_h / drawing.height, 0.72)
            drawing.width *= scale
            drawing.height *= scale
            drawing.scale(scale, scale)
            for n in range(count):
                r, c = divmod(n, cols)
                cx = x + 8 + c * cell_w + (cell_w - drawing.width) / 2
                cy = y + height - 8 - (r + 1) * cell_h + (cell_h - drawing.height) / 2
                renderPDF.draw(drawing, pdf, cx, cy)
        else:
            text = str(card.get("text", ""))
            font_size = 30 if len(text) <= 8 else 21 if len(text) <= 18 else 15
            pdf.setFont("Helvetica-Bold", font_size)
            pdf.drawCentredString(x + width / 2, y + height / 2 - font_size / 3, text[:42])
