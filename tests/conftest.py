"""Fixtures shared by several test modules.

Test modules cannot import each other (ADR-018), so anything two of
them need lives here as a fixture.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Callable

import pytest

from app.writer import write_maze
from mazegen.maze import Maze

ANALYZER: Path = Path(__file__).resolve().parent.parent / "maze_analyzer.py"


@pytest.fixture
def analyzer() -> ModuleType:
    """Import the analyzer of the intra, or skip when there is no copy.

    The module is registered in ``sys.modules`` before running it: its
    ``@dataclass`` looks itself up there, and fails otherwise.  If
    another test already imported it, that copy is reused.
    """
    loaded = sys.modules.get("maze_analyzer")
    if loaded is not None:
        return loaded
    if not ANALYZER.is_file():
        pytest.skip("no local copy of maze_analyzer.py")
    spec = importlib.util.spec_from_file_location("maze_analyzer", ANALYZER)
    if spec is None or spec.loader is None:
        pytest.skip("maze_analyzer.py cannot be imported")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def judge(
    analyzer: ModuleType, tmp_path: Path
) -> Callable[[Maze, int], tuple[Any, str]]:
    """Return a function that writes a maze and asks the analyzer.

    The maze goes through the real writer, as the evaluator will see
    it.  The function returns the analyzer report and its verdict line,
    with the default ``--min-loops`` and the ``--max-dead-ends`` given.
    """
    def run(maze: Maze, max_dead_ends: int) -> tuple[Any, str]:
        path = tmp_path / "maze.txt"
        write_maze(str(path), maze)
        report = analyzer.analyze(analyzer.Maze.from_file(str(path)))
        verdict = analyzer.verdict(
            report, analyzer.DEFAULT_MIN_LOOPS, max_dead_ends
        )
        return report, str(verdict)

    return run
