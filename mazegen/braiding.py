"""Turning a perfect maze into a playable Pac-Man board.

A spanning tree has no loop at all, so it can never break the corridor
width rule.  Braiding is the opposite move: it opens extra walls to
create loops and to remove dead ends, and every candidate wall has to
be checked against the 3x3 rule before being opened.

Nothing here reuses the validator's code: :func:`would_open_3x3` and
:func:`dead_ends` measure the same things as
:func:`mazegen.validator.open_areas_3x3` and
:func:`mazegen.validator.count_dead_ends`, with their own code, so the
tests can use one as the oracle of the other.  The only thing taken
from the validator is the :data:`~mazegen.validator.MIN_LOOPS`
threshold, so that both sides agree on a single number.
"""
from __future__ import annotations

import random
from collections.abc import Iterator

from mazegen.errors import GenerationError, MazeError
from mazegen.maze import Cell, Direction, Maze
from mazegen.validator import MIN_LOOPS

AREA: int = 3
"""Side of the smallest forbidden open area."""

Wall = tuple[int, int, Direction]
"""A wall written from its west or north cell: ``(x, y, EAST | SOUTH)``."""


# ----------------------------------------------------------------------
# The 3x3 rule
# ----------------------------------------------------------------------

def _canonical(
    maze: Maze, x: int, y: int, direction: Direction
) -> Wall | None:
    """Return the wall seen from its west or north cell.

    ``(1, 0, WEST)`` and ``(0, 0, EAST)`` are the same wall; writing
    both as ``(0, 0, EAST)`` lets two walls be compared with ``==``.

    Returns:
        The canonical wall, or ``None`` for a wall of the outer border,
        which has no cell on its other side.
    """
    target = maze.neighbour(x, y, direction)
    if target is None:
        return None
    if direction in (Direction.EAST, Direction.SOUTH):
        return (x, y, direction)
    return (target[0], target[1], direction.opposite)


def _blocks_around(maze: Maze, wall: Wall) -> list[Cell]:
    """Return the north-west corner of every block holding ``wall``.

    A block holds a wall as an inner wall when it contains both cells
    the wall separates: it must start at or before the smaller
    coordinate and end at or after the larger one.  For an east wall
    that leaves 2 columns and 3 rows of possible corners, 6 blocks at
    most, fewer near the border.
    """
    x, y, direction = wall
    dx, dy = direction.delta
    columns = range(max(0, x + dx - AREA + 1),
                    min(x, maze.width - AREA) + 1)
    rows = range(max(0, y + dy - AREA + 1),
                 min(y, maze.height - AREA) + 1)
    return [(bx, by) for by in rows for bx in columns]


def _inner_walls(bx: int, by: int) -> Iterator[Wall]:
    """Yield the 12 inner walls of the block with corner ``(bx, by)``."""
    for dy in range(AREA):
        for dx in range(AREA - 1):
            yield (bx + dx, by + dy, Direction.EAST)
    for dy in range(AREA - 1):
        for dx in range(AREA):
            yield (bx + dx, by + dy, Direction.SOUTH)


def _open_with(
    maze: Maze, bx: int, by: int, extra: Wall | None = None
) -> bool:
    """Tell whether the block is open, or would be once ``extra`` is."""
    return all(
        wall == extra or not maze.has_wall(*wall)
        for wall in _inner_walls(bx, by)
    )


def would_open_3x3(
    maze: Maze, x: int, y: int, direction: Direction
) -> bool:
    """Tell whether opening that wall would create a 3x3 open area.

    The maze is never modified: the wall is only treated as open while
    the blocks around it are inspected.  A wall of the outer border, or
    of a cell of the pattern, always gives ``False``, without a check
    of its own: no block holds a border wall, and a block holding a
    blocked cell always keeps one of its closed walls inside.

    Args:
        maze: The maze being braided.
        x: Column of the source cell.
        y: Row of the source cell.
        direction: Side of ``(x, y)`` about to be opened.

    Returns:
        ``True`` when at least one 3x3 block of cells would end up
        without a single wall inside it, which the subject forbids.

    Raises:
        MazeError: If ``(x, y)`` is outside the maze.
    """
    if not maze.in_bounds(x, y):
        raise MazeError(f"cell ({x}, {y}) is outside the maze")
    wall = _canonical(maze, x, y, direction)
    if wall is None:
        return False
    return any(
        _open_with(maze, bx, by, wall)
        for bx, by in _blocks_around(maze, wall)
    )


