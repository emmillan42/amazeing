"""Kruskal through the whole pipeline (A8, ADR-021, ADR-022).

Kruskal trees have far more leaves than the backtracker ones, and on
small grids the braiding needs its forced opening (open, then close a
wall of the 3x3 block it completed).  ADR-021 measured that on
hand-made Kruskal-like trees; these tests repeat it with the real
algorithm and the real generator.
"""
from __future__ import annotations

from typing import Any, Callable

import pytest

from mazegen import braiding
from mazegen.algorithms import available
from mazegen.generator import MazeGenerator
from mazegen.maze import Maze

Judge = Callable[[Maze, int], tuple[Any, str]]


@pytest.mark.parametrize("perfect", [True, False])
@pytest.mark.parametrize("name", available())
def test_every_registered_algorithm_generates(
    name: str, perfect: bool
) -> None:
    # generate() runs the validator itself: returning is passing.  With
    # no stub left in the registry, no algorithm may raise.
    for width, height in [(3, 3), (9, 7), (20, 15), (41, 25)]:
        MazeGenerator(
            width, height, perfect=perfect, seed=0, algorithm=name
        ).generate()


@pytest.mark.parametrize("width,height", [(9, 7), (20, 15), (41, 25)])
def test_perfect_mode_for_the_analyzer(
    judge: Judge, width: int, height: int
) -> None:
    for seed in range(3):
        maze = MazeGenerator(
            width, height, perfect=True, seed=seed, algorithm="kruskal"
        ).generate()
        _, verdict = judge(maze, 0)
        assert verdict.startswith("PERFECT maze"), verdict


@pytest.mark.parametrize(
    "width,height", [(3, 3), (4, 4), (9, 7), (20, 15), (41, 25)]
)
def test_playable_mode_is_bonus_grade(
    judge: Judge, width: int, height: int
) -> None:
    for seed in range(3):
        maze = MazeGenerator(
            width, height, perfect=False, seed=seed, algorithm="kruskal"
        ).generate()
        _, verdict = judge(maze, 0)
        assert "bonus-grade" in verdict, verdict


def test_forced_opening_with_real_kruskal(
    judge: Judge, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Measured: about one 3x3 board in seven needs the forced opening.
    # The spy only counts; the real function still does the work.
    calls: list[int] = []
    original = braiding._force_open

    def spy(*args: Any, **kwargs: Any) -> None:
        calls.append(1)
        original(*args, **kwargs)

    monkeypatch.setattr(braiding, "_force_open", spy)
    forced: list[Maze] = []
    for seed in range(200):
        before = len(calls)
        maze = MazeGenerator(
            3, 3, perfect=False, seed=seed, algorithm="kruskal"
        ).generate()
        if len(calls) > before:
            forced.append(maze)
    assert forced, "the forced opening was never reached"
    for maze in forced:
        _, verdict = judge(maze, 0)
        assert "bonus-grade" in verdict, verdict
