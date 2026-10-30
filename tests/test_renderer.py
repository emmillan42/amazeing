"""Tests of the ASCII renderer (B3)."""
from __future__ import annotations

import re

import pytest

from app.renderer import PALETTES, Palette, render
from mazegen.generator import MazeGenerator
from mazegen.maze import Direction, Maze

ANSI = re.compile(r"\033\[[0-9;]*m")


def _plain(text: str) -> list[str]:
    """Strip the colours and split into lines."""
    return ANSI.sub("", text).split("\n")


def _maze(width: int = 20, height: int = 15) -> Maze:
    """Return a solved playable maze."""
    return MazeGenerator(width, height, seed=4).generate()


@pytest.mark.parametrize("size", [(3, 3), (5, 4), (20, 15)])
def test_every_row_and_column_is_drawn(size: tuple[int, int]) -> None:
    """2 lines per row plus one, 4 characters per column plus one."""
    maze = _maze(*size)
    lines = _plain(render(maze))
    assert len(lines) == 2 * maze.height + 1
    assert all(len(line) == 4 * maze.width + 1 for line in lines)


def test_entry_and_exit_are_visible() -> None:
    """The exit sits in the last row and column: it must be drawn."""
    text = "\n".join(_plain(render(_maze())))
    assert text.count(" E ") == 1 and text.count(" X ") == 1


def test_walls_follow_the_maze() -> None:
    """Each wall slot shows a wall exactly when the maze has one."""
    maze = _maze(6, 5)
    lines = _plain(render(maze))
    last_x, last_y = maze.width - 1, maze.height - 1
    for y in range(maze.height):
        for x in range(maze.width):
            north = lines[2 * y][4 * x + 1:4 * x + 4]
            west = lines[2 * y + 1][4 * x]
            assert (north == "---") == maze.has_wall(x, y, Direction.NORTH)
            assert (west == "|") == maze.has_wall(x, y, Direction.WEST)
        east = lines[2 * y + 1][4 * maze.width]
        assert (east == "|") == maze.has_wall(last_x, y, Direction.EAST)
    for x in range(maze.width):
        south = lines[-1][4 * x + 1:4 * x + 4]
        assert (south == "---") == maze.has_wall(x, last_y, Direction.SOUTH)


def test_path_is_shown_only_on_demand() -> None:
    """The path marks appear with show_path, one per inner path cell."""
    maze = _maze()
    hidden = "\n".join(_plain(render(maze)))
    shown = "\n".join(_plain(render(maze, show_path=True)))
    assert "●" not in hidden
    assert shown.count("●") == len(maze.solution) - 2


def test_pattern_is_drawn() -> None:
    """Every blocked cell is filled."""
    maze = _maze()
    text = "\n".join(_plain(render(maze)))
    assert text.count("███") == len(maze.blocked)


@pytest.mark.parametrize("palette", PALETTES)
def test_palettes_only_change_colours(palette: Palette) -> None:
    """Switching palette never changes the drawing itself."""
    maze = _maze()
    assert _plain(render(maze, True, PALETTES[0])) == _plain(
        render(maze, True, palette)
    )


def test_palettes_have_different_wall_colours() -> None:
    """The menu entry "change wall colours" must change something."""
    assert len({palette.walls for palette in PALETTES}) == len(PALETTES)
