"""ASCII rendering of a maze, with ANSI colours.

MiniLibX would need ctypes bindings and a working X server; box
drawing characters plus ANSI escapes need nothing at all, work on every
campus machine, and make colour rotation a one-line change.

The drawing is a grid of ``2 * width + 1`` by ``2 * height + 1``
characters: odd positions are cells, even ones the walls between them.
"""
from __future__ import annotations

from dataclasses import dataclass

from mazegen.maze import Maze

RESET: str = "\033[0m"


@dataclass(frozen=True)
class Palette:
    """The ANSI escapes used to draw one frame.

    Attributes:
        name: Name shown in the menu.
        walls: Colour of the walls.
        pattern: Colour of the "42" pattern.
        path: Colour of the shortest path.
        entry: Colour of the entry cell.
        exit: Colour of the exit cell.
    """

    name: str
    walls: str
    pattern: str
    path: str
    entry: str
    exit: str


PALETTES: tuple[Palette, ...] = (
    Palette("white", RESET, "\033[37m", "\033[96m", "\033[95m",
            "\033[91m"),
    Palette("amber", "\033[33m", "\033[93m", "\033[97m", "\033[95m",
            "\033[91m"),
    Palette("green", "\033[32m", "\033[92m", "\033[96m", "\033[95m",
            "\033[91m"),
)


def render(
    maze: Maze, show_path: bool = False, palette: Palette = PALETTES[0]
) -> str:
    """Return the whole maze as a printable string.

    Args:
        maze: The maze to draw.
        show_path: Whether to highlight the stored shortest path.
        palette: The colours to use.

    Returns:
        The frame, newline separated, ready for ``print``.
    """
    raise NotImplementedError
