"""Perfect mazes checked by the official analyzer (S1 checkpoint).

``maze_analyzer.py`` comes from the intra and is listed in
``.gitignore``: the whole module is skipped when no local copy sits at
the root of the repository.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from mazegen.generator import MazeGenerator
from mazegen.maze import Maze

analyzer = pytest.importorskip("maze_analyzer")

SIZES: list[tuple[int, int]] = [
    (3, 3), (8, 6), (9, 7), (10, 8), (15, 11), (20, 15), (30, 20),
    (41, 25),
]


def subject_format(maze: Maze) -> str:
    """Lay ``maze`` out as the output file of the subject.

    Stand-in for ``app.writer.write_maze``: once B5 lands, this test
    must write through the real writer, which is what S1 is about.
    """
    footer = [
        f"{maze.entry[0]},{maze.entry[1]}",
        f"{maze.exit[0]},{maze.exit[1]}",
        maze.solution_string(),
    ]
    return "\n".join(maze.to_hex_lines() + [""] + footer) + "\n"


@pytest.mark.parametrize("width,height", SIZES)
def test_perfect_maze_passes_the_analyzer(
    width: int, height: int, tmp_path: Path
) -> None:
    for seed in range(5):
        maze = MazeGenerator(width, height, perfect=True, seed=seed).generate()
        path = tmp_path / f"maze_{seed}.txt"
        path.write_text(subject_format(maze), encoding="utf-8")
        report = analyzer.analyze(analyzer.Maze.from_file(str(path)))
        assert report.incoherent == ()
        assert report.disconnected_corridors == 0
        assert report.loops == 0
        assert analyzer.verdict(report, 2, 2).startswith("PERFECT")
