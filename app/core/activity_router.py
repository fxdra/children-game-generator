
from app.core.skill_mapping import SKILL_MAPPING


class ActivityRouter:
    """
    Mengelola routing berdasarkan kombinasi kategori
    dan jenis aktivitas.
    """

    CATEGORY_HANDLERS = {
        "Numerasi": "_handle_numerasi",
        "Bahasa": "_handle_bahasa",
        "Warna": "_handle_warna",
        "Bentuk": "_handle_bentuk",
        "Hewan": "_handle_hewan",
        "Motorik": "_handle_motorik",
        "Puzzle": "_handle_puzzle",
        "Aktivitas Dunia Nyata": "_handle_aktivitas_dunia_nyata",
    }

    def __init__(self):
        self.categories = SKILL_MAPPING

    def get_categories(self):
        """Mengembalikan seluruh kategori yang tersedia."""
        return list(self.categories.keys())

    def get_activities(self, category: str):
        """Mengembalikan aktivitas berdasarkan kategori."""
        category_data = self.categories.get(category)

        if category_data is None:
            return []

        return list(category_data.keys())

    def resolve(self, category: str, activity_type: str):
        """
        Memvalidasi kategori dan aktivitas,
        lalu mengembalikan informasi routing.
        """

        if category not in self.categories:
            return {
                "valid": False,
                "reason": "unknown_category",
                "category": category,
                "activity_type": activity_type,
                "handler": None,
            }

        if activity_type not in self.categories[category]:
            return {
                "valid": False,
                "reason": "unknown_activity",
                "category": category,
                "activity_type": activity_type,
                "handler": None,
            }

        handler = self.CATEGORY_HANDLERS.get(category)

        return {
            "valid": True,
            "reason": None,
            "category": category,
            "activity_type": activity_type,
            "handler": handler,
            "route": f"{category}:{activity_type}",
        }
