"""mazegen: a reusable maze generator.

Basic use::

    from mazegen import MazeGenerator

    generator = MazeGenerator(20, 15, seed=42, perfect=True)
    maze = generator.generate()

    print(maze.cell_code(0, 0))       # walls of the entry cell
    print(maze.to_hex_lines())        # the grid, one hex row per line
    print(maze.solution)              # [(0, 0), (1, 0), ...]
    print(maze.solution_string())     # "ESEEN..."
"""
from mazegen.errors import (
    ConfigError,
    GenerationError,
    InvalidGeometryError,
    MazeError,
    PatternTooLargeError,
)
from mazegen.generator import MazeGenerator
from mazegen.maze import Cell, Direction, Maze
from mazegen.pattern import fits, minimum_grid

__version__ = "1.0.0"

__all__ = [
    "Cell",
    "ConfigError",
    "Direction",
    "GenerationError",
    "InvalidGeometryError",
    "Maze",
    "MazeError",
    "MazeGenerator",
    "PatternTooLargeError",
    "__version__",
    "fits",
    "minimum_grid",
]
