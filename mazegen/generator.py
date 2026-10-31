"""Public API of the package: the :class:`MazeGenerator` class."""
from __future__ import annotations

import random

from mazegen.algorithms import get_algorithm
from mazegen.braiding import braid, ensure_open
from mazegen.errors import (
    GenerationError,
    InvalidGeometryError,
    MazeError,
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

        Every parameter is checked here, the pattern included: the
        ``42`` is always stamped at the same place, so an entry sitting
        on it is known before anything is carved.  A wrong parameter
        never waits for :meth:`generate` to show up.

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
                :data:`MIN_SIDE` on one side, if entry or exit is
                outside the grid or equal to the other, or if one of
                them falls on the pattern.
            ConfigError: If ``algorithm`` is unknown.
        """
        if width < MIN_SIDE or height < MIN_SIDE:
            raise InvalidGeometryError(
                f"invalid maze size {width}x{height}: each side must be "
                f"at least {MIN_SIDE}"
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
        self._generated: int = 0
        self._check_reserved_cells(self._blank_maze())

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
            GenerationError: If carving, braiding or the validator
                fail.  It is always a bug, and the message carries what
                is needed to reproduce it.
        """
        self._generated += 1
        maze = self._blank_maze()
        self._carve(maze)
        if not self._perfect:
            self._braid(maze)
        self._validate(maze)
        maze.set_solution(shortest_path(maze, maze.entry, maze.exit))
        self._maze = maze
        return maze

    # ------------------------------------------------------------------
    # Pipeline steps
    # ------------------------------------------------------------------

    def _blank_maze(self) -> Maze:
        """Return a maze with every wall closed and the pattern stamped."""
        maze = Maze(self._width, self._height, self._entry, self._exit)
        self._stamp_pattern(maze)
        return maze

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

        The corners of a playable board are checked too, but they can
        never be blocked: the pattern always keeps a margin to the
        border.  The centre is not checked: the pattern leaves its
        column free (ADR-025), and it is defined as the nearest free
        cell anyway.

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
                    f"{self._pattern!r} pattern, choose a free cell"
                )

    def _carve(self, maze: Maze) -> None:
        """Run the carving algorithm.

        Every parameter was checked by the constructor, so a failure
        here can only be a bug of the algorithm, typically a wall it
        should not open.  It is reported like a failure of braiding or
        of the validator, with what rebuilds the same maze.

        Raises:
            GenerationError: If the algorithm breaks an invariant of
                :class:`Maze`.
        """
        try:
            get_algorithm(self._algorithm).carve(maze, self._rng)
        except MazeError as error:
            raise self._internal_error(error) from error

    def _braid(self, maze: Maze) -> None:
        """Turn the spanning tree into a playable board.

        Braiding cannot fail on a carved maze: a dead end that can only
        be opened into a 3x3 block gets the block broken instead.  Any
        error here is therefore a bug, reported like a failure of the
        validator.

        The count of dead ends :func:`braid` returns is not checked:
        the validator measures the board with its own code right after,
        and a step does not grade its own work.

        Raises:
            GenerationError: If braiding breaks one of its guarantees.
        """
        try:
            braid(maze, self._rng)
            ensure_open(maze, self._rng)
        except MazeError as error:
            raise self._internal_error(error) from error

    def _validate(self, maze: Maze) -> None:
        """Run the validator and make its failure reproducible.

        Raises:
            GenerationError: If the maze breaks an invariant.
        """
        try:
            validate(maze, perfect=self._perfect)
        except GenerationError as error:
            raise self._internal_error(error) from error

    def _internal_error(self, error: MazeError) -> GenerationError:
        """Wrap a failure that can only be a bug of the generator.

        It is never the user's fault: the parameters were all checked
        by the constructor.  The message says so and lists what rebuilds
        the same maze: the arguments, seed included when there is one,
        and which call to :meth:`generate` it was, since each call
        draws from the same random generator.
        """
        return GenerationError(
            f"internal error, please report it: {error} "
            f"[{self._describe()}]"
        )

    def _describe(self) -> str:
        """Return the arguments of this generator, for bug reports."""
        seed = "unset" if self._seed is None else str(self._seed)
        return (
            f"{self._width}x{self._height}, "
            f"algorithm={self._algorithm}, perfect={self._perfect}, "
            f"pattern={self._pattern!r}, seed={seed}, "
            f"generate() call #{self._generated}"
        )
