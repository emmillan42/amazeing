"""Public API of the package: the :class:`MazeGenerator` class."""
from __future__ import annotations

import random

from mazegen.algorithms import get_algorithm
from mazegen.braiding import braid, ensure_open
from mazegen.errors import (
    GenerationError,
    InvalidGeometryError,
    PatternTooLargeError,
)
from mazegen.maze import Cell, Maze, validate_geometry
from mazegen.pattern import PATTERN, stamp
from mazegen.solver import shortest_path
from mazegen.validator import validate

MIN_SIDE: int = 3
"""Smallest maze side accepted, whatever the mode."""


class MazeGenerator:
    """Generate a maze, solve it, and keep both.

    The generator never prints anything: when the grid is too small for
    the ``42`` pattern it simply skips it and reports the fact through
    :attr:`pattern_skipped`, leaving the warning to the caller.

    Example:
        >>> from mazegen import MazeGenerator
        >>> generator = MazeGenerator(20, 15, seed=42, perfect=True)
        >>> maze = generator.generate()
        >>> len(maze.to_hex_lines())
        15
        >>> set(maze.solution_string()) <= set("NESW")
        True

    Attributes:
        entry: Entry cell.
        exit: Exit cell.
    """

    def __init__(
        self,
        width: int,
        height: int,
        *,
        entry: Cell = (0, 0),
        exit: Cell | None = None,
        perfect: bool = False,
        seed: int | None = None,
        algorithm: str = "backtracker",
        pattern: str | None = PATTERN,
    ) -> None:
        """Validate the parameters of a future maze.

        Args:
            width: Number of columns.
            height: Number of rows.
            entry: Entry cell, north-west corner by default.
            exit: Exit cell, south-east corner by default.
            perfect: ``True`` for a perfect maze with a single path,
                ``False`` for a playable braided board.
            seed: Seed of the random generator, for reproducibility.
            algorithm: Name of the carving algorithm to use.
            pattern: Text to draw with blocked cells, ``None`` to
                draw nothing.

        Raises:
            InvalidGeometryError: If the maze is smaller than
                :data:`MIN_SIDE` on one side, or if entry or exit is
                outside the grid or equal to the other.
            ConfigError: If ``algorithm`` is unknown.
        """
        if width < MIN_SIDE or height < MIN_SIDE:
            raise InvalidGeometryError(
                f"maze too small: {width}x{height}, minimum is "
                f"{MIN_SIDE}x{MIN_SIDE}"
            )
        exit = validate_geometry(width, height, entry, exit)
        get_algorithm(algorithm)
        self._width: int = width
        self._height: int = height
        self._entry: Cell = entry
        self._exit: Cell = exit
        self._perfect: bool = perfect
        self._seed: int | None = seed
        self._algorithm: str = algorithm
        self._pattern: str | None = pattern
        self._rng: random.Random = random.Random(seed)
        self._maze: Maze | None = None
        self._pattern_cells: set[Cell] = set()
        self._pattern_skipped: bool = False

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @property
    def maze(self) -> Maze:
        """The generated maze.

        Raises:
            GenerationError: If :meth:`generate` has not been called.
        """
        if self._maze is None:
            raise GenerationError("call generate() first")
        return self._maze

    @property
    def seed(self) -> int | None:
        """Seed used by the random generator, ``None`` if unset."""
        return self._seed

    @property
    def algorithm(self) -> str:
        """Name of the carving algorithm in use."""
        return self._algorithm

    @property
    def pattern_cells(self) -> frozenset[Cell]:
        """Cells blocked to draw the pattern, empty if it was skipped."""
        return frozenset(self._pattern_cells)

    @property
    def pattern_skipped(self) -> bool:
        """``True`` when the maze was too small for the pattern."""
        return self._pattern_skipped

    def generate(self) -> Maze:
        """Generate a new maze and solve it.

        The order of the steps is not negotiable: the pattern is
        stamped before carving, so the algorithm only ever sees the
        free cells, and the validator runs on every maze, not only in
        the tests.

        Returns:
            The freshly generated maze, with its solution stored.

        Raises:
            InvalidGeometryError: If entry or exit falls on the
                pattern.
            GenerationError: If the result breaks an invariant or if no
                path links entry and exit.
        """
        maze = Maze(self._width, self._height, self._entry, self._exit)
        self._stamp_pattern(maze)
        self._check_reserved_cells(maze)
        get_algorithm(self._algorithm).carve(maze, self._rng)
        if not self._perfect:
            braid(maze, self._rng)
            ensure_open(maze, self._rng)
        validate(maze, perfect=self._perfect)
        maze.set_solution(shortest_path(maze, maze.entry, maze.exit))
        self._maze = maze
        return maze

    # ------------------------------------------------------------------
    # Pipeline steps
    # ------------------------------------------------------------------

    def _stamp_pattern(self, maze: Maze) -> None:
        """Stamp the pattern, or record that it did not fit."""
        self._pattern_cells = set()
        self._pattern_skipped = False
        if self._pattern is None:
            return
        try:
            self._pattern_cells = stamp(maze, self._pattern)
        except PatternTooLargeError:
            self._pattern_skipped = True

    def _check_reserved_cells(self, maze: Maze) -> None:
        """Refuse an entry or an exit sitting on the pattern.

        The corners and the centre of a playable board are checked too,
        but they can never be blocked: the pattern is centred with a
        margin, and the centre is defined as the nearest free cell.

        Raises:
            InvalidGeometryError: If a reserved cell is blocked.
        """
        reserved = [("ENTRY", maze.entry), ("EXIT", maze.exit)]
        if not self._perfect:
            reserved += [
                ("CORNER", corner) for corner in maze.corners()
            ]
        for name, (x, y) in reserved:
            if maze.is_blocked(x, y):
                raise InvalidGeometryError(
                    f"{name} ({x}, {y}) falls on the "
                    f"{self._pattern!r} pattern"
                )
