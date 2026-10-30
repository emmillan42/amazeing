"""Reading of the ``KEY=VALUE`` configuration file.

Grammar:

* one ``KEY=VALUE`` pair per line, spaces around ``=`` are ignored;
* lines starting with ``#`` and empty lines are ignored;
* mandatory keys: ``WIDTH``, ``HEIGHT``, ``ENTRY``, ``EXIT``,
  ``OUTPUT_FILE``, ``PERFECT``;
* optional keys: ``SEED`` (integer), ``ALGORITHM`` (name of a carving
  algorithm), ``PATTERN`` (text to draw, empty to draw nothing);
* coordinates are written ``x,y``;
* booleans accept ``True`` and ``False`` in any case.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from mazegen.maze import Cell
from mazegen.pattern import PATTERN

MANDATORY_KEYS: tuple[str, ...] = (
    "WIDTH",
    "HEIGHT",
    "ENTRY",
    "EXIT",
    "OUTPUT_FILE",
    "PERFECT",
)

OPTIONAL_KEYS: tuple[str, ...] = ("SEED", "ALGORITHM", "PATTERN")


@dataclass(frozen=True)
class Config:
    """Every option read from the configuration file.

    Attributes:
        width: Number of columns of the maze.
        height: Number of rows of the maze.
        entry: Entry coordinates.
        exit: Exit coordinates.
        output_file: Path of the file to write.
        perfect: ``True`` for a perfect maze.
        seed: Optional seed, for reproducible mazes.
        algorithm: Name of the carving algorithm.
        pattern: Text drawn with blocked cells, ``None`` for none.
    """

    width: int
    height: int
    entry: Cell
    exit: Cell
    output_file: str
    perfect: bool
    seed: int | None = None
    algorithm: str = "backtracker"
    pattern: str | None = PATTERN


def parse_config(path: str | Path) -> Config:
    """Read and validate a configuration file.

    The file is opened through a context manager, so the handle is
    released even when a line turns out to be invalid.

    Args:
        path: Path of the configuration file.

    Returns:
        The parsed configuration.

    Raises:
        ConfigError: If the file is missing or unreadable, if a line is
            not a ``KEY=VALUE`` pair, if a mandatory key is missing, if
            a key is unknown or duplicated, or if a value has the wrong
            type.
    """
    raise NotImplementedError


def parse_int(raw: str, key: str) -> int:
    """Parse an integer value.

    Raises:
        ConfigError: If ``raw`` is not an integer.
    """
    raise NotImplementedError


def parse_bool(raw: str, key: str) -> bool:
    """Parse ``True`` or ``False``, in any case.

    Raises:
        ConfigError: If ``raw`` is not a boolean.
    """
    raise NotImplementedError


def parse_coords(raw: str, key: str) -> Cell:
    """Parse an ``x,y`` pair of coordinates.

    Raises:
        ConfigError: If ``raw`` is not two integers separated by a
            comma.
    """
    raise NotImplementedError
