"""Reading of the ``KEY=VALUE`` configuration file.

Grammar:

* one ``KEY=VALUE`` pair per line, spaces around ``=`` are ignored;
* lines starting with ``#`` and empty lines are ignored;
* keys are case insensitive: ``width=20`` is as valid as ``WIDTH=20``;
* mandatory keys: ``WIDTH``, ``HEIGHT``, ``ENTRY``, ``EXIT``,
  ``OUTPUT_FILE``, ``PERFECT``;
* optional keys: ``SEED`` (integer), ``ALGORITHM`` (name of a carving
  algorithm), ``PATTERN`` (text to draw, empty to draw nothing);
* coordinates are written ``x,y``;
* booleans accept ``True`` and ``False`` in any case.

The parser checks the syntax and the type of every value.  Whether the
values make a possible maze (size, entry and exit inside the grid, an
existing algorithm) is checked by :class:`mazegen.MazeGenerator`, so
each rule lives in a single place.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from mazegen.errors import ConfigError
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

DEFAULT_ALGORITHM: str = "backtracker"


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
    algorithm: str = DEFAULT_ALGORITHM
    pattern: str | None = PATTERN


def _read_lines(path: str | Path) -> list[str]:
    """Return the lines of the file, or explain why it cannot be read.

    Raises:
        ConfigError: If the file is missing, unreadable or not text.
    """
    try:
        with open(path, encoding="utf-8") as config_file:
            return config_file.readlines()
    except OSError as error:
        raise ConfigError(
            f"cannot read configuration file {str(path)!r}: "
            f"{error.strerror or error}"
        ) from error
    except UnicodeDecodeError as error:
        raise ConfigError(
            f"configuration file {str(path)!r} is not a text file"
        ) from error


def _split_pairs(lines: list[str]) -> dict[str, str]:
    """Turn the meaningful lines into a ``KEY -> raw value`` mapping.

    Keys are upper-cased here, so the rest of the parser only ever sees
    one spelling.

    Raises:
        ConfigError: On a line without ``=``, an empty key, an unknown
            key or a key given twice, naming the line number.
    """
    known = MANDATORY_KEYS + OPTIONAL_KEYS
    pairs: dict[str, str] = {}
    for number, line in enumerate(lines, start=1):
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        if "=" not in text:
            raise ConfigError(
                f"line {number}: expected KEY=VALUE, got {text!r}"
            )
        raw_key, value = text.split("=", 1)
        key = raw_key.strip().upper()
        if key not in known:
            raise ConfigError(
                f"line {number}: unknown key {raw_key.strip()!r}, "
                f"expected one of {', '.join(known)}"
            )
        if key in pairs:
            raise ConfigError(f"line {number}: key {key} is set twice")
        pairs[key] = value.strip()
    return pairs


def parse_config(path: str | Path) -> Config:
    """Read and validate a configuration file.

    An optional key written with an empty value falls back to its
    default, except ``PATTERN``, where empty means "draw nothing".

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
    pairs = _split_pairs(_read_lines(path))
    missing = [key for key in MANDATORY_KEYS if key not in pairs]
    if missing:
        raise ConfigError(f"missing mandatory key(s): {', '.join(missing)}")
    if not pairs["OUTPUT_FILE"]:
        raise ConfigError("OUTPUT_FILE cannot be empty")
    seed = pairs.get("SEED", "")
    pattern = pairs.get("PATTERN", PATTERN)
    return Config(
        width=parse_int(pairs["WIDTH"], "WIDTH"),
        height=parse_int(pairs["HEIGHT"], "HEIGHT"),
        entry=parse_coords(pairs["ENTRY"], "ENTRY"),
        exit=parse_coords(pairs["EXIT"], "EXIT"),
        output_file=pairs["OUTPUT_FILE"],
        perfect=parse_bool(pairs["PERFECT"], "PERFECT"),
        seed=parse_int(seed, "SEED") if seed else None,
        algorithm=pairs.get("ALGORITHM") or DEFAULT_ALGORITHM,
        pattern=pattern or None,
    )


def parse_int(raw: str, key: str) -> int:
    """Parse an integer value.

    Args:
        raw: The value as written in the file.
        key: The key it belongs to, for the error message.

    Returns:
        The integer.

    Raises:
        ConfigError: If ``raw`` is not an integer.
    """
    try:
        return int(raw)
    except ValueError as error:
        raise ConfigError(
            f"{key} must be an integer, got {raw!r}"
        ) from error


def parse_bool(raw: str, key: str) -> bool:
    """Parse ``True`` or ``False``, in any case.

    Args:
        raw: The value as written in the file.
        key: The key it belongs to, for the error message.

    Returns:
        The boolean.

    Raises:
        ConfigError: If ``raw`` is not a boolean.
    """
    lowered = raw.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    raise ConfigError(f"{key} must be True or False, got {raw!r}")


def parse_coords(raw: str, key: str) -> Cell:
    """Parse an ``x,y`` pair of coordinates.

    Args:
        raw: The value as written in the file.
        key: The key it belongs to, for the error message.

    Returns:
        The ``(x, y)`` pair.

    Raises:
        ConfigError: If ``raw`` is not two integers separated by a
            comma.
    """
    parts = raw.split(",")
    if len(parts) != 2:
        raise ConfigError(
            f"{key} must be two integers written x,y, got {raw!r}"
        )
    return (parse_int(parts[0].strip(), key),
            parse_int(parts[1].strip(), key))
