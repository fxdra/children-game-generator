from functools import lru_cache
from pathlib import Path


class OpenMojiAssetService:
    """Resolve OpenMoji paths and cache the asset index in memory."""

    BASE_DIR = Path(__file__).resolve().parents[2] / "assets" / "openmoji"
    COLOR_DIR = BASE_DIR / "color" / "svg"
    BLACK_DIR = BASE_DIR / "black" / "svg"

    ASSETS = {
        "apple": "1F34E.svg",
        "banana": "1F34C.svg",
        "cat": "1F408.svg",
        "dog": "1F415.svg",
    }

    # The index is shared by every picker instance. It is invalidated if the
    # asset directory changes while the application is running.
    _asset_index_cache = None
    _asset_index_signature = None

    @classmethod
    def get_asset(cls, name: str, variant: str = "color") -> Path:
        base_dir = cls.BLACK_DIR if variant == "black" else cls.COLOR_DIR
        filename = cls.ASSETS.get(name)
        if filename is None:
            filename = name if name.lower().endswith(".svg") else f"{name}.svg"

        asset_path = base_dir / filename
        if not asset_path.is_file():
            raise FileNotFoundError(f"File OpenMoji tidak ditemukan: {asset_path}")
        return asset_path

    @classmethod
    def get_all_assets(cls):
        """Return cached metadata; no SVG is parsed or rendered here."""
        directory = cls.COLOR_DIR
        if not directory.exists():
            cls._asset_index_cache = []
            cls._asset_index_signature = None
            return cls._asset_index_cache

        try:
            stat = directory.stat()
            signature = (stat.st_mtime_ns, stat.st_ino)
        except OSError:
            signature = None

        if cls._asset_index_cache is None or signature != cls._asset_index_signature:
            assets = [
                {
                    "name": path.stem,
                    "filename": path.name,
                    "path": path,
                }
                for path in sorted(directory.glob("*.svg"), key=lambda item: item.name)
            ]
            cls._asset_index_cache = assets
            cls._asset_index_signature = signature

        # Return the same metadata objects in a new list so callers cannot
        # accidentally append/remove entries from the shared cache.
        return list(cls._asset_index_cache)

    @classmethod
    def clear_asset_index_cache(cls):
        cls._asset_index_cache = None
        cls._asset_index_signature = None
