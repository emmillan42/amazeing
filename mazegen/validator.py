"""Invariants every generated maze must satisfy.

This is our own version of the ``maze_analyzer.py`` script shipped with
the subject: it costs a few milliseconds and it complains before the
peer evaluator does, so it runs on every generated maze, not only in
tests.

The checks never reuse the code they check.  Connectivity is measured
with its own breadth-first search, not with the solver, and the 3x3
rule is tested on the final grid, not with the braiding helper that
tries to avoid it: a shared bug would hide itself.

The playable thresholds are the defaults of the official analyzer.
They are the floor the subject asks for, not the target: the braiding
aims for zero real dead ends, the validator only refuses a board that
the analyzer itself would reject.
"""
from __future__ import annotations

from collections import deque

from mazegen.errors import GenerationError
from mazegen.maze import Cell, Direction, Maze

AREA: int = 3
"""Side of the smallest forbidden open area."""

MIN_LOOPS: int = 2
"""Independent loops a playable board needs (analyzer ``--min-loops``)."""

MAX_REAL_DEAD_ENDS: int = 2
"""Real dead ends a playable board tolerates (``--max-dead-ends``)."""


# ----------------------------------------------------------------------
# Common checks (A5a)
# ----------------------------------------------------------------------

def _reachable(maze: Maze, start: Cell) -> set[Cell]:
    """Return every cell reachable from ``start`` through open walls."""
    seen: set[Cell] = {start}
    queue: deque[Cell] = deque([start])
    while queue:
        x, y = queue.popleft()
        for target in maze.open_neighbours(x, y):
            if target not in seen:
                seen.add(target)
                queue.append(target)
    return seen


def _unreachable(maze: Maze) -> list[Cell]:
    """Return the free cells that cannot be reached from the entry."""
    reached = _reachable(maze, maze.entry)
    blocked = maze.blocked
    return [
        cell
        for cell in maze.cells()
        if cell not in blocked and cell not in reached
    ]


def is_connected(maze: Maze) -> bool:
    """Tell whether every free cell is reachable from the entry."""
    return not _unreachable(maze)


def borders_closed(maze: Maze) -> bool:
    """Tell whether the outer border is fully closed."""
    last_x, last_y = maze.width - 1, maze.height - 1
    horizontal = all(
        maze.has_wall(x, 0, Direction.NORTH)
        and maze.has_wall(x, last_y, Direction.SOUTH)
        for x in range(maze.width)
    )
    vertical = all(
        maze.has_wall(0, y, Direction.WEST)
        and maze.has_wall(last_x, y, Direction.EAST)
        for y in range(maze.height)
    )
    return horizontal and vertical


def _area_is_open(maze: Maze, x: int, y: int) -> bool:
    """Tell whether the 3x3 block with north-west corner ``(x, y)`` is open.

    A block is open when its 12 inner walls are all open: 6 vertical
    ones, between its columns, and 6 horizontal ones, between its rows.
    Its outer walls do not matter.
    """
    inner_east = all(
        not maze.has_wall(x + dx, y + dy, Direction.EAST)
        for dy in range(AREA)
        for dx in range(AREA - 1)
    )
    inner_south = all(
        not maze.has_wall(x + dx, y + dy, Direction.SOUTH)
        for dy in range(AREA - 1)
        for dx in range(AREA)
    )
    return inner_east and inner_south


def open_areas_3x3(maze: Maze) -> list[Cell]:
    """Return the north-west corner of every 3x3 open area."""
    return [
        (x, y)
        for y in range(maze.height - AREA + 1)
        for x in range(maze.width - AREA + 1)
        if _area_is_open(maze, x, y)
    ]


# ----------------------------------------------------------------------
# Mode checks (A5b)
# ----------------------------------------------------------------------

def _free_cells(maze: Maze) -> list[Cell]:
    """Return the cells that do not belong to the pattern."""
    blocked = maze.blocked
    return [cell for cell in maze.cells() if cell not in blocked]


def _open_edges(maze: Maze, free: set[Cell]) -> int:
    """Count the open walls between two free cells, each one once.

    Looking only east and south visits every inner wall exactly once.
    The outer border is skipped by the ``neighbour`` test, and an edge
    touching a blocked cell is skipped too: it would be an edge of the
    graph without its two vertices.
    """
    return sum(
        1
        for x, y in free
        for direction in (Direction.EAST, Direction.SOUTH)
        if not maze.has_wall(x, y, direction)
        and maze.neighbour(x, y, direction) in free
    )


def _components(maze: Maze, free: set[Cell]) -> int:
    """Count the connected components of the free cells."""
    seen: set[Cell] = set()
    count = 0
    for cell in free:
        if cell not in seen:
            seen |= _reachable(maze, cell)
            count += 1
    return count


