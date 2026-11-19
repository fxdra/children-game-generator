"""Meat Fighter Loop construction (four diagonal orientations)."""
from __future__ import annotations
import random
from .maze_graph_processor import Maze, Cell, Node, MazeGraphProcessor


class MazeBraidEngine:
    def __init__(self, graph: MazeGraphProcessor | None = None, rng: random.Random | None = None):
        self.graph = graph or MazeGraphProcessor()
        self.rng = rng or random.Random()

    @staticmethod
    def _wire_cross(cell: Cell, north: Cell, east: Cell, south: Cell, west: Cell,
                    north_south_hops_east_west: bool) -> None:
        lo, up = cell.lower, cell.upper
        if north_south_hops_east_west:
            if lo.north:
                lo.north.south, up.north, lo.north = up, lo.north, None
            else:
                north.lower.south, up.north = up, north.lower
            if lo.south:
                lo.south.north, up.south, lo.south = up, lo.south, None
            else:
                south.lower.north, up.south = up, south.lower
            if not lo.east:
                lo.east, east.lower.west = east.lower, lo
            if not lo.west:
                lo.west, west.lower.east = west.lower, lo
        else:
            if lo.east:
                lo.east.west, up.east, lo.east = up, lo.east, None
            else:
                east.lower.west, up.east = up, east.lower
            if lo.west:
                lo.west.east, up.west, lo.west = up, lo.west, None
            else:
                west.lower.east, up.west = up, west.lower
            if not lo.north:
                lo.north, north.lower.south = north.lower, lo
            if not lo.south:
                lo.south, south.lower.north = south.lower, lo

    def _try_loop(self, maze: Maze, cell: Cell, stack: list[Node], orientation: int,
                  north_south_hops: bool) -> bool:
        # (diagonal dx/dy, required cardinal cells, two links to diagonal)
        specs = {
            0: (1, -1, "north", "east", "south", "west"),        # NE in source's y-down grid
            1: (1, 1, "south", "east", "north", "west"),
            2: (-1, 1, "south", "west", "north", "east"),
            3: (-1, -1, "north", "west", "south", "east"),
        }
        dx, dy, first_name, second_name, opposite1, opposite2 = specs[orientation]
        # Use the exact cell coordinates used by the TypeScript implementation.
        diagonal = maze.cells[cell.y + dy][cell.x + dx]
        first = maze.cells[cell.y + (dy if first_name in ("north", "south") else 0)][cell.x + (dx if first_name in ("east", "west") else 0)]
        second = maze.cells[cell.y + (dy if second_name in ("north", "south") else 0)][cell.x + (dx if second_name in ("east", "west") else 0)]
        north, east = maze.cells[cell.y - 1][cell.x], maze.cells[cell.y][cell.x + 1]
        south, west = maze.cells[cell.y + 1][cell.x], maze.cells[cell.y][cell.x - 1]
        if not (first.white and not first.is_not_flat() and diagonal.white and not diagonal.is_not_flat()
                and second.white and not second.is_not_flat()):
            return False
        if not (north.white and east.white and south.white and west.white):
            return False

        touched = [cell, north, diagonal, east, south, west]
        for item in touched:
            item.backup()
        self._wire_cross(cell, north, east, south, west, north_south_hops)
        # Link the two cardinal cells around the selected diagonal.
        if orientation == 0:  # NE
            a, b, da, db = north, east, diagonal, ("east", "north")
        elif orientation == 1:  # SE
            a, b, da, db = south, east, diagonal, ("east", "south")
        elif orientation == 2:  # SW
            a, b, da, db = south, west, diagonal, ("west", "south")
        else:  # NW
            a, b, da, db = north, west, diagonal, ("west", "north")
        direction_a, direction_b = db
        opposite = {"north": "south", "south": "north", "east": "west", "west": "east"}
        if getattr(a.lower, direction_a) is None:
            setattr(a.lower, direction_a, da.lower)
            setattr(da.lower, opposite[direction_a], a.lower)
        if getattr(b.lower, direction_b) is None:
            setattr(b.lower, direction_b, da.lower)
            setattr(da.lower, opposite[direction_b], b.lower)

        if self.graph.find_loop(maze, cell.lower, stack) or self.graph.find_loop(maze, cell.upper, stack):
            for item in touched:
                item.restore()
            return False
        return True

    def add_loops(self, maze: Maze, loop_fraction: float, stack: list[Node]) -> int:
        candidates = [maze.cells[y][x] for y in range(1, maze.height - 1)
                      for x in range(1, maze.width - 1) if maze.cells[y][x].white]
        target = round(len(candidates) * loop_fraction)
        loops = 0
        while loops < target and candidates:
            cell = candidates.pop(self.rng.randrange(len(candidates)))
            orientations = [0, 1, 2, 3]
            self.rng.shuffle(orientations)
            for orientation in orientations:
                hop = self.rng.random() < 0.5
                if self._try_loop(maze, cell, stack, orientation, hop) or self._try_loop(maze, cell, stack, orientation, not hop):
                    loops += 1
                    break
        maze.loop_count = loops
        return loops
