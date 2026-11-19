"""Meat Fighter algorithm orchestration, kept separate from Erbsland backend."""
from __future__ import annotations
import random
from .maze_graph_processor import Maze, MazeOptions, MazeGraphProcessor, Node
from .maze_braid_engine import MazeBraidEngine
from .maze_weave_engine import MazeWeaveEngine
from .meatfighter_maze_solver import solve_maze


class MeatFighterMazeGenerator:
    def __init__(self, options: MazeOptions | None = None):
        self.options = options or MazeOptions()
        self.rng = random.Random(self.options.seed)
        self.graph = MazeGraphProcessor()
        self.maze: Maze | None = None
        self.braid = MazeBraidEngine(self.graph, self.rng)
        self.weave = MazeWeaveEngine(self.graph, self.rng)

    def generate(self) -> Maze:
        maze = Maze(self.options)
        stack: list[Node] = []
        self.braid.add_loops(maze, self.options.loop_frac, stack)
        self.weave.add_crosses(maze, self.options.cross_frac, stack)
        regions = self.graph.assign_regions(maze, stack)
        self._create_spanning_tree(maze, stack, regions, self.options.long_passages)
        solve_maze(maze, self.rng)
        self.maze = maze
        return maze

    def _create_spanning_tree(self, maze: Maze, nodes: list[Node],
                              regions: list[list[Node]], long_passages: bool) -> None:
        # Candidate lower nodes match the TypeScript condition.
        for y in range(maze.height - 1, -1, -1):
            for x in range(maze.width - 1, -1, -1):
                cell = maze.cells[y][x]
                if cell.white and not (cell.upper.north or cell.upper.east):
                    nodes.append(cell.lower)
        if long_passages:
            self.rng.shuffle(nodes)

        import itertools
        permutations = list(itertools.permutations(("north", "east", "south", "west")))
        deltas = {"north": (0, -1), "east": (1, 0), "south": (0, 1), "west": (-1, 0)}
        opposites = {"north": "south", "east": "west", "south": "north", "west": "east"}
        while nodes:
            index = len(nodes) - 1 if long_passages else self.rng.randrange(len(nodes))
            node = nodes[index]
            if long_passages:
                self._move_to_end(nodes, node)
            cell = node.cell
            directions = list(self.rng.choice(permutations))
            connected = False
            for direction in directions:
                dx, dy = deltas[direction]
                nx, ny = cell.x + dx, cell.y + dy
                if not (0 <= nx < maze.width and 0 <= ny < maze.height):
                    continue
                if getattr(node, direction) is not None:
                    continue
                neighbor_cell = maze.cells[ny][nx]
                neighbor = neighbor_cell.lower
                if not neighbor_cell.white or neighbor.region == node.region:
                    continue
                setattr(neighbor, opposites[direction], node)
                setattr(node, direction, neighbor)
                if long_passages:
                    self._move_to_end(nodes, neighbor)
                self.graph.merge_regions(neighbor.region, node.region, regions)
                connected = True
                break
            if not connected:
                if long_passages:
                    nodes.pop()
                else:
                    nodes.pop(index)

    @staticmethod
    def _move_to_end(nodes: list[Node], node: Node) -> None:
        try:
            index = nodes.index(node)
        except ValueError:
            return
        if index != len(nodes) - 1:
            nodes.append(nodes.pop(index))

    def get_maze(self) -> Maze:
        if self.maze is None:
            raise RuntimeError("Maze belum dibuat. Panggil generate() terlebih dahulu.")
        return self.maze
