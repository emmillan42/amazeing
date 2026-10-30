"""Writing of the output file required by the subject.

Layout of the file::

    <one hexadecimal digit per cell, one line per row>
    <empty line>
    <entry x,y>
    <exit x,y>
    <shortest path, as N/E/S/W letters>

Every line ends with ``\\n``, the last one included.
"""
from __future__ import annotations

from pathlib import Path

from mazegen.maze import Maze


def write_maze(path: str | Path, maze: Maze) -> None:
    """Write ``maze`` and its solution to ``path``.

    The maze already carries its entry, its exit and its solution, so
    nothing else has to be passed around.  The file is opened through a
    context manager to release the handle whatever happens.

    Args:
        path: Path of the output file.
        maze: The solved maze to serialise.

    Raises:
        MazeError: If the file cannot be written, typically a missing
            directory or a permission problem.
    """
    raise NotImplementedError
