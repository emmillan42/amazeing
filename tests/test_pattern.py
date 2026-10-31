"""Tests for the pattern placement (A9, ADR-025).

The old placement is rewritten here as a reference, centred and
nothing else, so the ``42`` can be compared with what it always was.
"""
from __future__ import annotations

import itertools

import pytest

from mazegen.errors import ConfigError, PatternTooLargeError
from mazegen.maze import ALL_WALLS, Cell, Maze
from mazegen.pattern import (
    GLYPHS,
    MARGIN,
    cells_for,
    fits,
    glyph_size,
    minimum_grid,
    stamp,
)

TEXTS: list[str] = [
    "".join(chars)
    for length in (1, 2, 3)
    for chars in itertools.product(sorted(GLYPHS), repeat=length)
]
EVEN_TEXTS: list[str] = [text for text in TEXTS if len(text) % 2 == 0]
ODD_TEXTS: list[str] = [text for text in TEXTS if len(text) % 2 == 1]


def centred_cells(width: int, height: int, text: str) -> set[Cell]:
    """Return the cells of the placement used before ADR-025."""
    block_width, block_height = glyph_size(text)
    x0 = (width - block_width) // 2
    y0 = (height - block_height) // 2
    cells: set[Cell] = set()
    dx = 0
    for char in text:
        for row, line in enumerate(GLYPHS[char]):
            for col, mark in enumerate(line):
                if mark == "#":
                    cells.add((x0 + dx + col, y0 + row))
        dx += len(GLYPHS[char][0]) + 1
    return cells


def draw(width: int, height: int, text: str) -> list[str]:
    """Return the grid as rows of ``#`` (blocked) and ``.`` (free)."""
    cells = cells_for(width, height, text)
    return [
        "".join("#" if (x, y) in cells else "." for x in range(width))
        for y in range(height)
    ]


def sizes_from_minimum(text: str) -> list[tuple[int, int]]:
    """Return every size from the minimum up to a generous bound."""
    min_width, min_height = minimum_grid(text)
    return [
        (width, height)
        for width in range(min_width, min_width + 16)
        for height in range(min_height, min_height + 5)
    ]


@pytest.mark.parametrize(
    "text,expected",
    [("42", (9, 7)), ("4", (8, 7)), ("2", (8, 7)), ("424", (16, 7)),
     ("2442", (17, 7))],
)
def test_minimum_grid(text: str, expected: tuple[int, int]) -> None:
    # 4n + 1 with an even n, 4n + 4 with an odd one; the height is the
    # glyph plus its margin in every case.
    assert minimum_grid(text) == expected


@pytest.mark.parametrize("text", TEXTS)
def test_minimum_is_exact_and_every_wider_grid_fits(text: str) -> None:
    min_width, min_height = minimum_grid(text)
    assert not fits(min_width - 1, min_height, text)
    assert not fits(min_width, min_height - 1, text)
    for width in range(min_width, 81):
        assert fits(width, min_height, text), width


@pytest.mark.parametrize("text", TEXTS)
def test_centre_column_is_free(text: str) -> None:
    # The analyzer looks at W // 2, or W / 2 - 1 and W / 2: both
    # include (W - 1) // 2, the column that must stay free.
    for width, height in sizes_from_minimum(text):
        column = (width - 1) // 2
        cells = cells_for(width, height, text)
        assert all(x != column for x, _ in cells), (width, height)


@pytest.mark.parametrize("text", TEXTS)
def test_margin_is_kept(text: str) -> None:
    for width, height in sizes_from_minimum(text):
        for x, y in cells_for(width, height, text):
            assert MARGIN <= x < width - MARGIN, (width, height)
            assert MARGIN <= y < height - MARGIN, (width, height)


@pytest.mark.parametrize("text", TEXTS)
def test_centre_is_the_geometric_one(text: str) -> None:
    # With the column free, Maze.centre() never has to look elsewhere.
    for width, height in sizes_from_minimum(text):
        maze = Maze(width, height)
        stamp(maze, text)
        assert maze.centre() == ((width - 1) // 2, (height - 1) // 2)


@pytest.mark.parametrize("text", EVEN_TEXTS + ["4242", "2442"])
def test_even_texts_do_not_move(text: str) -> None:
    min_width, min_height = minimum_grid(text)
    for width in range(min_width, 41):
        for height in range(min_height, 21):
            assert cells_for(width, height, text) == centred_cells(
                width, height, text
            ), (width, height)


@pytest.mark.parametrize("text", ODD_TEXTS)
def test_odd_texts_move_two_columns_east(text: str) -> None:
    # Every glyph has a "#" in its first column, so the leftmost
    # blocked cell is the left edge of the block.
    for width, height in sizes_from_minimum(text):
        block_width, _ = glyph_size(text)
        centred = (width - block_width) // 2
        x0 = min(x for x, _ in cells_for(width, height, text))
        assert x0 - centred == 2, (width, height)


def test_42_drawing_in_the_minimum_grid() -> None:
    assert draw(9, 7, "42") == [
        ".........",
        ".#.#.###.",
        ".#.#...#.",
        ".###.###.",
        "...#.#...",
        "...#.###.",
        ".........",
    ]


def test_4_drawing_in_its_minimum_grid() -> None:
    # Centred it would start at column 2 and block column 3, the
    # centre one; moved two columns east, column 3 is free.
    assert draw(8, 7, "4") == [
        "........",
        "....#.#.",
        "....#.#.",
        "....###.",
        "......#.",
        "......#.",
        "........",
    ]


def test_stamp_closes_every_cell() -> None:
    maze = Maze(20, 15)
    cells = stamp(maze, "4")
    assert cells == maze.blocked
    for x, y in cells:
        assert maze.cell_code(x, y) == ALL_WALLS


def test_too_small_reports_the_new_minimum() -> None:
    with pytest.raises(PatternTooLargeError, match="at least 8x7"):
        cells_for(7, 7, "4")


@pytest.mark.parametrize("text", ["7", "4 2", ""])
def test_bad_text_is_a_config_error(text: str) -> None:
    with pytest.raises(ConfigError):
        fits(20, 15, text)
    with pytest.raises(ConfigError):
        minimum_grid(text)
