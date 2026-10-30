"""Randomised Kruskal, the bonus algorithm."""
from __future__ import annotations

import random
from typing import ClassVar

from mazegen.algorithms.base import Algorithm
from mazegen.maze import Maze


class Kruskal(Algorithm):
    """Shuffle every inner wall and open the ones joining two trees.

    A union-find structure tells whether the two cells around a wall
    already belong to the same component.  The mazes it produces feel
    less winding than the backtracker ones: shorter corridors, more
    junctions.
    """

    name: ClassVar[str] = "kruskal"

    def carve(self, maze: Maze, rng: random.Random) -> None:
        """Carve a perfect maze over the free cells of ``maze``."""
        raise NotImplementedError
