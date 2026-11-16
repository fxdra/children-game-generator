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
        "star": "2B50.svg",
        "spark": "2728.svg",
        "jellyfish": "1FABC.svg",
        "coin": "1FA99.svg",
        "rocket": "1F680.svg",
        "crown": "1F451.svg",
        "fish": "1F41F.svg",
        "car": "1F697.svg",
        "train": "1F686.svg",
        "airplane": "2708.svg",
        "helicopter": "1F681.svg",
        "bus": "1F68C.svg",
        "bicycle": "1F6B2.svg",
        "motorcycle": "1F3CD.svg",
        "basketball": "1F3C0.svg",
        "soccer": "26BD.svg",
        "tennis": "1F3BE.svg",
        "rugby": "1F3C8.svg",
        "volleyball": "1F3D0.svg",
        "baseball": "26BE.svg",
        "golf": "26F3.svg",
        "bowling": "1F3B3.svg",
        "pingpong": "1F3D3.svg",
        "skateboard": "1F6F9.svg",
        "ski": "1F3BF.svg",
        "snowboard": "1F3C2.svg",
        "swimming": "1F3CA.svg",
        "weightlifting": "1F3CB.svg",
        "boxing": "1F94A.svg",
        "karate": "1F94B.svg",
        "fencing": "1F93A.svg",
        "archery": "1F3F9.svg",
        "horse": "1F40E.svg",
        "elephant": "1F418.svg",
        "giraffe": "1F992.svg",
        "monkey": "1F412.svg",
        "panda": "1F43C.svg",
        "penguin": "1F427.svg",
        "tiger": "1F42F.svg",
        "lion": "1F981.svg",
        "bear": "1F43B.svg",
        "rabbit": "1F407.svg",
        "frog": "1F438.svg",
        "snake": "1F40D.svg",
        "turtle": "1F422.svg",
        "octopus": "1F419.svg",
        "crab": "1F980.svg",
        "lobster": "1F99E.svg",
        "shrimp": "1F990.svg",
        "snail": "1F40C.svg",
        "butterfly": "1F98B.svg",
        "bee": "1F41D.svg",
        "ladybug": "1F41E.svg",
        "ant": "1F41C.svg",
        "spider": "1F577.svg",
        "scorpion": "1F982.svg",
        "caterpillar": "1F41B.svg",
        "dragon": "1F409.svg",
        "unicorn": "1F984.svg",
        "mermaid": "1F9DC.svg",
        "fairy": "1F9DA.svg",
        "wizard": "1F9D9.svg",
        "witch": "1F9DB.svg",
        "vampire": "1F9DB-200D-2642-FE0F.svg",
        "zombie": "1F9DF.svg",
        "alien": "1F47D.svg",
        "robot": "1F916.svg",
        "ghost": "1F47B.svg",
        "skull": "1F480.svg",
        "skeleton": "1F9B4.svg",
        "mushroom": "1F344.svg",
        "cactus": "1F335.svg",
        "tree": "1F333.svg",
        "palm_tree": "1F334.svg",
        "sunflower": "1F33B.svg",
        "rose": "1F339.svg",
        "tulip": "1F337.svg",
        "cherry_blossom": "1F338.svg",
        "hibiscus": "1F33A.svg",
        "maple_leaf": "1F341.svg",
        "fallen_leaf": "1F342.svg",
        "herb": "1F33F.svg",
        "shamrock": "2618.svg",
        "four_leaf_clover": "1F340.svg",
        "bamboo": "1F38D.svg",
        "coconut": "1F965.svg",
        "banana": "1F34C.svg",
        "grapes": "1F347.svg",
        "watermelon": "1F349.svg",
        "strawberry": "1F353.svg",
        "kiwi": "1F95D.svg",
        "pineapple": "1F34D.svg",
        "mango": "1F96D.svg",
        "papaya": "1F34E-1F34D.svg",
        "avocado": "1F951.svg",
        "peach": "1F351.svg",
        "plum": "1F350.svg",
        "pomegranate": "1F34D.svg",
        "lemon": "1F34B.svg",
        "lime": "1F34B-200D-1F7E9.svg",
        "cucumber": "1F952.svg",
        "tomato": "1F345.svg",
        "carrot": "1F955.svg",
        "corn": "1F33D.svg",
        "potato": "1F954.svg",
        "onion": "1F9C5.svg",
        "garlic": "1F9C4.svg",
        "pepper": "1F336.svg",
        "broccoli": "1F966.svg",
        "eggplant": "1F346.svg",
    }

    @classmethod
    def get_asset(
        cls,
        name: str,
        variant: str = "color",
    ) -> Path:

        if variant == "black":
            base_dir = cls.BLACK_DIR
        else:
            base_dir = cls.COLOR_DIR

        # Asset lama yang mempunyai nama alias.
        if name in cls.ASSETS:
            filename = cls.ASSETS[name]

        # Asset yang dipilih langsung dari Asset Picker.
        else:
            filename = (
                f"{name}.svg"
                if not name.lower().endswith(".svg")
                else name
            )

        asset_path = base_dir / filename

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