def count_loops(maze: Maze) -> int:
    """Return the number of independent loops.

    On the graph of free cells, that is ``E - V + C``: the number of
    open walls, minus the number of free cells, plus the number of
    connected components.  A perfect maze gives 0.

    The official analyzer computes ``E - V + 1`` on the region of the
    entry only.  Both agree once :func:`is_connected` holds, which is
    why :func:`validate` checks connectivity first; the ``C`` term keeps
    this function right on any maze, connected or not.
    """
    free = set(_free_cells(maze))
    return _open_edges(maze, free) - len(free) + _components(maze, free)


def _is_enclosed(maze: Maze, x: int, y: int) -> bool:
    """Tell whether every closed wall of ``(x, y)`` is a dead wall.

    A closed wall is dead when it faces the outer border or a cell of
    the pattern: no braiding can ever open it.
    """
    blocked = maze.blocked
    for direction in Direction:
        target = maze.neighbour(x, y, direction)
        if (maze.has_wall(x, y, direction) and target is not None
                and target not in blocked):
            return False
    return True


def count_dead_ends(maze: Maze) -> tuple[int, int]:
    """Return ``(real, enclosed)`` counts of single-exit cells.

    Same split as the official analyzer: a dead end is *real* when one
    of its closed walls could be opened towards a normal cell, and
    *enclosed*, hence tolerated, when every closed wall faces a cell of
    the "42" pattern or the outer border.  Only the real ones count
    against the mode.

    The analyzer only reads a file, so it spots the pattern as cells
    with their four walls closed; here the maze knows its blocked
    cells.  Both agree once :func:`is_connected` holds, because then no
    free cell has its four walls closed.
    """
    real = enclosed = 0
    for x, y in _free_cells(maze):
        if maze.degree(x, y) != 1:
            continue
        if _is_enclosed(maze, x, y):
            enclosed += 1
        else:
            real += 1
    return real, enclosed


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------

def _check_common(maze: Maze) -> None:
    """Raise on the first broken invariant shared by both modes."""
    if not borders_closed(maze):
        raise GenerationError("invalid maze: the outer border is open")
    unreachable = _unreachable(maze)
    if unreachable:
        x, y = unreachable[0]
        raise GenerationError(
            f"invalid maze: {len(unreachable)} free cell(s) cannot be "
            f"reached from the entry, the first one is ({x}, {y})"
        )
    areas = open_areas_3x3(maze)
    if areas:
        x, y = areas[0]
        raise GenerationError(
            f"invalid maze: {len(areas)} open 3x3 area(s), the first "
            f"one has its north-west corner at ({x}, {y})"
        )


def _check_perfect(maze: Maze) -> None:
    """Raise unless the maze has no loop at all.

    Connected, which :func:`_check_common` already made sure of, plus
    zero loops is exactly the definition of a spanning tree.
    """
    loops = count_loops(maze)
    if loops:
        raise GenerationError(
            f"invalid perfect maze: {loops} independent loop(s), "
            f"expected none"
        )


def _check_playable(maze: Maze) -> None:
    """Raise unless the maze is a usable Pac-Man board.

    Corners and centre need no check of their own: they are free cells,
    and :func:`_check_common` already proved every free cell reachable.
    """
    loops = count_loops(maze)
    if loops < MIN_LOOPS:
        raise GenerationError(
            f"invalid playable maze: {loops} independent loop(s), "
            f"at least {MIN_LOOPS} are needed"
        )
    real, _ = count_dead_ends(maze)
    if real > MAX_REAL_DEAD_ENDS:
        raise GenerationError(
            f"invalid playable maze: {real} real dead end(s), "
            f"at most {MAX_REAL_DEAD_ENDS} are tolerated"
        )


def validate(maze: Maze, *, perfect: bool) -> None:
    """Check every invariant and complain loudly on the first failure.

    Checked in both modes: closed outer border, full connectivity of
    the free cells, and no 3x3 open area.  Then, depending on the mode,
    exactly zero loops for a perfect maze, or at least
    :data:`MIN_LOOPS` independent routes and at most
    :data:`MAX_REAL_DEAD_ENDS` real dead ends for a playable board.

    The common checks always run first: the loop count and the dead
    end split only match the official analyzer on a connected maze.

    Args:
        maze: The maze to check.
        perfect: The mode that was requested.

    Raises:
        GenerationError: On the first invariant that fails, with a
            message naming it.
    """
    _check_common(maze)
    if perfect:
        _check_perfect(maze)
    else:
        _check_playable(maze)
