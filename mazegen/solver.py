"""Shortest path between two cells of a :class:`~mazegen.maze.Maze`.

The maze is seen as an unweighted graph: every cell is a vertex and
every open wall is an edge of length one.  Breadth-first search visits
the cells in order of distance from the start, so the first time it
reaches a cell it has already found a shortest way to it.  The whole
module rests on that single property.
"""
from __future__ import annotations

from collections import deque

from mazegen.errors import MazeError
from mazegen.maze import Cell, Maze


def shortest_path(maze: Maze, start: Cell, goal: Cell) -> list[Cell]:
    """Return a shortest path from ``start`` to ``goal``.

    Neighbours are explored in :class:`~mazegen.maze.Direction` order
    (N, E, S, W).  When several shortest paths exist, the same one is
    therefore always returned: the result depends on the maze only,
    never on chance.

    Args:
        maze: The maze to search.
        start: First cell of the path.
        goal: Last cell of the path.

    Returns:
        The cells of the path, ``start`` and ``goal`` included.  When
        both are the same cell the path is ``[start]``: zero moves.

    Raises:
        MazeError: If ``start`` or ``goal`` is outside the maze or is
            a blocked cell, or if ``goal`` cannot be reached.
    """
    for name, (x, y) in (("start", start), ("goal", goal)):
        if not maze.in_bounds(x, y):
            raise MazeError(f"{name} ({x}, {y}) is outside the maze")
        if maze.is_blocked(x, y):
            raise MazeError(f"{name} ({x}, {y}) is a blocked cell")

    # parent[cell] is the cell from which ``cell`` was first reached.
    # It is also the visited set: a cell is visited iff it is a key.
    parent: dict[Cell, Cell | None] = {start: None}
    queue: deque[Cell] = deque([start])
    while queue and goal not in parent:
        x, y = queue.popleft()
        for nxt in maze.open_neighbours(x, y):
            if nxt not in parent:
                parent[nxt] = (x, y)
                queue.append(nxt)

    if goal not in parent:
        raise MazeError(f"no path from {start} to {goal}")
    return _rebuild(parent, goal)


def _rebuild(parent: dict[Cell, Cell | None], goal: Cell) -> list[Cell]:
    """Follow the parent links back from ``goal`` and reverse them.

    Args:
        parent: Map built by the search, ``None`` marking the start.
        goal: Cell where the walk begins.

    Returns:
        The path in forward order, from the start to ``goal``.
    """
    path: list[Cell] = []
    cell: Cell | None = goal
    while cell is not None:
        path.append(cell)
        cell = parent[cell]
    path.reverse()
    return path
