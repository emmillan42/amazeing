"""Randomised Kruskal, the bonus algorithm."""
from __future__ import annotations

import random
from typing import ClassVar

from mazegen.algorithms.base import Algorithm
from mazegen.maze import Cell, Direction, Maze

InnerWall = tuple[Cell, Direction, Cell]
"""A wall between two free cells: ``(cell, direction, neighbour)``."""


class _DisjointSets:
    """Union-find over cells, with union by size and path halving.

    Each set is a tree of cells stored as parent links; the root names
    the set.  Union by size hangs the smaller tree under the larger, so
    no tree is deeper than ``log2`` of its size.  Path halving makes
    every visited cell skip one level on the way up, so later lookups
    get shorter.  Both are performance only: without them the result
    would be the same, but the trees could grow hundreds of levels deep.

    :meth:`find` is a loop on purpose: a recursive version would hit
    the recursion limit on a deep tree, the same risk ADR-016 avoids
    in the backtracker.
    """

    def __init__(self, cells: list[Cell]) -> None:
        """Start with every cell alone in its own set.

        Args:
            cells: The cells to track; any other cell is unknown.
        """
        self._parent: dict[Cell, Cell] = {cell: cell for cell in cells}
        self._size: dict[Cell, int] = {cell: 1 for cell in cells}

    def find(self, cell: Cell) -> Cell:
        """Return the root of the set holding ``cell``.

        Raises:
            KeyError: If ``cell`` was not given to the constructor.
        """
        parent = self._parent
        while parent[cell] != cell:
            parent[cell] = parent[parent[cell]]
            cell = parent[cell]
        return cell

    def union(self, first: Cell, second: Cell) -> bool:
        """Merge the sets of two cells.

        Returns:
            ``True`` if they were in different sets and are now one,
            ``False`` if they already shared a set and nothing changed.
        """
        root_a, root_b = self.find(first), self.find(second)
        if root_a == root_b:
            return False
        if self._size[root_a] < self._size[root_b]:
            root_a, root_b = root_b, root_a
        self._parent[root_b] = root_a
        self._size[root_a] += self._size[root_b]
        return True


class Kruskal(Algorithm):
    """Shuffle every inner wall and open the ones joining two trees.

    A union-find structure tells whether the two cells around a wall
    already belong to the same component.  The mazes it produces feel
    less winding than the backtracker ones: shorter corridors, more
    junctions.
    """

    name: ClassVar[str] = "kruskal"

    def carve(self, maze: Maze, rng: random.Random) -> None:
        """Carve a perfect maze over the free cells of ``maze``.

        Every wall between two free cells is visited once, in an order
        set by ``rng``.  A wall is opened only when its two cells are
        in different components, so no opening can close a loop.  Once
        every wall has been seen, two components left apart would have
        no wall between them, which cannot happen on the free cells:
        the result is a spanning tree.

        Args:
            maze: An untouched maze, pattern already stamped.
            rng: The seeded random generator, for reproducibility.
        """
        walls = self._inner_walls(maze)
        rng.shuffle(walls)
        blocked = maze.blocked
        sets = _DisjointSets(
            [cell for cell in maze.cells() if cell not in blocked]
        )
        for (x, y), direction, target in walls:
            if sets.union((x, y), target):
                maze.open_wall(x, y, direction)

    @staticmethod
    def _inner_walls(maze: Maze) -> list[InnerWall]:
        """Return every wall between two free cells, each one once.

        Each wall is taken from its west or north cell, looking east
        and south only.  The list follows the row-major order of
        :meth:`Maze.cells`, so after the shuffle the order depends on
        the seed only.  Walls of the border and of the pattern never
        get in: the first have no neighbour, the second have a blocked
        one.

        Args:
            maze: The maze being carved.

        Returns:
            ``(cell, direction, neighbour)`` triples, possibly empty.
        """
        blocked = maze.blocked
        walls: list[InnerWall] = []
        for x, y in maze.cells():
            if (x, y) in blocked:
                continue
            for direction in (Direction.EAST, Direction.SOUTH):
                target = maze.neighbour(x, y, direction)
                if target is not None and target not in blocked:
                    walls.append(((x, y), direction, target))
        return walls
