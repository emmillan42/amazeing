"""Invariants every generated maze must satisfy.

This is our own version of the ``maze_analyzer.py`` script shipped with
the subject: it costs microseconds and it complains before the peer
evaluator does, so it runs on every generated maze, not only in tests.

The checks never reuse the code they check.  Connectivity is measured
with its own breadth-first search, not with the solver, and the 3x3
rule is tested on the final grid, not with the braiding helper that
tries to avoid it: a shared bug would hide itself.
"""
from __future__ import annotations

from collections import deque

from mazegen.errors import GenerationError
from mazegen.maze import Cell, Direction, Maze

AREA: int = 3
"""Side of the smallest forbidden open area."""


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

def count_dead_ends(maze: Maze) -> tuple[int, int]:
    """Return ``(real, enclosed)`` counts of single-exit cells.

    Same split as the official analyzer: a dead end is *real* when one
    of its closed walls could be opened towards a normal cell, and
    *enclosed*, hence tolerated, when every closed wall faces a cell of
    the "42" pattern or the outer border.  Only the real ones count
    against the mode.
    """
    raise NotImplementedError


def count_loops(maze: Maze) -> int:
    """Return the number of independent loops.

    On the graph of free cells, that is ``E - V + C``: the number of
    open walls, minus the number of free cells, plus the number of
    connected components.  A perfect maze gives 0.
    """
    raise NotImplementedError


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------

def validate(maze: Maze, *, perfect: bool) -> None:
    """Check every invariant and complain loudly on the first failure.

    Checked in both modes: full connectivity of the free cells, closed
    outer border, and no 3x3 open area.  Then, depending on the mode,
    exactly zero loops for a perfect maze, or at least two independent
    routes and few dead ends for a playable board.

    Args:
        maze: The maze to check.
        perfect: The mode that was requested.

    Raises:
        GenerationError: On the first invariant that fails, with a
            message naming it.
    """
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
    # The mode checks, driven by ``perfect``, come with A5b.
