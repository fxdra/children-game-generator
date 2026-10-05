from pathlib import Path
from random import Random

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF

from app.services.openmoji_asset import OpenMojiAssetService


class MatchingCardPDFService:

    @classmethod
    def export(
        cls,
        matching_data: dict,
        output_path: str | Path,
    ):
        output_path = Path(
            output_path
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        pdf = canvas.Canvas(
            str(output_path),
            pagesize=A4,
        )

        page_width, page_height = A4

        # =========================
        # DATA
        # =========================

        title = matching_data.get(
            "title",
            "Matching Card",
        )

        mode = matching_data.get(
            "matching_mode",
            "Gambar ↔ Kata",
        )

        pairs = matching_data.get(
            "pairs",
            [],
        )

        cards = cls._build_cards(
            pairs,
            mode,
        )

        # =========================
        # PAGE
        # =========================

        margin_x = 50
        margin_top = 45
        margin_bottom = 45

        title_height = 35

        grid_top = (
            page_height
            - margin_top
            - title_height
        )

        grid_bottom = margin_bottom

        horizontal_gap = 18
        vertical_gap = 12

        columns = 2
        rows = 6

        card_width = (
            page_width
            - (margin_x * 2)
            - horizontal_gap
        ) / columns

        card_height = (
            grid_top
            - grid_bottom
            - (
                vertical_gap
                * (rows - 1)
            )
        ) / rows

        # =========================
        # TITLE
        # =========================

        pdf.setFont(
            "Helvetica-Bold",
            18,
        )

        pdf.drawCentredString(
            page_width / 2,
            page_height - 35,
            title,
        )

        # =========================
        # CARDS
        # =========================

        for index, card in enumerate(
            cards
        ):
            row = index // columns
            column = index % columns

            x = (
                margin_x
                + column
                * (
                    card_width
                    + horizontal_gap
                )
            )

            y = (
                grid_top
                - (
                    row + 1
                ) * card_height
                - (
                    row
                    * vertical_gap
                )
            )

            cls._draw_card(
                pdf,
                x,
                y,
                card_width,
                card_height,
                card,
            )

        pdf.save()

        return output_path

    @classmethod
    def _build_cards(
        cls,
        pairs: list,
        mode: str,
    ):
        randomizer = Random()

        # =========================
        # GAMBAR ↔ GAMBAR
        # =========================

        if mode == "Gambar ↔ Gambar":

            left_cards = []
            right_cards = []

            for pair_index, pair in enumerate(
                pairs,
                start=1,
            ):
                left_cards.append(
                    {
                        "pair_index": pair_index,
                        "type": "image",
                        "asset": pair[
                            "asset"
                        ],
                    }
                )

                right_cards.append(
                    {
                        "pair_index": pair_index,
                        "type": "image",
                        "asset": pair[
                            "match_asset"
                        ],
                    }
                )

            randomizer.shuffle(
                right_cards
            )

            cards = []

            for left_card, right_card in zip(
                left_cards,
                right_cards,
            ):
                cards.append(
                    left_card
                )

                cards.append(
                    right_card
                )

            return cards

        # =========================
        # GAMBAR ↔ KATA
        # =========================

        words = [
            pair["word"]
            for pair in pairs
        ]

        randomizer.shuffle(
            words
        )

        cards = []

        for pair_index, pair in enumerate(
            pairs,
            start=1,
        ):
            cards.append(
                {
                    "pair_index": pair_index,
                    "type": "image",
                    "asset": pair[
                        "asset"
                    ],
                }
            )

            cards.append(
                {
                    "pair_index": pair_index,
                    "type": "word",
                    "word": words[
                        pair_index - 1
                    ],
                }
            )

        return cards

    @classmethod
    def _draw_card(
        cls,
        pdf,
        x,
        y,
        width,
        height,
        card,
    ):
        # =========================
        # CARD BORDER
        # =========================

        pdf.setLineWidth(
            1.2
        )

        pdf.roundRect(
            x,
            y,
            width,
            height,
            8,
            stroke=1,
            fill=0,
        )

        # =========================
        # IMAGE CARD
        # =========================

        if card["type"] == "image":
            cls._draw_asset(
                pdf,
                card["asset"],
                x,
                y,
                width,
                height,
            )

        # =========================
        # WORD CARD
        # =========================

        else:
            word = card.get(
                "word",
                "",
            )

            pdf.setFont(
                "Helvetica-Bold",
                20,
            )

            pdf.drawCentredString(
                x + width / 2,
                y + height / 2 - 7,
                word,
            )

    @classmethod
    def _draw_asset(
        cls,
        pdf,
        asset_name,
        x,
        y,
        width,
        height,
    ):
        asset_path = (
            OpenMojiAssetService.get_asset(
                asset_name,
                "color",
            )
        )

        drawing = svg2rlg(
            str(asset_path)
        )

        if drawing is None:
            return

        max_size = min(
            width * 0.55,
            height * 0.55,
        )

        original_width = drawing.width
        original_height = drawing.height

        if not original_width or not original_height:
            return

        scale = min(
            max_size / original_width,
            max_size / original_height,
        )

        drawing.width = (
            original_width * scale
        )

        drawing.height = (
            original_height * scale
        )

        drawing.scale(
            scale,
            scale,
        )

        draw_x = (
            x
            + (
                width
                - drawing.width
            ) / 2
        )

        draw_y = (
            y
            + (
                height
                - drawing.height
            ) / 2
        )

        renderPDF.draw(
            drawing,
            pdf,
            draw_x,
            draw_y,
        )