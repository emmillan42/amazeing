"""Tests of the interactive menu (B4).

``input`` is replaced by a scripted list of answers, so each test reads
like the session of an evaluator at the keyboard.
"""
from __future__ import annotations

import builtins
import re
from collections.abc import Iterator
from pathlib import Path

import pytest

from app.config_parser import Config
from app.menu import Menu
from app.writer import format_maze, write_maze
from mazegen.generator import MazeGenerator


def _script(
    monkeypatch: pytest.MonkeyPatch, answers: list[str]
) -> None:
    """Make ``input`` return ``answers`` in order, then hit end of file."""
    feed: Iterator[str] = iter(answers)

    def fake_input(prompt: str = "") -> str:
        try:
            return next(feed)
        except StopIteration:
            raise EOFError from None

    monkeypatch.setattr(builtins, "input", fake_input)


def _setup(tmp_path: Path) -> tuple[MazeGenerator, Config, Path]:
    """Generate the first maze and write it, as a_maze_ing.py does."""
    output = tmp_path / "maze.txt"
    config = Config(20, 15, (0, 0), (19, 14), str(output), False, seed=3)
    generator = MazeGenerator(20, 15, seed=3)
    write_maze(output, generator.generate())
    return generator, config, output


def _last_screen(captured: str) -> str:
    """Return the last frame printed, without colours."""
    plain = re.sub(r"\033\[[0-9;]*[mHJ]", "", captured)
    return plain.split("=== A-Maze-ing ===")[-1]


def test_quit_right_away(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Choice 5 leaves the loop."""
    _script(monkeypatch, ["5"])
    Menu(*_setup(tmp_path)[:2]).run()
    assert "5. Quit" in capsys.readouterr().out


def test_end_of_input_and_ctrl_c_end_cleanly(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """No answer left, or Ctrl+C: the loop ends without a traceback."""
    _script(monkeypatch, [])
    Menu(*_setup(tmp_path)[:2]).run()

    def interrupt(prompt: str = "") -> str:
        raise KeyboardInterrupt

    monkeypatch.setattr(builtins, "input", interrupt)
    Menu(*_setup(tmp_path)[:2]).run()


def test_toggle_path_and_palette(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The status lines follow choices 2 and 3."""
    _script(monkeypatch, ["2", "3"])
    Menu(*_setup(tmp_path)[:2]).run()
    screen = _last_screen(capsys.readouterr().out)
    assert "(now shown)" in screen and "(now neon)" in screen


def test_unknown_choice_is_reported(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A wrong answer is a message, not an exit."""
    _script(monkeypatch, ["9", "5"])
    Menu(*_setup(tmp_path)[:2]).run()
    assert "unknown choice '9'" in capsys.readouterr().out


def test_regenerate_keeps_the_first_maze_on_disk(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """ADR-009: regenerating never rewrites the output file."""
    generator, config, output = _setup(tmp_path)
    first = output.read_text()
    _script(monkeypatch, ["1", "1", "5"])
    Menu(generator, config).run()
    assert output.read_text() == first


def test_save_writes_the_maze_on_display(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Choice 4 stores the maze currently shown."""
    generator, config, output = _setup(tmp_path)
    _script(monkeypatch, ["1", "4", "5"])
    Menu(generator, config).run()
    assert output.read_text() == format_maze(generator.maze)


def test_save_failure_is_shown_not_fatal(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """An unwritable output file is a message inside the menu."""
    generator, _, _ = _setup(tmp_path)
    broken = Config(20, 15, (0, 0), (19, 14),
                    str(tmp_path / "missing" / "m.txt"), False)
    _script(monkeypatch, ["4", "5"])
    Menu(generator, broken).run()
    assert "error: cannot write output file" in capsys.readouterr().out
