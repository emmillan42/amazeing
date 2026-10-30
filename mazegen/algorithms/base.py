"""Contract shared by every carving algorithm."""
from __future__ import annotations

import random
from abc import ABC, abstractmethod
from typing import ClassVar

from mazegen.maze import Maze


class Algorithm(ABC):
    """Carve a spanning tree over the free cells of a maze.

    A spanning tree reaches every free cell exactly once, so the result
    is fully connected, has no isolated cell besides the pattern, and
    holds no open area at all.  Whatever the subclass does, it must
    leave the blocked cells untouched.
    """

    name: ClassVar[str] = ""

    @abstractmethod
    def carve(self, maze: Maze, rng: random.Random) -> None:
        """Open the walls of ``maze`` until it is a perfect maze.

        Args:
            maze: An untouched maze, pattern already stamped.
            rng: The seeded random generator, for reproducibility.
        """
