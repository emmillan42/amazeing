"""The ``42`` pattern, drawn with fully closed cells.

Each digit is a 3x5 bitmap with one-cell strokes, and the two digits
are separated by one free column.  ``#`` marks a cell to block, ``.`` a
cell left to the generator::

    #.# ###
    #.# ..#
    ### ###
    ..# #..
    ..# ###

The block is centred and always keeps at least :data:`MARGIN` free
cells between itself and the outer border, so the remaining cells form
a connected ring around it.

The pattern is stamped **before** generating: the blocked cells are
removed from the grid the algorithm works on, which is why they end up
with the code ``f`` without any extra step and without breaking
connectivity or the shortest path.
"""
from __future__ import annotations

from mazegen.errors import ConfigError, PatternTooLargeError
from mazegen.maze import Cell, Maze

GLYPHS: dict[str, tuple[str, ...]] = {
    "4": (
        "#.#",
        "#.#",
        "###",
        "..#",
        "..#",
    ),
    "2": (
        "###",
        "..#",
        "###",
        "#..",
        "###",
    ),
}

PATTERN: str = "42"
"""Text drawn by default."""

GAP: int = 1
"""Free columns between two digits."""

MARGIN: int = 1
"""Free cells between the pattern and the outer border."""


def glyph_size(text: str = PATTERN) -> Cell:
    """Return the ``(width, height)`` of the block drawing ``text``.

    Raises:
        ConfigError: If ``text`` uses a character with no glyph.  It is
            a configuration error, not a "does not fit": the caller
            must report it instead of silently skipping the pattern.
    """
    try:
        bitmaps = [GLYPHS[char] for char in text]
    except KeyError as error:
        raise ConfigError(
            f"no glyph for character {error.args[0]!r}, "
            f"available: {', '.join(sorted(GLYPHS))}"
        ) from error
    width = sum(len(bitmap[0]) for bitmap in bitmaps)
    width += GAP * (len(bitmaps) - 1)
    height = max(len(bitmap) for bitmap in bitmaps)
    return (width, height)


def minimum_grid(text: str = PATTERN) -> Cell:
    """Return the smallest maze able to hold ``text`` and its margin."""
    width, height = glyph_size(text)
    return (width + 2 * MARGIN, height + 2 * MARGIN)


def fits(width: int, height: int, text: str = PATTERN) -> bool:
    """Tell whether ``text`` fits in a ``width`` x ``height`` maze."""
    min_width, min_height = minimum_grid(text)
    return width >= min_width and height >= min_height


def cells_for(
    width: int, height: int, text: str = PATTERN
) -> set[Cell]:
    """Return the cells to block to draw ``text``, centred in the grid.

    Args:
        width: Number of columns of the maze.
        height: Number of rows of the maze.
        text: Characters to draw, ``42`` by default.

    Returns:
        The absolute coordinates of every cell of the pattern.

    Raises:
        PatternTooLargeError: If the pattern does not fit.
    """
    if not fits(width, height, text):
        min_width, min_height = minimum_grid(text)
        raise PatternTooLargeError(
            f"the {text!r} pattern needs at least "
            f"{min_width}x{min_height}, got {width}x{height}"
        )
    block_width, block_height = glyph_size(text)
    x0 = (width - block_width) // 2
    y0 = (height - block_height) // 2
    cells: set[Cell] = set()
    dx = 0
    for char in text:
        bitmap = GLYPHS[char]
        for row, line in enumerate(bitmap):
            for col, mark in enumerate(line):
                if mark == "#":
                    cells.add((x0 + dx + col, y0 + row))
        dx += len(bitmap[0]) + GAP
    return cells


def stamp(maze: Maze, text: str = PATTERN) -> set[Cell]:
    """Block every cell of the pattern in ``maze``.

    Args:
        maze: The empty maze to stamp.
        text: Characters to draw, ``42`` by default.

    Returns:
        The cells that were blocked.

    Raises:
        PatternTooLargeError: If the pattern does not fit in the maze.
    """
    cells = cells_for(maze.width, maze.height, text)
    for x, y in cells:
        maze.block(x, y)
    return cells
