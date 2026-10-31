"""C3: the edge cases of PLAN §5, run through the real entry point.

Every case starts from the repository's ``config.txt`` and changes one
thing, the way the evaluator edits it during the defence.  The test
calls :func:`a_maze_ing.main` in-process, so an exception that escapes
``main`` fails the test: that is exactly a traceback on screen.

Messages produced by the parser are checked word for word.  Messages
produced by the generator are only checked for the ``error:`` prefix:
their wording belongs to ``mazegen`` and has its own tests.

Also covers the four fixes of ADR-030: the "42" warning that the first
screen clear used to erase, the size limit, the single message for a
malformed tuple, the byte order mark and undecodable menu input.
"""
from __future__ import annotations

import builtins
from collections.abc import Iterator
from pathlib import Path

import pytest

from a_maze_ing import main
from app.config_parser import MAX_SIDE, parse_config
from app.menu import CLEAR, Menu
from mazegen.errors import ConfigError
from mazegen.generator import MazeGenerator

REPO_CONFIG: Path = Path(__file__).resolve().parent.parent / "config.txt"
"""The default configuration, the evaluator's starting point."""

SMALL_WARNING: str = "too small for the '42' pattern"


def base_config(tmp_path: Path) -> str:
    """Return the repository's ``config.txt`` writing into ``tmp_path``.

    The output file is redirected so that no test writes into the
    repository.
    """
    text = REPO_CONFIG.read_text(encoding="utf-8")
    return edit(
        text,
        "OUTPUT_FILE=maze.txt",
        f"OUTPUT_FILE={tmp_path / 'maze.txt'}",
    )


def edit(text: str, old: str, new: str) -> str:
    """Replace ``old`` by ``new``, failing if ``old`` is not there.

    Without the check, a change to ``config.txt`` would make a case
    test the unchanged file and pass for the wrong reason.
    """
    assert old in text, f"{old!r} is no longer in config.txt"
    return text.replace(old, new, 1)


def run_main(
    tmp_path: Path,
    text: str,
    monkeypatch: pytest.MonkeyPatch,
    answers: tuple[str, ...] = ("5",),
) -> int:
    """Write ``text`` as a configuration and run the program on it.

    Args:
        tmp_path: Where to write the configuration.
        text: The configuration.
        monkeypatch: Used to feed ``answers`` to ``input``.
        answers: What the user types in the menu, one per prompt.

    Returns:
        The exit code returned by :func:`main`.
    """
    path = tmp_path / "case.txt"
    path.write_text(text, encoding="utf-8")
    feed: Iterator[str] = iter(answers)
    monkeypatch.setattr(builtins, "input", lambda _prompt="": next(feed))
    return main(["a_maze_ing.py", str(path)])


# ----------------------------------------------------------------------
# PLAN §5, one edit of config.txt per case
# ----------------------------------------------------------------------

PARSER_CASES: list[tuple[str, str, str, str]] = [
    ("WIDTH=abc", "WIDTH=20", "WIDTH=abc",
     "WIDTH must be an integer, got 'abc'"),
    ("PERFECT=quiza", "PERFECT=False", "PERFECT=quiza",
     "PERFECT must be True or False, got 'quiza'"),
    ("ENTRY=3", "ENTRY=0,0", "ENTRY=3",
     "ENTRY must be two integers written x,y, got '3'"),
    ("ENTRY=a,b", "ENTRY=0,0", "ENTRY=a,b",
     "ENTRY must be two integers written x,y, got 'a,b'"),
    ("ENTRY=(0,0)", "ENTRY=0,0", "ENTRY=(0,0)",
     "ENTRY must be two integers written x,y, got '(0,0)'"),
    ("EXIT=19;14", "EXIT=19,14", "EXIT=19;14",
     "EXIT must be two integers written x,y, got '19;14'"),
    ("missing WIDTH", "WIDTH=20\n", "",
     "missing mandatory key(s): WIDTH"),
    ("line without =", "WIDTH=20\n", "WIDTH=20\nHELLO\n",
     "expected KEY=VALUE, got 'HELLO'"),
    ("duplicated key", "HEIGHT=15\n", "HEIGHT=15\nwidth=30\n",
     "key WIDTH is set twice"),
    ("misspelt key", "# SEED=42", "SEDD=42",
     "unknown key 'SEDD'"),
    ("WIDTH over the limit", "WIDTH=20", f"WIDTH={MAX_SIDE + 1}",
     f"WIDTH must be at most {MAX_SIDE}"),
    # Just over the limit on purpose: if the limit is ever removed, this
    # case still builds a small maze instead of exhausting the memory.
    ("HEIGHT over the limit", "HEIGHT=15", f"HEIGHT={MAX_SIDE + 1}",
     f"HEIGHT must be at most {MAX_SIDE}"),
]


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [case[1:] for case in PARSER_CASES],
    ids=[case[0] for case in PARSER_CASES],
)
def test_parser_cases_end_with_a_clear_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    old: str,
    new: str,
    message: str,
) -> None:
    """Each malformed file gives its own message and exit code 1."""
    text = edit(base_config(tmp_path), old, new)
    assert run_main(tmp_path, text, monkeypatch) == 1
    err = capsys.readouterr().err
    assert err.startswith("error: ")
    assert message in err


