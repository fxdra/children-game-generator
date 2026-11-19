"""Port of Meat Fighter's border-to-border flood solver."""
from __future__ import annotations
import random
from .maze_graph_processor import Maze, Node


def find_border_nodes(maze: Maze, rng: random.Random) -> list[Node]:
    selected = set()
    cells = maze.cells
    for x in range(maze.width - 1, -1, -1):
        for y in range(maze.height):
            if cells[y][x].white:
                selected.add(cells[y][x]); break
        for y in range(maze.height - 1, -1, -1):
            if cells[y][x].white:
                selected.add(cells[y][x]); break
    for y in range(maze.height - 1, -1, -1):
        for x in range(maze.width):
            if cells[y][x].white:
                selected.add(cells[y][x]); break
        for x in range(maze.width - 1, -1, -1):
            if cells[y][x].white:
                selected.add(cells[y][x]); break
    result = [cell.lower for cell in selected]
    rng.shuffle(result)
    return result


def _wire_terminal(maze: Maze, node: Node, rng: random.Random) -> None:
    directions = ["north", "east", "south", "west"]
    rng.shuffle(directions)
    for direction in directions:
        x, y = node.cell.x, node.cell.y
        nx, ny = {"north": (x, y - 1), "east": (x + 1, y),
                  "south": (x, y + 1), "west": (x - 1, y)}[direction]
        if nx < 0 or ny < 0 or nx >= maze.width or ny >= maze.height or not maze.cells[ny][nx].white:
            setattr(node, direction, node)
            setattr(node, direction + "2", node)
            return


def solve_maze(maze: Maze, rng: random.Random) -> list[Node]:
    border_nodes = find_border_nodes(maze, rng)
    best: list[Node] = []
    stack: list[Node] = []
    for seed in border_nodes:
        for node in maze.all_nodes():
            node.visited_by = None
        seed.visited_by = seed
        seed.region = 0
        stack.append(seed)
        while stack:
            node = stack.pop()
            if node in border_nodes and node.region > len(best):
                best.clear()
                current = node
                while True:
                    best.append(current)
                    if current.visited_by is None or current.visited_by is current:
                        break
                    current = current.visited_by
            next_length = node.region + 1
            for neighbor in node.neighbors():
                if neighbor.visited_by is None:
                    neighbor.visited_by = node
                    neighbor.region = next_length
                    stack.append(neighbor)

    # Reset the solution overlay, leaving the primary maze graph intact.
    for node in maze.all_nodes():
        node.north2 = node.east2 = node.south2 = node.west2 = None
    if best:
        _wire_terminal(maze, best[0], rng)
        _wire_terminal(maze, best[-1], rng)
        opposite = {"north": "south", "east": "west", "south": "north", "west": "east"}
        for n0, n1 in zip(best, best[1:]):
            for direction in ("north", "east", "south", "west"):
                if getattr(n0, direction) is n1:
                    setattr(n0, direction + "2", n1)
                    setattr(n1, opposite[direction] + "2", n0)
                    break
    maze.solution = best
    maze.start = best[0] if best else None
    maze.finish = best[-1] if best else None
    return best
