"""The ``42`` pattern, drawn with fully closed cells.

Each digit is a 3x5 bitmap with one-cell strokes, and the two digits
are separated by one free column.  ``#`` marks a cell to block, ``.`` a
cell left to the generator::

    #.# ###
    #.# ..#
    ### ###
    ..# #..
    ..# ###

The block always keeps at least :data:`MARGIN` free cells between
itself and the outer border, so the remaining cells form a connected
ring around it.

Placement (ADR-025).  The block goes as close to the centre as
possible, with one extra condition: the grid column ``(W - 1) // 2``
must cross no cell of the pattern.  That column holds the centre of
:meth:`Maze.centre` and is one of the centre columns the analyzer
checks, so with the whole column free the centre is a corridor
whatever the row.  With an even number of glyphs the centred block
already has a separating column there and nothing moves, so the ``42``
is exactly where it always was.  With an odd number the centred block
puts the middle column of a glyph there, and the block moves two
columns.

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


def _block(text: str) -> tuple[str, ...]:
    """Return the rows of the whole block drawing ``text``.

    The glyphs are laid side by side with :data:`GAP` free columns
    between them; a glyph shorter than the others is padded with free
    rows at the bottom.  Every other function reads the pattern from
    here, so the layout lives in a single place.

    Raises:
        ConfigError: If ``text`` is empty or uses a character with no
            glyph.  It is a configuration error, not a "does not fit":
            the caller must report it instead of silently skipping the
            pattern.
    """
    if not text:
        raise ConfigError("the pattern text is empty")
    try:
        bitmaps = [GLYPHS[char] for char in text]
    except KeyError as error:
        raise ConfigError(
            f"no glyph for character {error.args[0]!r}, "
            f"available: {', '.join(sorted(GLYPHS))}"
        ) from error
    height = max(len(bitmap) for bitmap in bitmaps)
    gap = "." * GAP
    return tuple(
        gap.join(
            bitmap[row] if row < len(bitmap) else "." * len(bitmap[0])
            for bitmap in bitmaps
        )
        for row in range(height)
    )


def glyph_size(text: str = PATTERN) -> Cell:
    """Return the ``(width, height)`` of the block drawing ``text``.

    Raises:
        ConfigError: If ``text`` is empty or has a character with no
            glyph.
    """
    block = _block(text)
    return (len(block[0]), len(block))


def _origin(width: int, height: int, text: str) -> Cell | None:
    """Return the top-left cell of the block, or ``None`` if it does not fit.

    Among the columns where the block keeps its margin on both sides,
    only those leaving the grid column ``(width - 1) // 2`` free are
    valid: either that column falls outside the block, or it crosses a
    column of the block with no ``#``.  The valid one closest to the
    centred position wins, and a tie goes east, the side that receives
    the extra column when the free space is odd.  The row is always
    the centred one: no row of the glyphs is entirely free, so moving
    vertically would never help.

    Args:
        width: Number of columns of the maze.
        height: Number of rows of the maze.
        text: Characters to draw.

    Returns:
        ``(x0, y0)``, or ``None`` when no column is valid.
    """
    block = _block(text)
    block_width, block_height = len(block[0]), len(block)
    if height < block_height + 2 * MARGIN:
        return None
    centre_column = (width - 1) // 2
    blank = {
        col for col in range(block_width)
        if all(row[col] != "#" for row in block)
    }
    valid = [
        x0
        for x0 in range(MARGIN, width - block_width - MARGIN + 1)
        if not 0 <= centre_column - x0 < block_width
        or centre_column - x0 in blank
    ]
    if not valid:
        return None
    centred = (width - block_width) // 2
    x0 = min(valid, key=lambda x: (abs(x - centred), -x))
    return (x0, (height - block_height) // 2)


def minimum_grid(text: str = PATTERN) -> Cell:
    """Return the smallest maze able to hold ``text`` and its margin.

    The height only needs the margin.  The width is searched upwards
    from the block plus its margin: with an even number of glyphs the
    first try already fits, with an odd number it takes three more
    columns, so ``4n + 4`` instead of ``4n + 1`` (ADR-025).  The loop
    always ends: once the grid is about twice as wide as the block, the
    block fits entirely east of the centre column, which is then free.

    Raises:
        ConfigError: If ``text`` is empty or has a character with no
            glyph.
    """
    block_width, block_height = glyph_size(text)
    width = block_width + 2 * MARGIN
    height = block_height + 2 * MARGIN
    while _origin(width, height, text) is None:
        width += 1
    return (width, height)


def fits(width: int, height: int, text: str = PATTERN) -> bool:
    """Tell whether ``text`` fits in a ``width`` x ``height`` maze."""
    return _origin(width, height, text) is not None


def cells_for(
    width: int, height: int, text: str = PATTERN
) -> set[Cell]:
    """Return the cells to block to draw ``text``.

    Args:
        width: Number of columns of the maze.
        height: Number of rows of the maze.
        text: Characters to draw, ``42`` by default.

    Returns:
        The absolute coordinates of every cell of the pattern.

    Raises:
        ConfigError: If ``text`` is empty or has a character with no
            glyph.
        PatternTooLargeError: If the pattern does not fit.
    """
    origin = _origin(width, height, text)
    if origin is None:
        min_width, min_height = minimum_grid(text)
        raise PatternTooLargeError(
            f"the {text!r} pattern needs at least "
            f"{min_width}x{min_height}, got {width}x{height}"
        )
    x0, y0 = origin
    return {
        (x0 + col, y0 + row)
        for row, line in enumerate(_block(text))
        for col, mark in enumerate(line)
        if mark == "#"
    }


def stamp(maze: Maze, text: str = PATTERN) -> set[Cell]:
    """Block every cell of the pattern in ``maze``.

    Args:
        maze: The empty maze to stamp.
        text: Characters to draw, ``42`` by default.

    Returns:
        The cells that were blocked.

    Raises:
        ConfigError: If ``text`` is empty or has a character with no
            glyph.
        PatternTooLargeError: If the pattern does not fit in the maze.
    """
    cells = cells_for(maze.width, maze.height, text)
    for x, y in cells:
        maze.block(x, y)
    return cells
