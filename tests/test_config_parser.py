"""Tests of the configuration parser (B1).

The first block is the evaluation sheet, case by case: the evaluator
edits the default file in front of us, and each edit must end on a
clear message, never on a traceback.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from app.config_parser import Config, parse_config
from mazegen.errors import ConfigError, MazeError

VALID: str = (
    "WIDTH=20\nHEIGHT=15\nENTRY=0,0\nEXIT=19,14\n"
    "OUTPUT_FILE=maze.txt\nPERFECT=False\n"
)


def _write(tmp_path: Path, text: str) -> Path:
    """Write a configuration file and return its path."""
    path = tmp_path / "config.txt"
    path.write_text(text, encoding="utf-8")
    return path


# ----------------------------------------------------------------------
# The five cases of the evaluation sheet
# ----------------------------------------------------------------------

@pytest.mark.parametrize("text,message", [
    (VALID.replace("OUTPUT_FILE=maze.txt\n", ""), "OUTPUT_FILE"),
    (VALID + "no equal sign here\n", "line 7: expected KEY=VALUE"),
    (VALID.replace("WIDTH=20", "WIDTH=twenty"), "WIDTH must be an integer"),
    (VALID.replace("PERFECT=False", "PERFECT=maybe"), "True or False"),
    (VALID.replace("ENTRY=0,0", "ENTRY=0;0"), "ENTRY must be two"),
    (VALID.replace("EXIT=19,14", "EXIT=19,14,3"), "EXIT must be two"),
    (VALID.replace("EXIT=19,14", "EXIT=19,x"), "EXIT must be an integer"),
])
def test_evaluation_sheet_errors(
    tmp_path: Path, text: str, message: str
) -> None:
    """Each broken file gives a ConfigError naming what is wrong."""
    with pytest.raises(ConfigError, match=message):
        parse_config(_write(tmp_path, text))


def test_every_error_is_a_maze_error(tmp_path: Path) -> None:
    """a_maze_ing.py catches MazeError only: nothing else may escape."""
    with pytest.raises(MazeError):
        parse_config(_write(tmp_path, "WIDTH\n"))


# ----------------------------------------------------------------------
# What must be accepted
# ----------------------------------------------------------------------

def test_default_file_is_read(tmp_path: Path) -> None:
    """The mandatory keys alone give the documented defaults."""
    config = parse_config(_write(tmp_path, VALID))
    assert config == Config(20, 15, (0, 0), (19, 14), "maze.txt", False)
    assert config.seed is None
    assert config.algorithm == "backtracker"
    assert config.pattern == "42"


def test_lowercase_keys_and_values(tmp_path: Path) -> None:
    """The sheet says width=20 is as valid as WIDTH=20."""
    text = VALID.lower().replace("maze.txt", "Maze.TXT")
    config = parse_config(_write(tmp_path, text))
    assert config.width == 20 and config.perfect is False
    assert config.output_file == "Maze.TXT", "file names keep their case"


def test_comments_blank_lines_and_spaces(tmp_path: Path) -> None:
    """Full-line comments, empty lines and spaces around = are fine."""
    text = "# header\n\n" + VALID.replace("=", " = ") + "   # indented\n"
    assert parse_config(_write(tmp_path, text)).height == 15


def test_windows_line_endings(tmp_path: Path) -> None:
    """A file saved with CRLF endings reads the same."""
    path = tmp_path / "config.txt"
    path.write_bytes(VALID.replace("\n", "\r\n").encode())
    assert parse_config(path).exit == (19, 14)


def test_optional_keys(tmp_path: Path) -> None:
    """SEED, ALGORITHM and PATTERN are read when present."""
    text = VALID + "SEED=-7\nALGORITHM=Kruskal\nPATTERN=4\n"
    config = parse_config(_write(tmp_path, text))
    assert (config.seed, config.algorithm, config.pattern) == (
        -7, "Kruskal", "4"
    )


def test_empty_optional_values(tmp_path: Path) -> None:
    """Empty SEED and ALGORITHM mean default; empty PATTERN, none."""
    text = VALID + "SEED=\nALGORITHM=\nPATTERN=\n"
    config = parse_config(_write(tmp_path, text))
    assert (config.seed, config.algorithm, config.pattern) == (
        None, "backtracker", None
    )


def test_value_may_contain_an_equal_sign(tmp_path: Path) -> None:
    """Only the first = separates the key from the value."""
    text = VALID.replace("maze.txt", "a=b.txt")
    assert parse_config(_write(tmp_path, text)).output_file == "a=b.txt"


# ----------------------------------------------------------------------
# What must be refused, beyond the sheet
# ----------------------------------------------------------------------

@pytest.mark.parametrize("text,message", [
    (VALID + "SEDD=4\n", "unknown key 'SEDD'"),
    (VALID + "WIDTH=30\n", "WIDTH is set twice"),
    (VALID + "=5\n", "unknown key ''"),
    (VALID.replace("maze.txt", ""), "OUTPUT_FILE cannot be empty"),
    (VALID + "SEED=abc\n", "SEED must be an integer"),
    ("", "missing mandatory key"),
])
def test_other_errors(tmp_path: Path, text: str, message: str) -> None:
    """Typos and duplicates are reported, not silently ignored."""
    with pytest.raises(ConfigError, match=message):
        parse_config(_write(tmp_path, text))


def test_missing_file(tmp_path: Path) -> None:
    """A missing file is a ConfigError, not a FileNotFoundError."""
    with pytest.raises(ConfigError, match="cannot read"):
        parse_config(tmp_path / "nope.txt")


def test_directory_instead_of_file(tmp_path: Path) -> None:
    """A directory is not readable as a file either."""
    with pytest.raises(ConfigError, match="cannot read"):
        parse_config(tmp_path)


def test_binary_file(tmp_path: Path) -> None:
    """Bytes that are not UTF-8 text are refused with a message."""
    path = tmp_path / "config.txt"
    path.write_bytes(b"\xff\xfe\x00WIDTH=20")
    with pytest.raises(ConfigError, match="not a text file"):
        parse_config(path)


def test_geometry_is_left_to_the_generator(tmp_path: Path) -> None:
    """The parser checks types; the maze rules live in MazeGenerator."""
    text = VALID.replace("WIDTH=20", "WIDTH=-5")
    assert parse_config(_write(tmp_path, text)).width == -5
