"""Tests of the output file writer (B5)."""
from __future__ import annotations

from pathlib import Path

import pytest

from app.writer import format_maze, write_maze
from mazegen.errors import MazeError
from mazegen.generator import MazeGenerator
from mazegen.maze import Maze


def _maze() -> Maze:
    """Return a small solved maze."""
    return MazeGenerator(5, 4, seed=1, perfect=True).generate()


def test_layout() -> None:
    """Hex rows, empty line, entry, exit, path, every line ended."""
    maze = _maze()
    text = format_maze(maze)
    lines = text.split("\n")
    assert lines[:maze.height] == maze.to_hex_lines()
    assert lines[maze.height] == ""
    assert lines[maze.height + 1] == "0,0"
    assert lines[maze.height + 2] == "4,3"
    assert lines[maze.height + 3] == maze.solution_string()
    assert text.endswith("\n") and lines[-1] == ""
    assert len(lines) == maze.height + 5


def test_coordinates_are_not_tuples() -> None:
    """``x,y``, never Python's ``(x, y)``: the analyzer reads hex there."""
    assert "(" not in format_maze(_maze())


def test_file_matches_the_format(tmp_path: Path) -> None:
    """The file holds exactly the formatted text, with LF endings."""
    maze = _maze()
    path = tmp_path / "maze.txt"
    write_maze(path, maze)
    assert path.read_bytes() == format_maze(maze).encode()


def test_unwritable_path_is_a_maze_error(tmp_path: Path) -> None:
    """A missing directory gives a message, not an OSError."""
    with pytest.raises(MazeError, match="cannot write output file"):
        write_maze(tmp_path / "missing" / "maze.txt", _maze())


def test_nothing_is_created_on_failure(tmp_path: Path) -> None:
    """Writing into a directory path fails without leaving files."""
    with pytest.raises(MazeError):
        write_maze(tmp_path, _maze())
    assert list(tmp_path.iterdir()) == []
