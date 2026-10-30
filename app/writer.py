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

from mazegen.errors import MazeError
from mazegen.maze import Maze


def format_maze(maze: Maze) -> str:
    """Return the whole content of the output file for ``maze``.

    Kept apart from :func:`write_maze` so the format can be tested
    without touching the disk, and so nothing is opened before the
    text is complete.
    """
    entry_x, entry_y = maze.entry
    exit_x, exit_y = maze.exit
    lines = [
        *maze.to_hex_lines(),
        "",
        f"{entry_x},{entry_y}",
        f"{exit_x},{exit_y}",
        maze.solution_string(),
    ]
    return "\n".join(lines) + "\n"


def write_maze(path: str | Path, maze: Maze) -> None:
    """Write ``maze`` and its solution to ``path``.

    The maze already carries its entry, its exit and its solution, so
    nothing else has to be passed around.  ``newline="\\n"`` keeps the
    line endings the subject asks for on every system.

    Args:
        path: Path of the output file.
        maze: The solved maze to serialise.

    Raises:
        MazeError: If the file cannot be written, typically a missing
            directory or a permission problem.
    """
    text = format_maze(maze)
    try:
        with open(path, "w", encoding="utf-8", newline="\n") as out:
            out.write(text)
    except OSError as error:
        raise MazeError(
            f"cannot write output file {str(path)!r}: "
            f"{error.strerror or error}"
        ) from error
