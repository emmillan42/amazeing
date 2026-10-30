"""Tests of the generator pipeline in the playable mode (A7b).

Braiding itself is tested in ``test_braiding.py``.  Here the question
is how the generator uses it: the default configuration works, a bug in
braiding comes out as a reproducible internal error, and what braiding
reports about itself is never trusted.
"""
from __future__ import annotations

import random

import pytest

from mazegen import generator
from mazegen.errors import GenerationError, MazeError
from mazegen.generator import MazeGenerator
from mazegen.maze import Maze
from mazegen.validator import MIN_LOOPS, count_dead_ends, count_loops


def test_default_mode_gives_a_bonus_board() -> None:
    """``perfect=False`` is the default and needs nothing else."""
    maze = MazeGenerator(20, 15, seed=42).generate()
    assert count_dead_ends(maze) == (0, 3)
    assert count_loops(maze) >= MIN_LOOPS
    assert maze.solution_string()


@pytest.mark.parametrize("size", [(3, 3), (3, 4), (4, 3), (8, 6), (9, 7)])
def test_default_mode_on_small_grids(size: tuple[int, int]) -> None:
    """Grids with and without the pattern, serpent-prone sizes included."""
    for seed in range(20):
        maze = MazeGenerator(*size, seed=seed).generate()
        assert count_dead_ends(maze)[0] == 0


def _raise(error: MazeError) -> None:
    """Raise ``error``: a stand-in for a broken pipeline step."""
    raise error


def test_braid_failure_is_an_internal_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A braiding bug says it is ours and how to rebuild the maze."""
    cause = GenerationError("no wall of the 3x3 block at (0, 0)")

    def broken(maze: Maze, rng: random.Random,
               max_dead_ends: int = 0) -> int:
        _raise(cause)
        return 0

    monkeypatch.setattr(generator, "braid", broken)
    with pytest.raises(GenerationError) as caught:
        MazeGenerator(20, 15, seed=7).generate()
    message = str(caught.value)
    assert message.startswith("internal error, please report it")
    assert "no wall of the 3x3 block" in message
    assert "seed=7" in message and "perfect=False" in message
    assert "generate() call #1" in message
    assert caught.value.__cause__ is cause


def test_ensure_open_failure_is_an_internal_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Any ``MazeError`` from the braiding step is wrapped, not only one."""
    def broken(maze: Maze, rng: random.Random) -> None:
        _raise(MazeError("cannot open the outer border at (0, 0)"))

    monkeypatch.setattr(generator, "ensure_open", broken)
    with pytest.raises(GenerationError, match="internal error"):
        MazeGenerator(9, 7, seed=1).generate()


def test_what_braid_reports_is_not_trusted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A braid that does nothing and claims success is still caught.

    The real ``ensure_open`` still runs and opens some corners, so the
    board may reach two loops: what gives it away is the dead ends.
    """
    def lazy(maze: Maze, rng: random.Random,
             max_dead_ends: int = 0) -> int:
        return 0

    monkeypatch.setattr(generator, "braid", lazy)
    with pytest.raises(GenerationError, match="invalid playable maze"):
        MazeGenerator(20, 15, seed=3).generate()


def test_perfect_mode_never_braids(monkeypatch: pytest.MonkeyPatch) -> None:
    """With ``perfect=True`` the braiding step is not even called."""
    def forbidden(maze: Maze, rng: random.Random,
                  max_dead_ends: int = 0) -> int:
        raise AssertionError("braid called in perfect mode")

    monkeypatch.setattr(generator, "braid", forbidden)
    maze = MazeGenerator(20, 15, seed=3, perfect=True).generate()
    assert count_loops(maze) == 0
