"""Recursive backtracker, written as an iterative depth-first search."""
from __future__ import annotations

import random
from typing import ClassVar

from mazegen.algorithms.base import Algorithm
from mazegen.maze import Cell, Direction, Maze


class Backtracker(Algorithm):
    """Depth-first carving with an explicit stack.

    Starting from a free cell, the walker opens a wall towards a random
    unvisited neighbour and moves there; when it is stuck it pops the
    stack and tries again.  The explicit stack replaces recursion and
    removes any risk of hitting the recursion limit on a large grid.
    """

    name: ClassVar[str] = "backtracker"

    def carve(self, maze: Maze, rng: random.Random) -> None:
        """Carve a perfect maze over the free cells of ``maze``.

        Every wall is opened towards a cell that was never visited, so
        each opening adds one new cell to the tree and no opening can
        close a loop.  The blocked cells are marked as visited from the
        start: the walker never even considers them, and
        :meth:`Maze.open_wall` would refuse them anyway.

        Args:
            maze: An untouched maze, pattern already stamped.
            rng: The seeded random generator, for reproducibility.
        """
        blocked = maze.blocked
        free: list[Cell] = [
            cell for cell in maze.cells() if cell not in blocked
        ]
        if not free:
            return
        start: Cell = rng.choice(free)
        visited: set[Cell] = set(blocked)
        visited.add(start)
        stack: list[Cell] = [start]
        while stack:
            x, y = stack[-1]
            options = self._unvisited_neighbours(maze, x, y, visited)
            if not options:
                stack.pop()
                continue
            direction, target = rng.choice(options)
            maze.open_wall(x, y, direction)
            visited.add(target)
            stack.append(target)

    @staticmethod
    def _unvisited_neighbours(
        maze: Maze, x: int, y: int, visited: set[Cell]
    ) -> list[tuple[Direction, Cell]]:
        """Return the in-bounds unvisited neighbours of ``(x, y)``.

        Each one comes with the direction leading to it.  The list
        follows the order of :class:`Direction`, so the choice made by
        ``rng`` depends on the seed only.

        Args:
            maze: The maze being carved.
            x: Column of the current cell.
            y: Row of the current cell.
            visited: Cells already in the tree, plus the blocked ones.

        Returns:
            ``(direction, cell)`` pairs, possibly empty.
        """
        result: list[tuple[Direction, Cell]] = []
        for direction in Direction:
            target = maze.neighbour(x, y, direction)
            if target is not None and target not in visited:
                result.append((direction, target))
        return result