GENERATOR_CASES: list[tuple[str, str, str]] = [
    ("WIDTH=1", "WIDTH=20", "WIDTH=1"),
    ("HEIGHT=0", "HEIGHT=15", "HEIGHT=0"),
    ("negative WIDTH", "WIDTH=20", "WIDTH=-5"),
    ("ENTRY equals EXIT", "ENTRY=0,0", "ENTRY=19,14"),
    ("ENTRY outside", "ENTRY=0,0", "ENTRY=20,0"),
    ("negative ENTRY", "ENTRY=0,0", "ENTRY=-1,0"),
    ("EXIT outside", "EXIT=19,14", "EXIT=19,15"),
    ("PATTERN without glyph", "# PATTERN=42", "PATTERN=7"),
    ("unknown algorithm", "# ALGORITHM=backtracker", "ALGORITHM=prim"),
]


@pytest.mark.parametrize(
    ("old", "new"),
    [case[1:] for case in GENERATOR_CASES],
    ids=[case[0] for case in GENERATOR_CASES],
)
def test_impossible_mazes_end_with_a_clear_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    old: str,
    new: str,
) -> None:
    """A well-formed file asking for an impossible maze: exit code 1."""
    text = edit(base_config(tmp_path), old, new)
    assert run_main(tmp_path, text, monkeypatch) == 1
    assert capsys.readouterr().err.startswith("error: ")


def test_missing_config_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A path that does not exist is reported, not raised."""
    assert main(["a_maze_ing.py", str(tmp_path / "nope.txt")]) == 1
    assert "cannot read configuration file" in capsys.readouterr().err


def test_empty_output_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """``OUTPUT_FILE=`` is refused by the parser, before generating."""
    text = edit(
        base_config(tmp_path),
        f"OUTPUT_FILE={tmp_path / 'maze.txt'}",
        "OUTPUT_FILE=",
    )
    assert run_main(tmp_path, text, monkeypatch) == 1
    assert "OUTPUT_FILE cannot be empty" in capsys.readouterr().err


def test_output_directory_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """An output file in a missing directory is reported, not raised."""
    text = edit(
        base_config(tmp_path),
        f"OUTPUT_FILE={tmp_path / 'maze.txt'}",
        f"OUTPUT_FILE={tmp_path / 'no' / 'dir' / 'maze.txt'}",
    )
    assert run_main(tmp_path, text, monkeypatch) == 1
    assert capsys.readouterr().err.startswith("error: ")


@pytest.mark.parametrize("stop", [EOFError, KeyboardInterrupt])
def test_ctrl_d_and_ctrl_c_in_the_menu(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    stop: type[BaseException],
) -> None:
    """``Ctrl+D`` and ``Ctrl+C`` at the prompt end the program cleanly."""
    def interrupted(_prompt: str = "") -> str:
        raise stop

    path = tmp_path / "case.txt"
    path.write_text(base_config(tmp_path), encoding="utf-8")
    monkeypatch.setattr(builtins, "input", interrupted)
    assert main(["a_maze_ing.py", str(path)]) == 0


def test_invalid_menu_choices_keep_the_menu_open(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Letters, numbers out of range and empty lines are only reported."""
    code = run_main(
        tmp_path, base_config(tmp_path), monkeypatch,
        answers=("a", "9", "", "0", "5"),
    )
    assert code == 0
    out = capsys.readouterr().out
    for choice in ("'a'", "'9'", "''", "'0'"):
        assert f"unknown choice {choice}" in out


# ----------------------------------------------------------------------
# ADR-030: the fixes
# ----------------------------------------------------------------------

