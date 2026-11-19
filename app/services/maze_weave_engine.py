"""Meat Fighter crossing construction. Cross tracks occupy separate Nodes."""
from __future__ import annotations
import random
from .maze_graph_processor import Maze, Cell, Node, MazeGraphProcessor
from .maze_braid_engine import MazeBraidEngine


class MazeWeaveEngine:
    def __init__(self, graph: MazeGraphProcessor | None = None, rng: random.Random | None = None):
        self.graph = graph or MazeGraphProcessor()
        self.rng = rng or random.Random()
        self._wire = MazeBraidEngine._wire_cross

    def add_cross(self, maze: Maze, cell: Cell, stack: list[Node], north_south_hops: bool) -> bool:
        north = maze.cells[cell.y - 1][cell.x]
        east = maze.cells[cell.y][cell.x + 1]
        south = maze.cells[cell.y + 1][cell.x]
        west = maze.cells[cell.y][cell.x - 1]
        if not all(c.white for c in (north, east, south, west)):
            return False
        touched = [cell, north, east, south, west]
        for item in touched:
            item.backup()
        self._wire(cell, north, east, south, west, north_south_hops)
        if self.graph.find_loop(maze, cell.lower, stack) or self.graph.find_loop(maze, cell.upper, stack):
            for item in touched:
                item.restore()
            return False
        return True

    def add_crosses(self, maze: Maze, cross_fraction: float, stack: list[Node]) -> int:
        candidates = [maze.cells[y][x] for y in range(1, maze.height - 1)
                      for x in range(1, maze.width - 1)
                      if maze.cells[y][x].white and maze.cells[y][x].is_flat()]
        target = round(len(candidates) * cross_fraction)
        crosses = 0
        while crosses < target and candidates:
            cell = candidates.pop(self.rng.randrange(len(candidates)))
            hop = self.rng.random() < 0.5
            if self.add_cross(maze, cell, stack, hop) or self.add_cross(maze, cell, stack, not hop):
                crosses += 1
        maze.cross_count = crosses
        return crosses
