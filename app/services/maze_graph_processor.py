from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


class Node:
    __slots__ = (
        "cell", "north", "east", "south", "west",
        "north2", "east2", "south2", "west2", "visited_by", "region",
    )

    def __init__(self, cell: "Cell") -> None:
        self.cell = cell
        self.north: Node | None = None
        self.east: Node | None = None
        self.south: Node | None = None
        self.west: Node | None = None
        self.north2: Node | None = None
        self.east2: Node | None = None
        self.south2: Node | None = None
        self.west2: Node | None = None
        self.visited_by: Node | None = None
        self.region: int = -1

    def backup(self) -> None:
        self.north2, self.east2 = self.north, self.east
        self.south2, self.west2 = self.south, self.west

    def restore(self) -> None:
        self.north, self.east = self.north2, self.east2
        self.south, self.west = self.south2, self.west2

    def neighbors(self) -> Iterable["Node"]:
        for node in (self.north, self.east, self.south, self.west):
            if node is not None:
                yield node


class Cell:
    __slots__ = ("x", "y", "white", "lower", "upper")

    def __init__(self, x: int, y: int, white: bool = True) -> None:
        self.x, self.y, self.white = x, y, bool(white)
        self.lower = Node(self)
        self.upper = Node(self)

    def backup(self) -> None:
        self.lower.backup()
        self.upper.backup()

    def restore(self) -> None:
        self.lower.restore()
        self.upper.restore()

    def is_not_flat(self) -> bool:
        n = self.upper
        return any((n.north, n.east, n.south, n.west))

    def is_flat(self) -> bool:
        return not self.is_not_flat()


@dataclass(frozen=True)
class MazeOptions:
    width: int = 30
    height: int = 30
    loop_frac: float = 0.05
    cross_frac: float = 0.25
    long_passages: bool = False
    mask: list[list[bool]] | None = None
    seed: int | None = None

    def validate(self) -> None:
        if self.mask is not None:
            if not self.mask or not self.mask[0]:
                raise ValueError("mask tidak boleh kosong")
            width, height = len(self.mask[0]), len(self.mask)
            if any(len(row) != width for row in self.mask):
                raise ValueError("semua baris mask harus memiliki lebar yang sama")
        else:
            width, height = self.width, self.height
        if width < 1 or height < 1 or width > 200 or height > 200:
            raise ValueError("ukuran maze harus berada pada rentang 1–200")
        if not 0 <= self.loop_frac <= 1:
            raise ValueError("loop_frac harus berada pada rentang 0–1")
        if not 0 <= self.cross_frac <= 1:
            raise ValueError("cross_frac harus berada pada rentang 0–1")


class Maze:
    def __init__(self, options: MazeOptions) -> None:
        options.validate()
        self.width = len(options.mask[0]) if options.mask is not None else options.width
        self.height = len(options.mask) if options.mask is not None else options.height
        self.cells = [
            [Cell(x, y, options.mask[y][x] if options.mask is not None else True)
             for x in range(self.width)]
            for y in range(self.height)
        ]
        self.solution: list[Node] = []
        self.start: Node | None = None
        self.finish: Node | None = None
        self.loop_count = 0
        self.cross_count = 0

    def all_nodes(self) -> Iterable[Node]:
        for row in self.cells:
            for cell in row:
                yield cell.lower
                yield cell.upper


class MazeGraphProcessor:
    """Graph operations shared by the Loop, Cross and tree-building stages."""

    @staticmethod
    def assign_region(region: int, seed: Node, stack: list[Node]) -> list[Node]:
        nodes = [seed]
        seed.region = region
        stack.append(seed)
        try:
            while stack:
                node = stack.pop()
                for neighbor in node.neighbors():
                    if neighbor.region < 0:
                        neighbor.region = region
                        stack.append(neighbor)
                        nodes.append(neighbor)
        finally:
            stack.clear()
        return nodes

    def assign_regions(self, maze: Maze, stack: list[Node]) -> list[list[Node]]:
        regions: list[list[Node]] = []
        for row in maze.cells:
            for cell in row:
                if cell.lower.region < 0:
                    regions.append(self.assign_region(len(regions), cell.lower, stack))
                if cell.upper.region < 0:
                    regions.append(self.assign_region(len(regions), cell.upper, stack))
        return regions

    @staticmethod
    def find_loop(maze: Maze, seed: Node, stack: list[Node]) -> bool:
        for node in maze.all_nodes():
            node.visited_by = None
        seed.visited_by = seed
        stack.append(seed)
        try:
            while stack:
                node = stack.pop()
                for neighbor in node.neighbors():
                    if neighbor.visited_by is not None:
                        if neighbor is not node.visited_by:
                            return True
                    else:
                        neighbor.visited_by = node
                        stack.append(neighbor)
            return False
        finally:
            stack.clear()

    @staticmethod
    def merge_regions(region1: int, region2: int, regions: list[list[Node]]) -> None:
        if region1 == region2:
            return
        source, target = regions[region1], regions[region2]
        for node in source:
            node.region = region2
            target.append(node)
        regions[region1] = []
