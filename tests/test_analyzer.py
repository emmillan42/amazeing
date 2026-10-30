"""Generated mazes checked by the official analyzer.

Two things are checked here.  Perfect mazes must get the ``PERFECT``
verdict (S1 checkpoint, A3 and A5a).  And every measure of our own
validator must give the very number the analyzer gives (A5b), on
mazes with loops too, since a perfect maze always reports 0 loops and
would prove nothing about ``count_loops``.

``maze_analyzer.py`` comes from the intra and is listed in
``.gitignore``: the whole module is skipped when no local copy sits at
the root of the repository.
"""
from __future__ import annotations

import random
from pathlib import Path
from typing import Any

import pytest

from app.writer import write_maze
from mazegen.generator import MazeGenerator
from mazegen.maze import Direction, Maze
from mazegen.validator import count_dead_ends, count_loops

analyzer = pytest.importorskip("maze_analyzer")

SIZES: list[tuple[int, int]] = [
    (3, 3), (8, 6), (9, 7), (10, 8), (15, 11), (20, 15), (30, 20),
    (41, 25),
]


def analyze(maze: Maze, path: Path) -> Any:
    """Write ``maze`` to ``path`` and return the analyzer's report."""
    write_maze(path, maze)
    return analyzer.analyze(analyzer.Maze.from_file(str(path)))


def open_random_walls(maze: Maze, rng: random.Random, count: int) -> None:
    """Open up to ``count`` random inner walls between free cells.

    The 3x3 rule is ignored on purpose: neither the analyzer nor the
    counters look at it, and the point is to reach many loop counts.
    Opening walls never disconnects anything, so the maze stays in the
    domain where both tools must agree.
    """
    blocked = maze.blocked
    free = [cell for cell in maze.cells() if cell not in blocked]
    for _ in range(count):
        x, y = rng.choice(free)
        direction = rng.choice([Direction.EAST, Direction.SOUTH])
        target = maze.neighbour(x, y, direction)
        if target is not None and target not in blocked:
            maze.open_wall(x, y, direction)


@pytest.mark.parametrize("width,height", SIZES)
def test_perfect_maze_passes_the_analyzer(
    width: int, height: int, tmp_path: Path
) -> None:
    for seed in range(5):
        maze = MazeGenerator(width, height, perfect=True, seed=seed).generate()
        report = analyze(maze, tmp_path / f"maze_{seed}.txt")
        assert report.incoherent == ()
        assert report.disconnected_corridors == 0
        assert report.loops == 0
        assert analyzer.verdict(report, 2, 2).startswith("PERFECT")


@pytest.mark.parametrize("width,height", SIZES)
def test_measures_match_the_analyzer(
    width: int, height: int, tmp_path: Path
) -> None:
    for seed in range(5):
        maze = MazeGenerator(width, height, perfect=True, seed=seed).generate()
        rng = random.Random(seed)
        for step in range(8):
            report = analyze(maze, tmp_path / f"maze_{seed}_{step}.txt")
            assert count_loops(maze) == report.loops
            assert count_dead_ends(maze) == report.dead_ends
            open_random_walls(maze, rng, 5)
