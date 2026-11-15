"""Application service for the shared GameAnak content library."""
from __future__ import annotations

import hashlib
import json
import uuid
from pathlib import Path
from typing import Any

from app.repositories import ContentRepository


class ContentService:
    """Validates, normalizes, and persists activity-specific content."""

    RUNTIME_ONLY_FIELDS = {"maze_generator"}

    def __init__(self, repository: ContentRepository | None = None):
        self.repository = repository or ContentRepository()

    @classmethod
    def _normalize(cls, value: Any) -> Any:
        if isinstance(value, Path):
            return str(value)
        if isinstance(value, dict):
            return {
                str(key): cls._normalize(item)
                for key, item in value.items()
                if key not in cls.RUNTIME_ONLY_FIELDS
            }
        if isinstance(value, (list, tuple)):
            return [cls._normalize(item) for item in value]
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        raise TypeError(
            f"Tipe data {type(value).__name__} tidak dapat disimpan ke content library."
        )

    def create_custom_content(self, payload: dict[str, Any]) -> tuple[dict[str, Any], bool]:
        if not isinstance(payload, dict):
            raise ValueError("Konten harus berupa dict.")
        title = str(payload.get("activity_title") or payload.get("title") or "").strip()
        category = str(payload.get("category") or "").strip()
        activity_type = str(payload.get("activity_type") or "").strip()
        if not title:
            raise ValueError("Judul aktivitas wajib diisi.")
        if not category or not activity_type:
            raise ValueError("Kategori dan jenis aktivitas wajib diisi.")

        normalized_payload = self._normalize(payload)
        canonical = json.dumps(
            normalized_payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        fingerprint = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

        existing = self.repository.find_by_fingerprint(fingerprint)
        if existing:
            return existing, False

        record = {
            "id": str(uuid.uuid4()),
            "title": title,
            "category": category,
            "activity_type": activity_type,
            "age": str(payload.get("age") or ""),
            "payload": normalized_payload,
            "fingerprint": fingerprint,
            "status": "active",
            "source": "custom",
        }
        return self.repository.save(record), True

    def list_content(self, category: str | None = None, activity_type: str | None = None):
        return self.repository.list_items(category=category, activity_type=activity_type)

    def get_content(self, content_id: str):
        return self.repository.get(content_id)