# ----------------------------------------------------------------------
# Dead ends
# ----------------------------------------------------------------------

def _openable(
    maze: Maze, x: int, y: int, blocked: frozenset[Cell]
) -> list[Direction]:
    """Return the closed walls of ``(x, y)`` that face a free cell.

    These are the only walls braiding may ever open.  ``blocked`` is
    passed in because :attr:`Maze.blocked` builds a new set on every
    access.
    """
    result: list[Direction] = []
    for direction in Direction:
        target = maze.neighbour(x, y, direction)
        if (target is not None and target not in blocked
                and maze.has_wall(x, y, direction)):
            result.append(direction)
    return result


def dead_ends(maze: Maze) -> list[Cell]:
    """Return every real dead end, in row-major order.

    A dead end is a cell with a single exit.  It is *real* when one of
    its closed walls faces a free cell, so braiding could open it; the
    pockets of the ``42`` pattern, closed by the pattern and the border
    only, are left out (ADR-011).  Blocked cells have no exit at all,
    so the degree test alone keeps them out.
    """
    blocked = maze.blocked
    return [
        (x, y)
        for x, y in maze.cells()
        if maze.degree(x, y) == 1 and _openable(maze, x, y, blocked)
    ]


# ----------------------------------------------------------------------
# Fixing one dead end
# ----------------------------------------------------------------------

def _degree_across(maze: Maze, x: int, y: int, direction: Direction) -> int:
    """Return the number of exits of the neighbour on that side."""
    dx, dy = direction.delta
    return maze.degree(x + dx, y + dy)


def _choose(
    maze: Maze, x: int, y: int, options: list[Direction],
    rng: random.Random,
) -> Direction:
    """Pick a side, preferring one that faces another dead end.

    Opening a wall between two dead ends removes both with one wall,
    so the board keeps more of its maze look and fewer 3x3 blocks get
    close to complete.
    """
    preferred = [
        direction for direction in options
        if _degree_across(maze, x, y, direction) == 1
    ]
    return rng.choice(preferred or options)


def _break_block(
    maze: Maze, bx: int, by: int, rng: random.Random
) -> None:
    """Close one inner wall of an open 3x3 block, keeping it playable.

    Only a wall whose two cells have at least three exits qualifies:
    both keep at least two, so no dead end appears.  Every inner wall
    of an open block lies on a 2x2 loop, so closing it never cuts the
    maze in two.  One always qualifies: the centre of an open block
    has four exits and each middle cell of its sides at least three,
    so any of the four walls around the centre will do.

    Raises:
        GenerationError: If no wall qualifies, which can only mean the
            block was not open: a bug of the caller.
    """
    walls = [
        (x, y, direction)
        for x, y, direction in _inner_walls(bx, by)
        if maze.degree(x, y) >= 3
        and _degree_across(maze, x, y, direction) >= 3
    ]
    if not walls:
        raise GenerationError(
            f"no wall of the 3x3 block at ({bx}, {by}) can be closed "
            f"safely"
        )
    maze.close_wall(*rng.choice(walls))


def _force_open(
    maze: Maze, x: int, y: int, direction: Direction, rng: random.Random
) -> None:
    """Open a wall of a dead end that completes a 3x3 block, then break it.

    Used when every closed side of a dead end would complete a block.
    Exactly one block can be completed: an open block holds two walls
    of each of its corner cells, and the dead end only has its single
    exit plus the wall being opened, so the block is the one holding
    those two walls.  The loop is there for that one block, not for
    several.
    """
    wall = _canonical(maze, x, y, direction)
    completed = [] if wall is None else [
        (bx, by) for bx, by in _blocks_around(maze, wall)
        if _open_with(maze, bx, by, wall)
    ]
    maze.open_wall(x, y, direction)
    for bx, by in completed:
        _break_block(maze, bx, by, rng)


