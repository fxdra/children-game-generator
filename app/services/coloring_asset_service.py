
from pathlib import Path


class ColoringAssetService:
    BASE_DIR = (
        Path(__file__).resolve().parents[2]
        / "assets"
        / "coloring"
    )

    CATEGORIES = {
        "Animal": "animal",
        "Character": "character",
    }

    SUPPORTED_EXTENSIONS = {
        ".svg",
        ".jpg",
        ".jpeg",
        ".png",
    }

    @classmethod
    def get_categories(cls):
        return list(cls.CATEGORIES.keys())

    @classmethod
    def get_assets(cls, category: str):
        folder_name = cls.CATEGORIES.get(category)

        if not folder_name:
            raise ValueError(
                f"Kategori tidak dikenal: {category}"
            )

        category_dir = cls.BASE_DIR / folder_name

        if not category_dir.exists():
            return []

        assets = []

        for path in sorted(category_dir.iterdir()):
            if (
                path.is_file()
                and path.suffix.lower()
                in cls.SUPPORTED_EXTENSIONS
            ):
                assets.append({
                    "name": path.stem,
                    "filename": path.name,
                    "category": category,
                    "path": path,
                })

        return assets

    @classmethod
    def get_asset_path(cls, category: str, filename: str):
        folder_name = cls.CATEGORIES.get(category)

        if not folder_name:
            raise ValueError(
                f"Kategori tidak dikenal: {category}"
            )

        asset_path = (
            cls.BASE_DIR
            / folder_name
            / filename
        ).resolve()

        category_dir = (
            cls.BASE_DIR / folder_name
        ).resolve()

        if category_dir not in asset_path.parents:
            raise ValueError("Path aset tidak valid.")

        if not asset_path.is_file():
            raise FileNotFoundError(
                f"Aset tidak ditemukan: {filename}"
            )

        if asset_path.suffix.lower() not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(
                "Format aset tidak didukung."
            )

        return asset_path
