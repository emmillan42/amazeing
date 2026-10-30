"""Tests for the pipeline of :class:`MazeGenerator` (A7a).

What matters here is not the maze itself, the other test files cover
it, but when each error shows up and what it says: a wrong parameter
must fail in the constructor, a missing piece must fail with a message
instead of a traceback, and a bug must be reproducible from its
message alone.
"""
from __future__ import annotations

import random

import pytest

import mazegen.generator as generator_module
from mazegen.algorithms.base import Algorithm
from mazegen.errors import GenerationError, InvalidGeometryError, MazeError
from mazegen.generator import MIN_SIDE, MazeGenerator
from mazegen.maze import Maze
from mazegen.validator import count_loops


class LazyAlgorithm(Algorithm):
    """A buggy algorithm that carves nothing at all."""

    def carve(self, maze: Maze, rng: random.Random) -> None:
        """Leave every wall closed."""


class StubAlgorithm(Algorithm):
    """An algorithm that is still a stub."""

    def carve(self, maze: Maze, rng: random.Random) -> None:
        """Do what every stub of the project does."""
        raise NotImplementedError


# ----------------------------------------------------------------------
# Constructor
# ----------------------------------------------------------------------

@pytest.mark.parametrize("width,height", [
    (MIN_SIDE - 1, 10), (10, MIN_SIDE - 1), (0, 10), (-5, 10),
])
def test_size_is_checked(width: int, height: int) -> None:
    with pytest.raises(InvalidGeometryError, match="invalid maze size"):
        MazeGenerator(width, height)


def test_size_error_is_not_the_pattern_warning() -> None:
    # "too small" is the wording of the pattern warning, which is not
    # fatal: the fatal error must not sound the same.
    with pytest.raises(InvalidGeometryError) as caught:
        MazeGenerator(2, 10)
    assert "too small" not in str(caught.value)


# (6, 5) and (8, 5) are the two top cells of the "4" in 20x15.

def test_entry_on_the_pattern_fails_in_the_constructor() -> None:
    with pytest.raises(InvalidGeometryError, match=r"ENTRY \(6, 5\)"):
        MazeGenerator(20, 15, entry=(6, 5), perfect=True)


def test_exit_on_the_pattern_fails_in_the_constructor() -> None:
    with pytest.raises(InvalidGeometryError, match=r"EXIT \(8, 5\)"):
        MazeGenerator(20, 15, exit=(8, 5), perfect=True)


def test_cell_on_a_skipped_pattern_is_fine() -> None:
    # Below 9x7 there is no pattern, so no cell can fall on it.
    MazeGenerator(8, 6, entry=(3, 2), perfect=True, seed=0).generate()


def test_pattern_state_is_known_before_generating() -> None:
    assert MazeGenerator(8, 6).pattern_skipped
    generator = MazeGenerator(20, 15, perfect=True)
    assert not generator.pattern_skipped
    assert len(generator.pattern_cells) == 20


def test_maze_before_generate_is_an_error() -> None:
    with pytest.raises(GenerationError, match="generate"):
        _ = MazeGenerator(20, 15).maze


# ----------------------------------------------------------------------
# Missing pieces: an error, never a traceback
# ----------------------------------------------------------------------

def test_stub_algorithm_is_reported(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        generator_module, "get_algorithm", lambda name: StubAlgorithm()
    )
    with pytest.raises(GenerationError, match="not implemented"):
        MazeGenerator(20, 15, perfect=True).generate()


def test_stub_braiding_is_reported(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patched, so the test keeps its meaning once A6 is done.
    def stub(maze: Maze, rng: random.Random, max_dead_ends: int = 0) -> int:
        raise NotImplementedError

    monkeypatch.setattr(generator_module, "braid", stub)
    with pytest.raises(GenerationError, match="perfect=True"):
        MazeGenerator(20, 15, perfect=False).generate()


def test_mode_reaches_the_validator(monkeypatch: pytest.MonkeyPatch) -> None:
    # With a braiding that does nothing, the playable mode gets a bare
    # spanning tree, which only the playable checks can reject.
    def no_braid(maze: Maze, rng: random.Random,
                 max_dead_ends: int = 0) -> int:
        return 0

    def no_open(maze: Maze, rng: random.Random) -> None:
        return None

    monkeypatch.setattr(generator_module, "braid", no_braid)
    monkeypatch.setattr(generator_module, "ensure_open", no_open)
    with pytest.raises(GenerationError, match="playable maze: 0 indep"):
        MazeGenerator(20, 15, perfect=False, seed=0).generate()


def test_every_failure_is_a_maze_error(
    monkeypatch: pytest.MonkeyPatch
) -> None:
    # a_maze_ing.py only catches MazeError: anything else would be a
    # traceback in front of the evaluator.
    monkeypatch.setattr(
        generator_module, "get_algorithm", lambda name: StubAlgorithm()
    )
    with pytest.raises(MazeError):
        MazeGenerator(20, 15, perfect=True).generate()


# ----------------------------------------------------------------------
# Bugs: reproducible from the message
# ----------------------------------------------------------------------

def test_invalid_maze_names_how_to_rebuild_it(
    monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        generator_module, "get_algorithm", lambda name: LazyAlgorithm()
    )
    generator = MazeGenerator(20, 15, perfect=True, seed=7)
    with pytest.raises(GenerationError) as caught:
        generator.generate()
    message = str(caught.value)
    assert message.startswith("internal error")
    assert "cannot be reached" in message
    for part in ["20x15", "perfect=True", "seed=7", "call #1"]:
        assert part in message


def test_failed_maze_is_not_kept(monkeypatch: pytest.MonkeyPatch) -> None:
    generator = MazeGenerator(20, 15, perfect=True, seed=7)
    first = generator.generate()
    monkeypatch.setattr(
        generator_module, "get_algorithm", lambda name: LazyAlgorithm()
    )
    with pytest.raises(GenerationError, match="call #2"):
        generator.generate()
    assert generator.maze is first


# ----------------------------------------------------------------------
# Perfect mode, end to end
# ----------------------------------------------------------------------

@pytest.mark.parametrize("width,height", [(3, 3), (9, 7), (20, 15)])
def test_perfect_mode_end_to_end(width: int, height: int) -> None:
    generator = MazeGenerator(width, height, perfect=True, seed=1)
    maze = generator.generate()
    assert generator.maze is maze
    assert count_loops(maze) == 0
    assert maze.solution[0] == maze.entry
    assert maze.solution[-1] == maze.exit


def test_same_seed_same_sequence() -> None:
    # The n-th maze of a generator depends on the seed and on n only:
    # that is what makes "seed=..., call #n" a reproduction recipe.
    first = MazeGenerator(20, 15, perfect=True, seed=3)
    second = MazeGenerator(20, 15, perfect=True, seed=3)
    for _ in range(3):
        assert (first.generate().to_hex_lines()
                == second.generate().to_hex_lines())
