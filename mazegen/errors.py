"""Exception hierarchy of the project.

Every error raised on purpose derives from :class:`MazeError`, so the
entry point can catch a single type, print a readable message on
``stderr`` and exit with code 1 instead of showing a traceback.
"""
from __future__ import annotations


class MazeError(Exception):
    """Base class of every error raised by the project."""


class ConfigError(MazeError):
    """The configuration file is missing, unreadable or invalid."""


class InvalidGeometryError(MazeError):
    """The requested geometry cannot describe a valid maze.

    Raised for sizes that are too small, coordinates outside the grid,
    an entry equal to the exit, or an entry or exit falling on a cell
    reserved by the ``42`` pattern.
    """


class PatternTooLargeError(MazeError):
    """The ``42`` pattern does not fit in the requested grid.

    The subject allows the pattern to be skipped in that case, so
    :class:`~mazegen.generator.MazeGenerator` catches this error and
    only records the fact; the warning message is the caller's job.
    """


class GenerationError(MazeError):
    """The generated maze breaks one of its own invariants.

    Raised by the validator: reaching it means a bug in one of the
    generation steps, never a bad input from the user.
    """
