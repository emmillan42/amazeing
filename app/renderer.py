"""ASCII rendering of a maze, with ANSI colours.

Every cell is drawn three characters wide.  A row of the maze becomes
two lines of text: its north walls, then its west walls and contents.
A last line draws the south walls of the bottom row, and every
content line ends with the east wall of its last cell, so the whole
border comes from the maze itself, not from a guess.
"""
from __future__ import annotations

from dataclasses import dataclass

from mazegen.maze import Cell, Direction, Maze

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
    Palette("default", walls="\033[34m", pattern="\033[90m",
            path="\033[93m", entry="\033[92m", exit="\033[91m"),
    Palette("neon", walls="\033[92m", pattern="\033[91m",
            path="\033[96m", entry="\033[90m", exit="\033[34m"),
    Palette("plain", walls=RESET, pattern="\033[37m",
            path="\033[96m", entry="\033[95m", exit="\033[91m"),
)


def _paint(text: str, colour: str) -> str:
    """Wrap ``text`` in a colour and a reset."""
    return f"{colour}{text}{RESET}"


def _north_line(maze: Maze, y: int, palette: Palette) -> str:
    """Return the line of north walls of row ``y``."""
    corner = _paint("+", palette.walls)
    parts = [
        corner + (_paint("---", palette.walls)
                  if maze.has_wall(x, y, Direction.NORTH) else "   ")
        for x in range(maze.width)
    ]
    return "".join(parts) + corner


def _south_line(maze: Maze, palette: Palette) -> str:
    """Return the line of south walls of the bottom row."""
    corner = _paint("+", palette.walls)
    y = maze.height - 1
    parts = [
        corner + (_paint("---", palette.walls)
                  if maze.has_wall(x, y, Direction.SOUTH) else "   ")
        for x in range(maze.width)
    ]
    return "".join(parts) + corner


def _content(
    maze: Maze, cell: Cell, path: set[Cell], blocked: frozenset[Cell],
    palette: Palette,
) -> str:
    """Return the three characters drawn inside ``cell``."""
    if cell in blocked:
        return _paint("███", palette.pattern)
    if cell == maze.entry:
        return _paint(" E ", palette.entry)
    if cell == maze.exit:
        return _paint(" X ", palette.exit)
    if cell in path:
        return _paint(" ● ", palette.path)
    return "   "


def _cell_line(
    maze: Maze, y: int, path: set[Cell], blocked: frozenset[Cell],
    palette: Palette,
) -> str:
    """Return the line of west walls and contents of row ``y``."""
    side = _paint("|", palette.walls)
    parts = [
        (side if maze.has_wall(x, y, Direction.WEST) else " ")
        + _content(maze, (x, y), path, blocked, palette)
        for x in range(maze.width)
    ]
    last = maze.width - 1
    end = side if maze.has_wall(last, y, Direction.EAST) else " "
    return "".join(parts) + end


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
    path = set(maze.solution) if show_path else set()
    blocked = maze.blocked
    lines: list[str] = []
    for y in range(maze.height):
        lines.append(_north_line(maze, y, palette))
        lines.append(_cell_line(maze, y, path, blocked, palette))
    lines.append(_south_line(maze, palette))
    return "\n".join(lines)
