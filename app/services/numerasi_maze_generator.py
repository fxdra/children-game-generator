
from __future__ import annotations

import math
import random
from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class DecoyBranch:
    route_points: tuple[tuple[float, float], ...]
    numbers: tuple[tuple[float, float, int], ...]


@dataclass(frozen=True)
class NumerasiMaze:
    rows: int
    columns: int
    subtype: str
    cells: tuple[tuple[str, ...], ...]
    path: tuple[tuple[int, int], ...]
    instruction: str
    route_points: tuple[tuple[float, float], ...] = ()
    number_positions: tuple[tuple[float, float], ...] = ()
    decoy_branches: tuple[DecoyBranch, ...] = ()
    route_segments: tuple[tuple[tuple[float, float], ...], ...] = ()
    bridge_crossings: tuple[tuple[float, float], ...] = ()
    # (x, y, value, is_target): target labels and decoys placed along one road.
    number_labels: tuple[tuple[float, float, int, bool], ...] = ()
    road_width: float = 112.0


class NumerasiMazeGenerator:
    SUBTYPES = ("Number Path", "Math Equation", "Number Pattern")

    PRESETS = {
        "Mudah": (7, 7, 10),
        "Sedang": (9, 9, 15),
        "Sulit": (11, 11, 20),
    }

    # Grid grows with difficulty; renderer scales the road width accordingly.
    NUMBER_PATH_GRIDS = {"Mudah": 7, "Sedang": 8, "Sulit": 9}
    NUMBER_PATH_ROAD_WIDTHS = {"Mudah": 112.0, "Sedang": 94.0, "Sulit": 78.0}

    NUMBER_PATH_X_MIN = 110
    NUMBER_PATH_X_MAX = 690
    NUMBER_PATH_Y_MIN = 160
    NUMBER_PATH_Y_MAX = 840

    ROAD_CLEARANCE = 1
    CURVE_STEPS = 12
    MAX_ATTEMPTS = 250

    BRANCH_COUNTS = {
        "Mudah": 1,
        "Sedang": 2,
        "Sulit": 3,
    }

    WEAVE_COUNTS = {
        "Mudah": 0,
        "Sedang": 1,
        "Sulit": 2,
    }

    def __init__(
        self,
        subtype: str,
        difficulty: str = "Mudah",
        seed: int | None = None,
    ):
        if subtype not in self.SUBTYPES:
            raise ValueError(f"Subtype tidak dikenal: {subtype}")

        if difficulty not in self.PRESETS:
            difficulty = "Mudah"

        self.subtype = subtype
        self.difficulty = difficulty
        self.random = random.Random(seed)

    def generate(self) -> NumerasiMaze:
        rows, columns, target = self.PRESETS[self.difficulty]

        if self.subtype == "Number Path":
            return self._generate_number_path(target)

        path = self._make_path(rows, columns, target)
        values = [
            [self._decoy_value() for _ in range(columns)]
            for _ in range(rows)
        ]

        for index, (row, column) in enumerate(path, start=1):
            values[row][column] = self._path_value(index)

        return NumerasiMaze(
            rows=rows,
            columns=columns,
            subtype=self.subtype,
            cells=tuple(tuple(str(v) for v in line) for line in values),
            path=tuple(path),
            instruction=self._instruction(),
        )

    # ---------------------------------------------------------
    # NUMBER PATH
    # ---------------------------------------------------------

    def _generate_number_path(self, target: int) -> NumerasiMaze:
        size = self.NUMBER_PATH_GRIDS[self.difficulty]

        decoy_count = {"Mudah": 3, "Sedang": 5, "Sulit": 8}[self.difficulty]
        total_labels = target + decoy_count

        # Satu jalur kontinu. Setiap titik grid menjadi anchor label,
        # sehingga angka juga tersebar pada area belokan.
        # Reserve the first and last anchors for START and FINISH.
        main_path = self._generate_main_path(size, total_labels + 2)
        main_coordinates = self._grid_to_coordinates(main_path, size)
        main_smooth = self._smooth_bezier_path(main_coordinates)
        label_coordinates = main_coordinates[1:-1]

        decoy_values = [
            self.random.randint(1, target)
            for _ in range(decoy_count)
        ]
        labels = [(value, True) for value in range(1, target + 1)]
        labels.extend((value, False) for value in decoy_values)
        self.random.shuffle(labels)

        number_labels = tuple(
            (x, y, value, is_target)
            for (x, y), (value, is_target)
            in zip(label_coordinates, labels)
        )

        # Backward compatibility: consumers of number_positions still
        # receive the same coordinate-only structure.
        number_positions = tuple((x, y) for x, y, _, _ in number_labels)

        return NumerasiMaze(
            rows=size,
            columns=size,
            subtype=self.subtype,
            cells=(),
            path=tuple(main_path),
            instruction=self._instruction(),
            route_points=tuple(main_smooth),
            number_positions=number_positions,
            decoy_branches=(),
            route_segments=(tuple(main_smooth),),
            bridge_crossings=(),
            number_labels=number_labels,
            road_width=self.NUMBER_PATH_ROAD_WIDTHS[self.difficulty],
        )

    def _generate_main_path(
        self,
        size: int,
        target: int,
    ) -> list[tuple[int, int]]:
        """Self-avoiding recursive backtracking path."""

        for _ in range(self.MAX_ATTEMPTS):
            start = (
                self.random.randrange(1, size - 1),
                self.random.randrange(1, size - 1),
            )

            path = [start]
            visited = {start}

            def extend() -> bool:
                if len(path) >= target:
                    return True

                row, column = path[-1]

                neighbors = [
                    (row - 1, column),
                    (row + 1, column),
                    (row, column - 1),
                    (row, column + 1),
                ]
                self.random.shuffle(neighbors)

                for point in neighbors:
                    r, c = point

                    if not (0 <= r < size and 0 <= c < size):
                        continue

                    if point in visited:
                        continue

                    # Hindari menempel pada jalur lama selain ruas terakhir.
                    if self._too_close_to_old_path(point, path):
                        continue

                    visited.add(point)
                    path.append(point)

                    if extend():
                        return True

                    path.pop()
                    visited.remove(point)

                return False

            if extend():
                return path

        # Fallback: tetap menghasilkan jalur valid tanpa clearance tambahan.
        return self._generate_fallback_path(size, target)

    @staticmethod
    def _too_close_to_old_path(
        point: tuple[int, int],
        path: list[tuple[int, int]],
    ) -> bool:
        r, c = point

        for old_r, old_c in path[:-2]:
            if max(abs(r - old_r), abs(c - old_c)) <= 1:
                return True

        return False

    def _generate_fallback_path(
        self,
        size: int,
        target: int,
    ) -> list[tuple[int, int]]:
        for _ in range(self.MAX_ATTEMPTS):
            start = (
                self.random.randrange(size),
                self.random.randrange(size),
            )
            path = [start]
            visited = {start}

            def extend() -> bool:
                if len(path) == target:
                    return True

                r, c = path[-1]
                neighbors = [
                    (r - 1, c),
                    (r + 1, c),
                    (r, c - 1),
                    (r, c + 1),
                ]
                self.random.shuffle(neighbors)

                for point in neighbors:
                    nr, nc = point

                    if not (0 <= nr < size and 0 <= nc < size):
                        continue
                    if point in visited:
                        continue

                    visited.add(point)
                    path.append(point)

                    if extend():
                        return True

                    path.pop()
                    visited.remove(point)

                return False

            if extend():
                return path

        raise RuntimeError("Gagal membentuk jalur Number Path.")

    # ---------------------------------------------------------
    # BRAID BRANCHES
    # ---------------------------------------------------------

    def _generate_braid_branches(
        self,
        main_path: list[tuple[int, int]],
        size: int,
        target: int,
    ) -> list[DecoyBranch]:
        """
        Membuat jalur alternatif yang benar-benar terhubung
        ke dua titik jalur utama.
        """

        branches = []
        occupied = set(main_path)

        desired = self.BRANCH_COUNTS[self.difficulty]
        candidates = list(range(1, len(main_path) - 3))
        self.random.shuffle(candidates)

        for start_index in candidates:
            if len(branches) >= desired:
                break

            end_index = min(
                len(main_path) - 1,
                start_index + self.random.randint(3, 5),
            )

            start = main_path[start_index]
            end = main_path[end_index]

            branch_grid = self._find_branch_path(
                start,
                end,
                size,
                occupied,
            )

            if not branch_grid or len(branch_grid) < 4:
                continue

            occupied.update(branch_grid[1:-1])

            coords = self._grid_to_coordinates(branch_grid, size)
            smooth = self._smooth_bezier_path(coords)

            number_count = min(2, max(1, len(branch_grid) - 2))
            samples = self._resample_route(smooth, number_count + 2)[1:-1]

            wrong_numbers = []
            for x, y in samples:
                wrong = max(
                    1,
                    min(
                        target,
                        start_index + self.random.choice([-1, 2, 3]),
                    ),
                )
                wrong_numbers.append((x, y, wrong))

            branches.append(
                DecoyBranch(
                    route_points=tuple(smooth),
                    numbers=tuple(wrong_numbers),
                )
            )

        return branches

    def _find_branch_path(
        self,
        start: tuple[int, int],
        end: tuple[int, int],
        size: int,
        occupied: set[tuple[int, int]],
    ) -> list[tuple[int, int]]:
        """
        BFS mencari jalur alternatif yang menghubungkan dua titik
        pada main path tanpa menggunakan sel main path lainnya.
        """

        queue = deque([start])
        previous = {start: None}

        while queue:
            current = queue.popleft()

            if current == end:
                result = []
                node = end

                while node is not None:
                    result.append(node)
                    node = previous[node]

                return list(reversed(result))

            r, c = current
            neighbors = [
                (r - 1, c),
                (r + 1, c),
                (r, c - 1),
                (r, c + 1),
            ]
            self.random.shuffle(neighbors)

            for point in neighbors:
                nr, nc = point

                if not (0 <= nr < size and 0 <= nc < size):
                    continue
                if point in previous:
                    continue

                # Boleh masuk ke endpoint, tetapi tidak boleh menembus
                # bagian lain dari jalur utama.
                if point in occupied and point != end:
                    continue

                previous[point] = current
                queue.append(point)

        return []

    # ---------------------------------------------------------
    # WEAVE CROSSING
    # ---------------------------------------------------------

    def _generate_weave_routes(
        self,
        main_path: list[tuple[int, int]],
        branches: list[DecoyBranch],
        size: int,
    ) -> list[DecoyBranch]:
        """
        Weave crossing memerlukan dua jalur geometris yang berbeda.
        Untuk tahap ini, jalur alternatif yang sudah terhubung dari
        braid dipertahankan sebagai jalur tersendiri.

        Renderer nantinya menentukan efek over-under berdasarkan
        koordinat persilangan yang benar-benar terdeteksi.
        """
        return []

    # ---------------------------------------------------------
    # COORDINATES AND CURVES
    # ---------------------------------------------------------

    def _grid_to_coordinates(
        self,
        grid_path: list[tuple[int, int]],
        size: int,
    ) -> list[tuple[float, float]]:
        spacing_x = (
            self.NUMBER_PATH_X_MAX - self.NUMBER_PATH_X_MIN
        ) / max(1, size - 1)

        spacing_y = (
            self.NUMBER_PATH_Y_MAX - self.NUMBER_PATH_Y_MIN
        ) / max(1, size - 1)

        result = []

        for index, (row, column) in enumerate(grid_path):
            scale = 0.25 if index in (0, len(grid_path) - 1) else 0.65

            jitter_x = self.random.uniform(
                -spacing_x * 0.12,
                spacing_x * 0.12,
            ) * scale

            jitter_y = self.random.uniform(
                -spacing_y * 0.12,
                spacing_y * 0.12,
            ) * scale

            x = self.NUMBER_PATH_X_MIN + column * spacing_x + jitter_x
            y = self.NUMBER_PATH_Y_MIN + row * spacing_y + jitter_y

            result.append((float(x), float(y)))

        return result

    def _smooth_bezier_path(
        self,
        points: list[tuple[float, float]],
    ) -> list[tuple[float, float]]:
        if len(points) < 3:
            return list(points)

        result = [points[0]]

        for index in range(1, len(points) - 1):
            previous = points[index - 1]
            corner = points[index]
            following = points[index + 1]

            incoming = math.hypot(
                corner[0] - previous[0],
                corner[1] - previous[1],
            )
            outgoing = math.hypot(
                following[0] - corner[0],
                following[1] - corner[1],
            )

            if incoming == 0 or outgoing == 0:
                continue

            cut = min(incoming, outgoing) * 0.22

            entry = (
                corner[0] + (previous[0] - corner[0]) * cut / incoming,
                corner[1] + (previous[1] - corner[1]) * cut / incoming,
            )
            exit_point = (
                corner[0] + (following[0] - corner[0]) * cut / outgoing,
                corner[1] + (following[1] - corner[1]) * cut / outgoing,
            )

            result.append(entry)

            for step in range(1, self.CURVE_STEPS + 1):
                t = step / self.CURVE_STEPS
                inv = 1 - t

                x = (
                    inv * inv * entry[0]
                    + 2 * inv * t * corner[0]
                    + t * t * exit_point[0]
                )
                y = (
                    inv * inv * entry[1]
                    + 2 * inv * t * corner[1]
                    + t * t * exit_point[1]
                )

                result.append((x, y))

        result.append(points[-1])
        return result

    @staticmethod
    def _resample_route(
        points: list[tuple[float, float]],
        count: int,
    ) -> list[tuple[float, float]]:
        if not points:
            return []

        if count <= 1:
            return [points[0]]

        segments = []
        total = 0.0

        for start, end in zip(points, points[1:]):
            length = math.hypot(
                end[0] - start[0],
                end[1] - start[1],
            )
            if length > 0:
                segments.append((start, end, length))
                total += length

        if total <= 0:
            return [points[0]] * count

        result = []

        for index in range(count):
            target_distance = total * index / (count - 1)
            traversed = 0.0

            for start, end, length in segments:
                if traversed + length >= target_distance:
                    ratio = (target_distance - traversed) / length
                    result.append((
                        start[0] + (end[0] - start[0]) * ratio,
                        start[1] + (end[1] - start[1]) * ratio,
                    ))
                    break

                traversed += length

        return result

    # ---------------------------------------------------------
    # GRID ACTIVITIES
    # ---------------------------------------------------------

    def _make_path(
        self,
        rows: int,
        columns: int,
        target: int,
    ) -> list[tuple[int, int]]:
        for _ in range(self.MAX_ATTEMPTS):
            start = (
                self.random.randrange(rows),
                self.random.randrange(columns),
            )
            path = [start]
            visited = {start}

            def extend() -> bool:
                if len(path) == target:
                    return True

                r, c = path[-1]
                neighbors = [
                    (r - 1, c),
                    (r + 1, c),
                    (r, c - 1),
                    (r, c + 1),
                ]
                self.random.shuffle(neighbors)

                for point in neighbors:
                    nr, nc = point

                    if not (0 <= nr < rows and 0 <= nc < columns):
                        continue
                    if point in visited:
                        continue

                    visited.add(point)
                    path.append(point)

                    if extend():
                        return True

                    path.pop()
                    visited.remove(point)

                return False

            if extend():
                return path

        raise RuntimeError("Gagal membentuk jalur Numerasi Maze.")

    def _path_value(self, index: int) -> str:
        if self.subtype == "Math Equation":
            if index == 1:
                return "1 + 0"

            left = self.random.randint(1, index - 1)
            return f"{left} + {index - left}"

        return str(index * 2)

    def _decoy_value(self) -> str:
        if self.subtype == "Math Equation":
            a = self.random.randint(1, 9)
            b = self.random.randint(1, 9)
            return f"{a} + {b}"

        return str(
            self.random.choice(
                [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
            )
        )

    def _instruction(self) -> str:
        return {
            "Number Path": (
                "Mulai dari START. Cari angka secara berurutan hingga FINISH. Abaikan angka pengecoh."
            ),
            "Math Equation": (
                "Selesaikan operasi hitung secara berurutan."
            ),
            "Number Pattern": (
                "Ikuti pola bilangan dengan benar."
            ),
        }[self.subtype]
