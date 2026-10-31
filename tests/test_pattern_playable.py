"""The analyzer on boards with an odd pattern (A9, ADR-025).

Before ADR-025, ``PATTERN=4`` blocked every centre cell the analyzer
looks at, and the verdict was "Not Pac-Man-ready" with zero dead ends.
"""
from __future__ import annotations

from typing import Any, Callable

import pytest

from mazegen.generator import MazeGenerator
from mazegen.maze import Maze

Judge = Callable[[Maze, int], tuple[Any, str]]


@pytest.mark.parametrize("width,height", [(9, 7), (20, 15)])
@pytest.mark.parametrize("seed", [0, 1, 42])
def test_pattern_4_is_usable(
    judge: Judge, width: int, height: int, seed: int
) -> None:
    maze = MazeGenerator(
        width, height, perfect=False, seed=seed, pattern="4"
    ).generate()
    report, verdict = judge(maze, 0)
    assert report.unreachable_key_cells == ()
    assert verdict.startswith("Pac-Man-USABLE"), verdict


@pytest.mark.parametrize("text", ["2", "424"])
def test_other_odd_texts_are_usable(judge: Judge, text: str) -> None:
    maze = MazeGenerator(
        20, 15, perfect=False, seed=42, pattern=text
    ).generate()
    report, verdict = judge(maze, 0)
    assert report.unreachable_key_cells == ()
    assert verdict.startswith("Pac-Man-USABLE"), verdict