def _fix_dead_end(
    maze: Maze, x: int, y: int, blocked: frozenset[Cell],
    rng: random.Random,
) -> tuple[int, int]:
    """Give the real dead end ``(x, y)`` a second exit.

    A side that keeps the 3x3 rule is opened when there is one;
    otherwise :func:`_force_open` opens a side anyway and breaks the
    blocks it completed.

    Returns:
        ``(removed, loops)``: how many dead ends disappeared, 1 or 2
        when the neighbour was a dead end too, and how many
        independent loops were added, 1 for a plain opening and 0 for
        a forced one, which also closes a wall.
    """
    openable = _openable(maze, x, y, blocked)
    safe = [
        direction for direction in openable
        if not would_open_3x3(maze, x, y, direction)
    ]
    direction = _choose(maze, x, y, safe or openable, rng)
    removed = 1 + int(_degree_across(maze, x, y, direction) == 1)
    if safe:
        maze.open_wall(x, y, direction)
        return removed, 1
    _force_open(maze, x, y, direction, rng)
    return removed, 0


# ----------------------------------------------------------------------
# Braiding
# ----------------------------------------------------------------------

def _add_loops(
    maze: Maze, missing: int, blocked: frozenset[Cell],
    rng: random.Random,
) -> None:
    """Open ``missing`` random walls that keep the 3x3 rule.

    The maze is connected, so each opening joins two cells that were
    already linked and adds exactly one independent loop.  If no wall
    is left, the function gives up and the validator will name the
    problem.
    """
    for _ in range(missing):
        walls = [
            (x, y, direction)
            for x, y in maze.cells()
            for direction in _openable(maze, x, y, blocked)
            if direction in (Direction.EAST, Direction.SOUTH)
            and not would_open_3x3(maze, x, y, direction)
        ]
        if not walls:
            return
        maze.open_wall(*rng.choice(walls))


def braid(
    maze: Maze, rng: random.Random, max_dead_ends: int = 0
) -> int:
    """Open extra walls until few enough dead ends are left.

    Each real dead end is opened towards a random free neighbour that
    does not break the 3x3 rule, preferably another dead end.  When
    every side would complete a 3x3 block, the wall is opened anyway
    and, in each block it completed, one inner wall whose two cells
    keep at least two exits is closed: connectivity holds, no new dead
    end appears and the loop count does not change.

    The dead ends are listed once.  Opening a wall only adds exits, and
    a forced opening only closes walls between cells with three exits
    or more, so no new dead end ever appears: the list can only shrink,
    and the count of what is left is kept by arithmetic, not by
    scanning the grid again.

    The maze also leaves with at least
    :data:`mazegen.validator.MIN_LOOPS` independent loops.  Starting
    from a spanning tree, each plain opening adds exactly one loop, so
    if too few were made, random walls that keep the 3x3 rule are
    opened until the count is reached.  On a maze that already had
    loops the count is a lower bound, which only means a wall more.

    Args:
        maze: The maze to braid, already carved.
        rng: The seeded random generator, for reproducibility.
        max_dead_ends: How many real dead ends are acceptable.

    Returns:
        The number of real dead ends still present.

    Raises:
        GenerationError: If a completed 3x3 block cannot be broken,
            which the proof in :func:`_break_block` rules out.
    """
    blocked = maze.blocked
    pending = dead_ends(maze)
    remaining = len(pending)
    rng.shuffle(pending)
    loops = 0
    for x, y in pending:
        if remaining <= max_dead_ends:
            break
        if maze.degree(x, y) != 1:
            continue
        removed, added = _fix_dead_end(maze, x, y, blocked, rng)
        remaining -= removed
        loops += added
    _add_loops(maze, MIN_LOOPS - loops, blocked, rng)
    return remaining


def ensure_open(maze: Maze, rng: random.Random) -> None:
    """Make sure the corners and the centre are not real dead ends.

    The ghosts and the super pac-gums sit in the corners and the player
    starts in the centre, the one returned by :meth:`Maze.centre`, so
    none of them may be a trap.  After ``braid(maze, rng, 0)`` this
    does nothing; it matters when :func:`braid` was allowed to leave
    dead ends.  A key cell closed in by the pattern and the border has
    nothing to open and is left as it is.

    Each key cell is fixed exactly as :func:`braid` fixes a dead end,
    so the 3x3 rule holds and the loop count never goes down.
    """
    blocked = maze.blocked
    for x, y in maze.corners() + [maze.centre()]:
        if maze.degree(x, y) == 1 and _openable(maze, x, y, blocked):
            _fix_dead_end(maze, x, y, blocked, rng)
