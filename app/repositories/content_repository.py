"""Persistent JSON repository for GameAnak activity content."""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ContentRepository:
    """Stores activity-specific payloads in one shared JSON library."""

    def __init__(self, file_path: str | Path | None = None):
        project_root = Path(__file__).resolve().parents[2]
        self.file_path = Path(file_path) if file_path else project_root / "data" / "content_library.json"
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._write({"version": 1, "items": []})

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat(timespec="seconds")

    def _read(self) -> dict[str, Any]:
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except json.JSONDecodeError as error:
            raise ValueError(f"File library JSON rusak: {error}") from error

        if not isinstance(data, dict) or not isinstance(data.get("items"), list):
            raise ValueError("Struktur content library tidak valid.")
        return data

    def _write(self, data: dict[str, Any]) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(
            prefix=f".{self.file_path.name}.",
            suffix=".tmp",
            dir=str(self.file_path.parent),
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(data, handle, ensure_ascii=False, indent=2)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, self.file_path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)

    def list_items(
        self,
        category: str | None = None,
        activity_type: str | None = None,
        include_archived: bool = False,
    ) -> list[dict[str, Any]]:
        items = self._read()["items"]
        result = []
        for item in items:
            if not include_archived and item.get("status", "active") != "active":
                continue
            if category and item.get("category") != category:
                continue
            if activity_type and item.get("activity_type") != activity_type:
                continue
            result.append(item)
        return sorted(result, key=lambda item: item.get("updated_at", ""), reverse=True)

    def get(self, content_id: str) -> dict[str, Any] | None:
        for item in self._read()["items"]:
            if item.get("id") == content_id:
                return item
        return None

    def find_by_fingerprint(self, fingerprint: str) -> dict[str, Any] | None:
        for item in self._read()["items"]:
            if item.get("fingerprint") == fingerprint and item.get("status", "active") == "active":
                return item
        return None

    def save(self, item: dict[str, Any]) -> dict[str, Any]:
        required = ("id", "title", "category", "activity_type", "payload", "fingerprint")
        missing = [key for key in required if key not in item]
        if missing:
            raise ValueError(f"Field content belum lengkap: {', '.join(missing)}")
        if not isinstance(item["payload"], dict):
            raise ValueError("Payload harus berupa object/dict.")

        data = self._read()
        now = self._now()
        existing_index = next(
            (index for index, current in enumerate(data["items"]) if current.get("id") == item["id"]),
            None,
        )
        saved = dict(item)
        saved["updated_at"] = now
        if existing_index is None:
            saved["created_at"] = saved.get("created_at", now)
            saved["status"] = saved.get("status", "active")
            data["items"].append(saved)
        else:
            saved["created_at"] = data["items"][existing_index].get("created_at", now)
            saved["status"] = data["items"][existing_index].get("status", "active")
            data["items"][existing_index] = saved
        self._write(data)
        return saved

    def archive(self, content_id: str) -> bool:
        data = self._read()
        for item in data["items"]:
            if item.get("id") == content_id:
                item["status"] = "archived"
                item["updated_at"] = self._now()
                self._write(data)
                return True
        return False

    def delete(self, content_id: str) -> bool:
        data = self._read()
        original_count = len(data["items"])
        data["items"] = [item for item in data["items"] if item.get("id") != content_id]
        if len(data["items"]) == original_count:
            return False
        self._write(data)
        return True
