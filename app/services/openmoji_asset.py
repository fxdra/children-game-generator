from pathlib import Path

class OpenMojiAssetService:

    BASE_DIR = (
        Path(__file__).resolve().parents[2]
        / "assets"
        / "openmoji"
    )

    COLOR_DIR = BASE_DIR / "color" / "svg"
    BLACK_DIR = BASE_DIR / "black" / "svg"

    # Asset yang sudah kita kenal untuk tahap awal.
    ASSETS = {
        "apple": "1F34E.svg",
        "banana": "1F34C.svg",
        "cat": "1F408.svg",
        "dog": "1F415.svg",
    }

    @classmethod
    def get_asset(
        cls,
        name: str,
        variant: str = "color",
    ) -> Path:
        if name not in cls.ASSETS:
            raise ValueError(
                f"Asset OpenMoji '{name}' belum tersedia."
            )

        if variant == "black":
            base_dir = cls.BLACK_DIR
        else:
            base_dir = cls.COLOR_DIR

        asset_path = (
            base_dir / cls.ASSETS[name]
        )

        if not asset_path.exists():
            raise FileNotFoundError(
                f"File OpenMoji tidak ditemukan: "
                f"{asset_path}"
            )

        return asset_path

    @classmethod
    def get_all_assets(cls):
        assets = []

        if not cls.COLOR_DIR.exists():
            return assets

        for asset_path in sorted(
            cls.COLOR_DIR.glob("*.svg")
        ):
            assets.append({
                "name": asset_path.stem,
                "filename": asset_path.name,
                "path": asset_path,
            })

        return assets