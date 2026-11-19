
from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from app.repositories import ContentRepository
from .maze_graph_processor import Maze, MazeOptions


class ContentService:
    """Validates, normalizes, and persists activity-specific content."""

    RUNTIME_ONLY_FIELDS = {"maze_generator"}

    NODE_DIRECTIONS = (
        "north", "east", "south", "west",
        "north2", "east2", "south2", "west2",
    )

    def __init__(self, repository: ContentRepository | None = None):
        self.repository = repository or ContentRepository()

    # ==========================================================
    # MAZE SERIALIZATION
    # ==========================================================

    @staticmethod
    def _node_id(node) -> str:
        cell = node.cell
        layer = "lower" if node is cell.lower else "upper"
        return f"{cell.x},{cell.y},{layer}"

    @classmethod
    def _serialize_maze(cls, maze: Maze) -> dict[str, Any]:
        """Mengubah graph Maze menjadi struktur yang aman disimpan sebagai JSON."""

        nodes = {}

        for node in maze.all_nodes():
            node_id = cls._node_id(node)

            nodes[node_id] = {
                direction: (
                    cls._node_id(getattr(node, direction))
                    if getattr(node, direction) is not None
                    else None
                )
                for direction in cls.NODE_DIRECTIONS
            }

        return {
            "__type": "maze",
            "version": 1,
            "width": maze.width,
            "height": maze.height,
            "cells": [
                [cell.white for cell in row]
                for row in maze.cells
            ],
            "nodes": nodes,
            "solution": [
                cls._node_id(node)
                for node in maze.solution
            ],
            "start": (
                cls._node_id(maze.start)
                if maze.start is not None
                else None
            ),
            "finish": (
                cls._node_id(maze.finish)
                if maze.finish is not None
                else None
            ),
            "loop_count": maze.loop_count,
            "cross_count": maze.cross_count,
        }

    @classmethod
    def restore_maze(cls, data: dict[str, Any]) -> Maze:
        """Merekonstruksi graph Maze dari data hasil _serialize_maze()."""

        if not isinstance(data, dict) or data.get("__type") != "maze":
            raise ValueError("Data bukan hasil serialisasi Maze.")

        if data.get("version") != 1:
            raise ValueError("Versi data Maze tidak didukung.")

        width = int(data["width"])
        height = int(data["height"])
        cells_mask = data["cells"]

        if len(cells_mask) != height:
            raise ValueError("Jumlah baris cells tidak sesuai dengan height.")

        if any(len(row) != width for row in cells_mask):
            raise ValueError("Lebar cells tidak konsisten.")

        maze = Maze(
            MazeOptions(
                width=width,
                height=height,
                mask=cells_mask,
            )
        )

        # Buat lookup seluruh node berdasarkan koordinat dan layer.
        node_lookup = {
            cls._node_id(node): node
            for node in maze.all_nodes()
        }

        serialized_nodes = data["nodes"]

        # Pastikan struktur node yang disimpan sesuai dengan maze.
        if set(serialized_nodes) != set(node_lookup):
            raise ValueError("Struktur node pada data Maze tidak lengkap.")

        # Hubungkan kembali seluruh koneksi graph.
        for node_id, connections in serialized_nodes.items():
            node = node_lookup[node_id]

            for direction in cls.NODE_DIRECTIONS:
                target_id = connections.get(direction)

                if target_id is None:
                    setattr(node, direction, None)
                    continue

                target = node_lookup.get(target_id)

                if target is None:
                    raise ValueError(
                        f"Koneksi Maze mengarah ke node tidak dikenal: {target_id}"
                    )

                setattr(node, direction, target)

            # Metadata ini hanya dipakai saat proses pembentukan maze.
            node.visited_by = None
            node.region = -1

        # Pulihkan jalur solusi dan titik awal/akhir.
        try:
            maze.solution = [
                node_lookup[node_id]
                for node_id in data.get("solution", [])
            ]

            start_id = data.get("start")
            finish_id = data.get("finish")

            maze.start = node_lookup[start_id] if start_id else None
            maze.finish = node_lookup[finish_id] if finish_id else None

        except KeyError as error:
            raise ValueError(
                f"Referensi node Maze tidak ditemukan: {error}"
            ) from error

        maze.loop_count = int(data.get("loop_count", 0))
        maze.cross_count = int(data.get("cross_count", 0))

        return maze

    # ==========================================================
    # CONTENT NORMALIZATION
    # ==========================================================

    @classmethod
    def _normalize(cls, value: Any) -> Any:

        # Maze harus ditangani sebelum pemeriksaan tipe lainnya.
        if isinstance(value, Maze):
            return cls._serialize_maze(value)

        if is_dataclass(value) and not isinstance(value, type):
            return cls._normalize(asdict(value))

        if isinstance(value, Path):
            return str(value)

        if isinstance(value, dict):
            return {
                str(key): cls._normalize(item)
                for key, item in value.items()
                if key not in cls.RUNTIME_ONLY_FIELDS
            }

        if isinstance(value, (list, tuple)):
            return [
                cls._normalize(item)
                for item in value
            ]

        if value is None or isinstance(value, (str, int, float, bool)):
            return value

        raise TypeError(
            f"Tipe data {type(value).__name__} "
            "tidak dapat disimpan ke content library."
        )

    # ==========================================================
    # CONTENT LIBRARY
    # ==========================================================

    def create_custom_content(
        self,
        payload: dict[str, Any],
    ) -> tuple[dict[str, Any], bool]:

        if not isinstance(payload, dict):
            raise ValueError("Konten harus berupa dict.")

        title = str(
            payload.get("activity_title")
            or payload.get("title")
            or ""
        ).strip()

        category = str(payload.get("category") or "").strip()
        activity_type = str(payload.get("activity_type") or "").strip()

        if not title:
            raise ValueError("Judul aktivitas wajib diisi.")

        if not category or not activity_type:
            raise ValueError(
                "Kategori dan jenis aktivitas wajib diisi."
            )

        normalized_payload = self._normalize(payload)

        canonical = json.dumps(
            normalized_payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )

        fingerprint = hashlib.sha256(
            canonical.encode("utf-8")
        ).hexdigest()

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

    def list_content(
        self,
        category: str | None = None,
        activity_type: str | None = None,
    ):
        return self.repository.list_items(
            category=category,
            activity_type=activity_type,
        )

    def get_content(self, content_id: str):
        return self.repository.get(content_id)