def test_pattern_warning_survives_the_screen_clear(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The "42 does not fit" warning is on the screen the user sees.

    Before ADR-030 it was printed on ``stderr`` and then erased by the
    first frame of the menu, which starts with a screen clear.
    """
    text = base_config(tmp_path)
    text = edit(text, "WIDTH=20", "WIDTH=5")
    text = edit(text, "HEIGHT=15", "HEIGHT=5")
    text = edit(text, "EXIT=19,14", "EXIT=4,4")
    assert run_main(tmp_path, text, monkeypatch) == 0
    captured = capsys.readouterr()
    assert SMALL_WARNING in captured.err
    last_screen = captured.out.rsplit(CLEAR, 1)[-1]
    assert SMALL_WARNING in last_screen


def test_no_warning_when_the_pattern_fits(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The default 20x15 maze draws the "42" and warns about nothing."""
    assert run_main(tmp_path, base_config(tmp_path), monkeypatch) == 0
    captured = capsys.readouterr()
    assert SMALL_WARNING not in captured.out + captured.err


def test_menu_notice_stays_on_every_screen(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The notice outlives messages, regenerations and bad choices."""
    config = parse_config(_write(tmp_path, base_config(tmp_path)))
    generator = MazeGenerator(9, 7, seed=1)
    generator.generate()
    feed: Iterator[str] = iter(["1", "2", "3", "x", "5"])
    monkeypatch.setattr(builtins, "input", lambda _prompt="": next(feed))
    Menu(generator, config, notice="NOTICE").run()
    screens = capsys.readouterr().out.split(CLEAR)[1:]
    assert len(screens) == 5
    assert all("NOTICE" in screen for screen in screens)


def test_undecodable_input_is_an_invalid_choice(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Bytes that are not UTF-8 at the prompt do not end the program."""
    answers: Iterator[str | None] = iter([None, "5"])

    def fake_input(_prompt: str = "") -> str:
        answer = next(answers)
        if answer is None:
            raise UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid")
        return answer

    path = _write(tmp_path, base_config(tmp_path))
    monkeypatch.setattr(builtins, "input", fake_input)
    assert main(["a_maze_ing.py", str(path)]) == 0
    assert "unreadable input" in capsys.readouterr().out


def test_side_limit_is_inclusive(tmp_path: Path) -> None:
    """``MAX_SIDE`` itself is accepted; only parsing, nothing is built."""
    text = edit(base_config(tmp_path), "WIDTH=20", f"WIDTH={MAX_SIDE}")
    assert parse_config(_write(tmp_path, text)).width == MAX_SIDE


def test_side_limit_does_not_hide_the_minimum(tmp_path: Path) -> None:
    """A negative size passes the parser: the generator owns the minimum."""
    text = edit(base_config(tmp_path), "WIDTH=20", "WIDTH=-5")
    assert parse_config(_write(tmp_path, text)).width == -5


@pytest.mark.parametrize("raw", ["3, 4", " 3 ,4 ", "+3,4"])
def test_coordinates_tolerate_spaces_and_signs(
    tmp_path: Path, raw: str
) -> None:
    """The single ``except`` did not make the tuple parser stricter."""
    text = edit(base_config(tmp_path), "ENTRY=0,0", f"ENTRY={raw}")
    assert parse_config(_write(tmp_path, text)).entry == (3, 4)


def test_byte_order_mark_is_ignored(tmp_path: Path) -> None:
    """A file saved "UTF-8 with BOM" reads like the plain one."""
    path = tmp_path / "bom.txt"
    path.write_bytes(
        b"\xef\xbb\xbf" + base_config(tmp_path).encode("utf-8")
    )
    plain = parse_config(_write(tmp_path, base_config(tmp_path)))
    assert parse_config(path) == plain


def test_huge_size_is_refused_before_allocating(tmp_path: Path) -> None:
    """The limit answers before any memory is used.

    Without it, ``Maze`` builds ``height`` lists of ``width + 1``
    booleans and the process dies of ``MemoryError`` or is killed by
    the system.
    """
    text = edit(base_config(tmp_path), "WIDTH=20", "WIDTH=100000000")
    with pytest.raises(ConfigError, match="at most"):
        parse_config(_write(tmp_path, text))


def _write(tmp_path: Path, text: str) -> Path:
    """Write ``text`` to a configuration file and return its path."""
    path = tmp_path / "config.txt"
    path.write_text(text, encoding="utf-8")
    return path
