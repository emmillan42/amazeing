"""Every algorithm, both modes, through the analyzer (B9).

The analyzer of the subject is the referee the evaluator will use, so
each registered algorithm is judged by it on files written by the real
writer, with the default ``42`` pattern: ``PERFECT maze`` in perfect
mode, and the no-dead-end bonus grade in playable mode.
"""
from __future__ import annotations

from typing import Any, Callable

import pytest

from mazegen.algorithms import available
from mazegen.generator import MazeGenerator
from mazegen.maze import Maze

Judge = Callable[[Maze, int], tuple[Any, str]]

SIZES: list[tuple[int, int]] = [(3, 3), (9, 7), (20, 15), (41, 25)]


@pytest.mark.parametrize("width,height", SIZES)
@pytest.mark.parametrize("name", available())
def test_perfect_mode(
    judge: Judge, name: str, width: int, height: int
) -> None:
    for seed in range(3):
        maze = MazeGenerator(
            width, height, perfect=True, seed=seed, algorithm=name
        ).generate()
        report, verdict = judge(maze, 0)
        assert report.incoherent == ()
        assert verdict.startswith("PERFECT maze"), verdict


@pytest.mark.parametrize("width,height", SIZES)
@pytest.mark.parametrize("name", available())
def test_playable_mode_is_bonus_grade(
    judge: Judge, name: str, width: int, height: int
) -> None:
    for seed in range(3):
        maze = MazeGenerator(
            width, height, perfect=False, seed=seed, algorithm=name
        ).generate()
        report, verdict = judge(maze, 0)
        assert report.unreachable_key_cells == ()
        assert "bonus-grade" in verdict, verdict
