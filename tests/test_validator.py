"""Tests for the common checks of the validator (A5a).

Every check is shown failing on a maze built by hand to break exactly
one invariant, then passing on generated perfect mazes.
"""
from __future__ import annotations

import pytest

from mazegen.errors import GenerationError
from mazegen.generator import MazeGenerator
from mazegen.maze import Direction, Maze
from mazegen.validator import (
    borders_closed,
    is_connected,
    open_areas_3x3,
    validate,
)


def open_all(maze: Maze) -> Maze:
    """Open every inner wall that does not touch a blocked cell."""
    blocked = maze.blocked
    for x, y in maze.cells():
        for direction in (Direction.EAST, Direction.SOUTH):
            target = maze.neighbour(x, y, direction)
            if (target is not None and (x, y) not in blocked
                    and target not in blocked):
                maze.open_wall(x, y, direction)
    return maze


def snake(width: int, height: int) -> Maze:
    """Return a boustrophedon corridor: connected, no loop, no 3x3."""
    maze = Maze(width, height)
    for y in range(height):
        for x in range(width - 1):
            maze.open_wall(x, y, Direction.EAST)
        if y < height - 1:
            x = width - 1 if y % 2 == 0 else 0
            maze.open_wall(x, y, Direction.SOUTH)
    return maze


# ----------------------------------------------------------------------
# borders_closed
# ----------------------------------------------------------------------

def test_new_maze_has_closed_borders() -> None:
    assert borders_closed(Maze(5, 4))


@pytest.mark.parametrize("side", ["north", "south", "west", "east"])
def test_open_border_is_detected(side: str) -> None:
    # open_wall refuses the border, so the only way to break it is to
    # write the storage directly.  That is the point of the check.
    maze = Maze(5, 4)
    if side == "north":
        maze._h_walls[0][2] = False
    elif side == "south":
        maze._h_walls[4][2] = False
    elif side == "west":
        maze._v_walls[1][0] = False
    else:
        maze._v_walls[1][5] = False
    assert not borders_closed(maze)


# ----------------------------------------------------------------------
# is_connected
# ----------------------------------------------------------------------

def test_closed_maze_is_not_connected() -> None:
    assert not is_connected(Maze(3, 3))


def test_corridor_is_connected() -> None:
    assert is_connected(snake(6, 5))


def test_one_cut_disconnects() -> None:
    maze = snake(6, 5)
    maze.close_wall(5, 0, Direction.SOUTH)
    assert not is_connected(maze)


def test_blocked_cells_are_not_required() -> None:
    maze = Maze(3, 3)
    maze.block(1, 1)
    for x, y, direction in [
        (0, 0, Direction.EAST), (1, 0, Direction.EAST),
        (2, 0, Direction.SOUTH), (2, 1, Direction.SOUTH),
        (2, 2, Direction.WEST), (1, 2, Direction.WEST),
        (0, 2, Direction.NORTH),
    ]:
        maze.open_wall(x, y, direction)
    assert is_connected(maze)


# ----------------------------------------------------------------------
# open_areas_3x3
# ----------------------------------------------------------------------

def test_open_3x3_is_detected() -> None:
    assert open_areas_3x3(open_all(Maze(3, 3))) == [(0, 0)]


def test_every_open_3x3_is_listed() -> None:
    assert open_areas_3x3(open_all(Maze(4, 4))) == [
        (0, 0), (1, 0), (0, 1), (1, 1),
    ]


@pytest.mark.parametrize("width,height", [(3, 2), (2, 3), (5, 2), (2, 5)])
def test_two_wide_areas_are_allowed(width: int, height: int) -> None:
    # The subject allows 2x3 and 3x2 open areas.
    assert open_areas_3x3(open_all(Maze(width, height))) == []


INNER_WALLS: list[tuple[int, int, Direction]] = [
    (x, y, Direction.EAST) for y in range(3) for x in range(2)
] + [
    (x, y, Direction.SOUTH) for y in range(2) for x in range(3)
]


@pytest.mark.parametrize("x,y,direction", INNER_WALLS)
def test_each_inner_wall_counts(x: int, y: int, direction: Direction) -> None:
    # Closing any one of the 12 inner walls is enough to break the area.
    maze = open_all(Maze(3, 3))
    maze.close_wall(x, y, direction)
    assert open_areas_3x3(maze) == []


def test_outer_walls_do_not_matter() -> None:
    maze = open_all(Maze(5, 5))
    for y in range(5):
        maze.close_wall(0, y, Direction.EAST)
        maze.close_wall(3, y, Direction.EAST)
    assert open_areas_3x3(maze) == [(1, 0), (1, 1), (1, 2)]


def test_blocked_cell_breaks_the_area() -> None:
    maze = Maze(3, 3)
    maze.block(1, 1)
    open_all(maze)
    assert open_areas_3x3(maze) == []


# ----------------------------------------------------------------------
# validate
# ----------------------------------------------------------------------

def test_validate_reports_the_border() -> None:
    maze = snake(4, 4)
    maze._v_walls[0][0] = False
    with pytest.raises(GenerationError, match="border"):
        validate(maze, perfect=True)


def test_validate_reports_unreachable_cells() -> None:
    with pytest.raises(GenerationError, match="cannot be reached"):
        validate(Maze(3, 3), perfect=True)


def test_validate_reports_open_areas() -> None:
    with pytest.raises(GenerationError, match="3x3"):
        validate(open_all(Maze(4, 4)), perfect=False)


@pytest.mark.parametrize("width,height", [
    (3, 3), (8, 6), (9, 7), (10, 8), (20, 15), (41, 25),
])
def test_generated_perfect_mazes_pass(width: int, height: int) -> None:
    for seed in range(5):
        # generate() calls validate() itself: not raising is the test.
        MazeGenerator(width, height, perfect=True, seed=seed).generate()
