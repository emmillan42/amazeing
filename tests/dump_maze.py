"""Write a perfect maze in the output format of the subject.

Throwaway helper for the S1 checkpoint: it lets the engine be checked
with ``maze_analyzer.py`` before the real writer (B5) exists.  It is
not part of the program and is never imported by ``mazegen``.

Usage, from the root of the repository::

    python3 -m tests.dump_maze 20 15 42 > /tmp/maze.txt
    python3 maze_analyzer.py /tmp/maze.txt
"""
from __future__ import annotations

import sys

from mazegen.errors import MazeError
from mazegen.generator import MazeGenerator
from mazegen.maze import Maze


def subject_format(maze: Maze) -> str:
    """Return ``maze`` as the subject lays out the output file.

    One hexadecimal row per line, an empty line, then the entry, the
    exit and the shortest path, each on its own line.
    """
    entry_x, entry_y = maze.entry
    exit_x, exit_y = maze.exit
    lines = maze.to_hex_lines()
    lines += [
        "",
        f"{entry_x},{entry_y}",
        f"{exit_x},{exit_y}",
        maze.solution_string(),
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    """Generate the maze described by ``argv`` and print it.

    Args:
        argv: ``WIDTH HEIGHT [SEED]``, without the program name.

    Returns:
        The exit code: 0 on success, 1 on any error.
    """
    if len(argv) not in (2, 3):
        print("usage: python3 -m tests.dump_maze WIDTH HEIGHT [SEED]",
              file=sys.stderr)
        return 1
    try:
        width, height = int(argv[0]), int(argv[1])
        seed = int(argv[2]) if len(argv) == 3 else None
        generator = MazeGenerator(width, height, perfect=True, seed=seed)
        maze = generator.generate()
    except (ValueError, MazeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    if generator.pattern_skipped:
        print("warning: maze too small for the pattern, skipped",
              file=sys.stderr)
    sys.stdout.write(subject_format(maze))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
