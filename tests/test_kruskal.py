"""Tests for randomised Kruskal (A8).

The properties are measured with helpers written here, not with
``mazegen.validator``: the validator is under test too, and a test
that trusts it would prove nothing about the carving.
"""
from __future__ import annotations

import random

import pytest

from mazegen.algorithms import get_algorithm
from mazegen.algorithms.kruskal import Kruskal, _DisjointSets
from mazegen.maze import ALL_WALLS, Cell, Direction, Maze
from mazegen.pattern import fits, stamp

SIZES: list[tuple[int, int]] = [
    (w, h) for w in range(3, 22, 3) for h in range(3, 22, 4)
] + [(9, 7), (20, 15), (41, 25)]


def carved(width: int, height: int, seed: int, pattern: bool) -> Maze:
    """Return a freshly carved maze, with the 42 if asked and possible."""
    maze = Maze(width, height)
    if pattern and fits(width, height):
        stamp(maze)
    Kruskal().carve(maze, random.Random(seed))
    return maze


def free_cells(maze: Maze) -> set[Cell]:
    """Return the cells that do not belong to the pattern."""
    return set(maze.cells()) - maze.blocked


def open_edges(maze: Maze) -> int:
    """Count each open inner wall once, looking east and south only."""
    return sum(
        1
        for x, y in maze.cells()
        for direction in (Direction.EAST, Direction.SOUTH)
        if maze.neighbour(x, y, direction) is not None
        and not maze.has_wall(x, y, direction)
    )


def reached_from(maze: Maze, start: Cell) -> set[Cell]:
    """Return the cells reachable from ``start``, by depth-first search."""
    seen = {start}
    stack = [start]
    while stack:
        for target in maze.open_neighbours(*stack.pop()):
            if target not in seen:
                seen.add(target)
                stack.append(target)
    return seen


@pytest.mark.parametrize("pattern", [True, False])
@pytest.mark.parametrize("width,height", SIZES)
def test_spanning_tree(width: int, height: int, pattern: bool) -> None:
    # A connected graph with V nodes and V - 1 edges is a tree.
    for seed in range(3):
        maze = carved(width, height, seed, pattern)
        free = free_cells(maze)
        assert reached_from(maze, next(iter(free))) == free
        assert open_edges(maze) == len(free) - 1


@pytest.mark.parametrize("width,height", [(9, 7), (20, 15), (41, 25)])
def test_pattern_left_untouched(width: int, height: int) -> None:
    maze = carved(width, height, seed=0, pattern=True)
    assert maze.blocked
    for x, y in maze.blocked:
        assert maze.cell_code(x, y) == ALL_WALLS


def test_same_seed_same_maze() -> None:
    first = carved(20, 15, seed=42, pattern=True)
    second = carved(20, 15, seed=42, pattern=True)
    assert first.to_hex_lines() == second.to_hex_lines()


def test_seed_changes_the_maze() -> None:
    mazes = {
        tuple(carved(20, 15, seed, pattern=True).to_hex_lines())
        for seed in range(10)
    }
    assert len(mazes) == 10


def test_global_random_is_not_used() -> None:
    # ADR-006: only the rng received as a parameter may be consumed.
    state = random.getstate()
    carved(20, 15, seed=1, pattern=True)
    assert random.getstate() == state


def test_large_maze() -> None:
    maze = carved(150, 150, seed=0, pattern=True)
    assert open_edges(maze) == len(free_cells(maze)) - 1


def test_registered_under_its_name() -> None:
    assert isinstance(get_algorithm("kruskal"), Kruskal)
    assert isinstance(get_algorithm(" KRUSKAL "), Kruskal)


def test_not_the_backtracker() -> None:
    # Same seed, same grid: a different algorithm must give a
    # different maze, or the registry is pointing at the wrong class.
    maze = carved(20, 15, seed=42, pattern=True)
    other = Maze(20, 15)
    stamp(other)
    get_algorithm("backtracker").carve(other, random.Random(42))
    assert maze.to_hex_lines() != other.to_hex_lines()


def test_union_reports_whether_it_merged() -> None:
    cells: list[Cell] = [(0, 0), (1, 0), (2, 0), (3, 0)]
    sets = _DisjointSets(cells)
    assert sets.union((0, 0), (1, 0))
    assert sets.union((2, 0), (3, 0))
    assert not sets.union((1, 0), (0, 0))
    assert sets.find((0, 0)) == sets.find((1, 0))
    assert sets.find((0, 0)) != sets.find((2, 0))
    assert sets.union((1, 0), (3, 0))
    assert not sets.union((0, 0), (2, 0))
    assert len({sets.find(cell) for cell in cells}) == 1


def test_find_follows_a_long_chain_without_recursion() -> None:
    # Each union names the new lone cell first, the worst order for a
    # structure without union by size: the whole set would hang under
    # it, one level deeper each time.  A recursive find() without union
    # by size would hit the recursion limit here.
    cells: list[Cell] = [(x, 0) for x in range(5000)]
    sets = _DisjointSets(cells)
    for cell in cells[1:]:
        assert sets.union(cell, cells[0])
    roots = {sets.find(cell) for cell in cells}
    assert len(roots) == 1


def test_blocked_cells_are_unknown_to_the_sets() -> None:
    sets = _DisjointSets([(0, 0)])
    with pytest.raises(KeyError):
        sets.find((1, 0))
