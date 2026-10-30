"""Entry point of the project.

Usage::

    python3 a_maze_ing.py config.txt
"""
from __future__ import annotations

import sys

from app.config_parser import Config, parse_config
from app.menu import Menu
from app.writer import write_maze
from mazegen.errors import MazeError
from mazegen.generator import MazeGenerator
from mazegen.pattern import minimum_grid

USAGE: str = "usage: python3 a_maze_ing.py config.txt"


def build_generator(config: Config) -> MazeGenerator:
    """Create the generator described by ``config``."""
    return MazeGenerator(
        config.width,
        config.height,
        entry=config.entry,
        exit=config.exit,
        perfect=config.perfect,
        seed=config.seed,
        algorithm=config.algorithm,
        pattern=config.pattern,
    )


def warn_if_pattern_skipped(
    generator: MazeGenerator, config: Config
) -> None:
    """Warn on the console when the maze was too small for the pattern.

    The text comes from the configuration, not from the default: with
    ``PATTERN=4`` the warning must talk about "4" and its own minimum.
    """
    if not generator.pattern_skipped or config.pattern is None:
        return
    min_width, min_height = minimum_grid(config.pattern)
    print(
        f"warning: maze too small for the {config.pattern!r} pattern, "
        f"it needs at least {min_width}x{min_height}",
        file=sys.stderr,
    )


def main(argv: list[str]) -> int:
    """Run the program.

    Args:
        argv: The command line, ``sys.argv`` style.

    Returns:
        ``0`` on success, ``1`` when an error was reported to the user.
    """
    if len(argv) != 2:
        print(USAGE, file=sys.stderr)
        return 1
    try:
        config = parse_config(argv[1])
        generator = build_generator(config)
        maze = generator.generate()
        warn_if_pattern_skipped(generator, config)
        write_maze(config.output_file, maze)
        Menu(generator, config).run()
    except MazeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
