"""Unit tests for :mod:`mazegen.solver` (task A4)."""
from __future__ import annotations

import random

import pytest

from mazegen.errors import MazeError
from mazegen.maze import Cell, Direction, Maze
from mazegen.solver import shortest_path


def open_all(maze: Maze) -> Maze:
    """Open every inner wall of ``maze`` and return it."""
    for x, y in maze.cells():
        for direction in (Direction.EAST, Direction.SOUTH):
            if maze.neighbour(x, y, direction) is not None:
                maze.open_wall(x, y, direction)
    return maze


def random_maze(width: int, height: int, seed: int) -> Maze:
    """Open each inner wall with probability 0.7, loops allowed."""
    rng = random.Random(seed)
    maze = Maze(width, height)
    for x, y in maze.cells():
        for direction in (Direction.EAST, Direction.SOUTH):
            if (maze.neighbour(x, y, direction) is not None
                    and rng.random() < 0.7):
                maze.open_wall(x, y, direction)
    return maze


def brute_force_length(maze: Maze, start: Cell, goal: Cell) -> int | None:
    """Return the length of the shortest path by trying every path.

    Independent oracle: exhaustive depth-first search over simple
    paths, sharing no code with the solver.  Only usable on tiny mazes.
    """
    best: int | None = None
    stack: list[tuple[Cell, frozenset[Cell]]] = [
        (start, frozenset([start]))
    ]
    while stack:
        cell, seen = stack.pop()
        if cell == goal:
            if best is None or len(seen) < best:
                best = len(seen)
            continue
        for nxt in maze.open_neighbours(*cell):
            if nxt not in seen:
                stack.append((nxt, seen | {nxt}))
    return best


def assert_valid_path(maze: Maze, path: list[Cell]) -> None:
    """Check that consecutive cells are joined by an open wall."""
    for cell, nxt in zip(path, path[1:]):
        assert nxt in maze.open_neighbours(*cell)


def test_corridor() -> None:
    maze = open_all(Maze(3, 1))
    assert shortest_path(maze, (0, 0), (2, 0)) == [(0, 0), (1, 0), (2, 0)]


def test_start_equals_goal() -> None:
    maze = Maze(2, 2)
    assert shortest_path(maze, (1, 1), (1, 1)) == [(1, 1)]


def test_tie_is_broken_in_direction_order() -> None:
    # Two shortest paths in an open 2x2: east first, then south.
    maze = open_all(Maze(2, 2))
    path = shortest_path(maze, (0, 0), (1, 1))
    assert path == [(0, 0), (1, 0), (1, 1)]
    maze.set_solution(path)
    assert maze.solution_string() == "ES"


def test_unreachable_goal_raises() -> None:
    maze = Maze(2, 1)   # every wall closed
    with pytest.raises(MazeError, match="no path"):
        shortest_path(maze, (0, 0), (1, 0))


def test_cell_outside_raises() -> None:
    maze = Maze(2, 2)
    with pytest.raises(MazeError, match="outside"):
        shortest_path(maze, (0, 0), (5, 5))


def test_blocked_cell_raises() -> None:
    maze = Maze(3, 3)
    maze.block(1, 1)
    with pytest.raises(MazeError, match="blocked"):
        shortest_path(maze, (0, 0), (1, 1))


def test_goes_around_blocked_cells() -> None:
    maze = Maze(3, 3)
    maze.block(1, 1)
    for x, y in maze.cells():
        for direction in (Direction.EAST, Direction.SOUTH):
            target = maze.neighbour(x, y, direction)
            if (target is not None and (x, y) != (1, 1)
                    and target != (1, 1)):
                maze.open_wall(x, y, direction)
    path = shortest_path(maze, (1, 0), (1, 2))
    assert len(path) == 5
    assert (1, 1) not in path
    assert_valid_path(maze, path)


@pytest.mark.parametrize("seed", range(200))
def test_matches_brute_force(seed: int) -> None:
    maze = random_maze(4, 3, seed)
    start, goal = (0, 0), (3, 2)
    expected = brute_force_length(maze, start, goal)
    if expected is None:
        with pytest.raises(MazeError):
            shortest_path(maze, start, goal)
        return
    path = shortest_path(maze, start, goal)
    assert path[0] == start and path[-1] == goal
    assert len(path) == expected
    assert_valid_path(maze, path)
    assert shortest_path(maze, start, goal) == path   # deterministic
