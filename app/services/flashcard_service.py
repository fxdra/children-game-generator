
from math import ceil

from app.services.openmoji_asset import OpenMojiAssetService

class NumberCardService:
    MIN_NUMBER = 1
    MAX_NUMBER = 50
    CARDS_PER_PAGE = 6
    MAX_COLUMNS = 10

    @classmethod
    def number_to_words(cls, number: int) -> str:
        if not cls.MIN_NUMBER <= number <= cls.MAX_NUMBER:
            raise ValueError(
                f"Angka harus antara {cls.MIN_NUMBER} "
                f"sampai {cls.MAX_NUMBER}."
            )

        words = {
            1: "satu",
            2: "dua",
            3: "tiga",
            4: "empat",
            5: "lima",
            6: "enam",
            7: "tujuh",
            8: "delapan",
            9: "sembilan",
            10: "sepuluh",
            11: "sebelas",
        }

        if number in words:
            return words[number]

        if number < 20:
            return (
                cls.number_to_words(number - 10)
                + " belas"
            )

        tens = (number // 10) * 10
        remainder = number % 10

        result = cls.number_to_words(tens // 10) + " puluh"

        if remainder:
            result += " " + cls.number_to_words(remainder)

        return result

    @classmethod
    def create_card(cls, number: int) -> dict:
        word = cls.number_to_words(number)

        columns = min(number, cls.MAX_COLUMNS)
        rows = ceil(number / columns)

        # Pilih asset berdasarkan nomor kartu.
        asset_names = list(OpenMojiAssetService.ASSETS.keys())
        asset_name = asset_names[(number - 1) % len(asset_names)]

        return {
            "number": number,
            "word": word,
            "quantity": number,
            "columns": columns,
            "rows": rows,
            "asset": asset_name,
        }

    @classmethod
    def create_cards(
        cls,
        start_number: int = 1,
        end_number: int = 50,
    ) -> list:
        if start_number < cls.MIN_NUMBER:
            raise ValueError("Angka awal minimal 1.")

        if end_number > cls.MAX_NUMBER:
            raise ValueError("Angka akhir maksimal 50.")

        if start_number > end_number:
            raise ValueError(
                "Angka awal tidak boleh lebih besar "
                "dari angka akhir."
            )

        return [
            cls.create_card(number)
            for number in range(
                start_number,
                end_number + 1,
            )
        ]

    @classmethod
    def create_pages(
        cls,
        start_number: int = 1,
        end_number: int = 50,
    ) -> list:
        cards = cls.create_cards(
            start_number,
            end_number,
        )

        pages = []

        for index in range(
            0,
            len(cards),
            cls.CARDS_PER_PAGE,
        ):
            pages.append(
                cards[index:index + cls.CARDS_PER_PAGE]
            )

        return pages
