"""Tests for the validator: common checks (A5a) and mode checks (A5b).

Every check is shown failing on a maze built by hand to break exactly
one invariant, then passing on generated perfect mazes.  The measures
themselves are compared with the official analyzer in
``test_analyzer.py``.
"""
from __future__ import annotations

import pytest

from mazegen.errors import GenerationError
from mazegen.generator import MazeGenerator
from mazegen.maze import Direction, Maze
from mazegen.validator import (
    MAX_REAL_DEAD_ENDS,
    MIN_LOOPS,
    borders_closed,
    count_dead_ends,
    count_loops,
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
# count_loops
# ----------------------------------------------------------------------

def test_closed_maze_has_no_loop() -> None:
    # 9 isolated cells: E = 0, V = 9, C = 9.
    assert count_loops(Maze(3, 3)) == 0


def test_corridor_has_no_loop() -> None:
    assert count_loops(snake(6, 5)) == 0


@pytest.mark.parametrize("extra", [1, 2, 3])
def test_each_rung_adds_one_loop(extra: int) -> None:
    # Every extra wall opened between two rows of the snake closes one
    # more cycle, and never a 3x3 area: one wall per row gap at most.
    maze = snake(6, 5)
    for y in range(extra):
        maze.open_wall(2, y, Direction.SOUTH)
    assert count_loops(maze) == extra


@pytest.mark.parametrize("width,height", [(2, 2), (3, 2), (4, 4), (7, 5)])
def test_open_grid_has_one_loop_per_face(width: int, height: int) -> None:
    # Independent oracle: a fully open grid has one cycle per inner
    # face, that is (width - 1) * (height - 1).
    maze = open_all(Maze(width, height))
    assert count_loops(maze) == (width - 1) * (height - 1)


def test_components_are_counted() -> None:
    # Two open 2x2 squares split by a closed column: 2 loops.  Without
    # the C term, E - V + 1 would give 8 - 10 + 1 = -1.
    maze = Maze(5, 2)
    for x in (0, 3):
        maze.open_wall(x, 0, Direction.EAST)
        maze.open_wall(x, 1, Direction.EAST)
        maze.open_wall(x, 0, Direction.SOUTH)
        maze.open_wall(x + 1, 0, Direction.SOUTH)
    assert count_loops(maze) == 2


def test_blocked_cells_do_not_count() -> None:
    # A ring around a blocked centre: 8 cells, 8 edges, 1 loop.
    maze = Maze(3, 3)
    maze.block(1, 1)
    open_all(maze)
    assert count_loops(maze) == 1


def test_edge_into_the_pattern_is_not_an_edge() -> None:
    # open_wall refuses it, so only a direct write to the storage can
    # open a wall of a blocked cell.  The graph of free cells must not
    # see that edge: it would have one vertex outside the graph.
    maze = Maze(3, 1)
    maze.block(2, 0)
    maze.open_wall(0, 0, Direction.EAST)
    maze._v_walls[0][2] = False
    assert count_loops(maze) == 0


# ----------------------------------------------------------------------
# count_dead_ends
# ----------------------------------------------------------------------

def test_corridor_ends_are_real_dead_ends() -> None:
    # Both ends of the snake could still be opened towards a free cell.
    assert count_dead_ends(snake(4, 4)) == (2, 0)


def test_loop_without_dead_end() -> None:
    assert count_dead_ends(open_all(Maze(2, 2))) == (0, 0)


def test_pockets_against_the_pattern_are_enclosed() -> None:
    # A T over three blocked cells: its three tips are dead ends whose
    # closed walls all face the border or the pattern, so no braiding
    # could ever open them.  The two free cells left in the bottom
    # corners are isolated, not dead ends: they have no exit at all.
    maze = Maze(3, 3)
    for x, y in [(0, 1), (2, 1), (1, 2)]:
        maze.block(x, y)
    open_all(maze)
    assert count_dead_ends(maze) == (0, 3)


def test_corner_against_the_border_is_real() -> None:
    # The border alone does not make a dead end enclosed: (0, 0) still
    # has a closed wall towards a free cell.
    maze = Maze(2, 2)
    for x, y, direction in [
        (0, 0, Direction.EAST), (1, 0, Direction.SOUTH),
        (1, 1, Direction.WEST),
    ]:
        maze.open_wall(x, y, direction)
    assert count_dead_ends(maze) == (2, 0)


def test_cells_with_two_exits_are_not_dead_ends() -> None:
    real, enclosed = count_dead_ends(open_all(Maze(4, 3)))
    assert real == enclosed == 0


def test_generated_maze_has_the_pattern_pockets() -> None:
    # ADR-007: the 3x5 glyphs leave exactly 3 enclosed dead ends.
    maze = MazeGenerator(20, 15, perfect=True, seed=42).generate()
    assert count_dead_ends(maze)[1] == 3


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


def test_perfect_mode_rejects_a_loop() -> None:
    maze = snake(6, 5)
    maze.open_wall(2, 0, Direction.SOUTH)
    with pytest.raises(GenerationError, match="1 independent loop"):
        validate(maze, perfect=True)


def test_perfect_mode_accepts_a_tree() -> None:
    validate(snake(6, 5), perfect=True)


def braided_snake(rungs: int) -> Maze:
    """Return a 6x5 snake with ``rungs`` extra walls between rows."""
    maze = snake(6, 5)
    for y in range(rungs):
        maze.open_wall(2, y, Direction.SOUTH)
    return maze


def test_playable_mode_needs_loops() -> None:
    with pytest.raises(GenerationError, match="at least"):
        validate(braided_snake(MIN_LOOPS - 1), perfect=False)


def test_playable_mode_accepts_enough_loops() -> None:
    # The snake keeps its 2 real dead ends: exactly the tolerance.
    assert count_dead_ends(braided_snake(MIN_LOOPS))[0] == 2
    validate(braided_snake(MIN_LOOPS), perfect=False)


def test_playable_mode_rejects_too_many_dead_ends() -> None:
    # Cut the far end of the snake off its row and hang it from the
    # row below: one more real dead end, connectivity kept.
    maze = braided_snake(4)
    maze.close_wall(4, 4, Direction.EAST)
    maze.open_wall(5, 3, Direction.SOUTH)
    real, _ = count_dead_ends(maze)
    assert real == MAX_REAL_DEAD_ENDS + 1
    with pytest.raises(GenerationError, match="dead end"):
        validate(maze, perfect=False)


def test_perfect_maze_is_not_playable() -> None:
    maze = MazeGenerator(20, 15, perfect=True, seed=0).generate()
    with pytest.raises(GenerationError, match="0 independent loop"):
        validate(maze, perfect=False)


def test_common_checks_come_first() -> None:
    # A closed maze has no loop either, but the connectivity message
    # must win: loops mean nothing on a disconnected graph.
    with pytest.raises(GenerationError, match="cannot be reached"):
        validate(Maze(3, 3), perfect=False)


@pytest.mark.parametrize("width,height", [
    (3, 3), (8, 6), (9, 7), (10, 8), (20, 15), (41, 25),
])
def test_generated_perfect_mazes_pass(width: int, height: int) -> None:
    for seed in range(5):
        # generate() calls validate() itself: not raising is the test.
        MazeGenerator(width, height, perfect=True, seed=seed).generate()
