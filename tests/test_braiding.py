"""Tests of the braiding helpers (A6).

The validator is the oracle: it measures 3x3 areas and dead ends with
its own code (ADR-017), so agreeing with it on many random states is a
real check, not a tautology.
"""
from __future__ import annotations

import random
from itertools import combinations

import pytest

from mazegen import braiding
from mazegen.braiding import braid, dead_ends, ensure_open, would_open_3x3
from mazegen.errors import GenerationError, MazeError
from mazegen.generator import MazeGenerator
from mazegen.maze import Cell, Direction, Maze
from mazegen.validator import (
    MIN_LOOPS,
    count_dead_ends,
    count_loops,
    is_connected,
    open_areas_3x3,
    validate,
)

Wall = tuple[int, int, Direction]

INNER_WALLS: list[Wall] = [
    (x, y, Direction.EAST) for y in range(3) for x in range(2)
] + [
    (x, y, Direction.SOUTH) for y in range(2) for x in range(3)
]
"""The 12 inner walls of a 3x3 maze, written from their west or north."""

SIZES: list[tuple[int, int]] = [(3, 3), (3, 7), (5, 4), (6, 6), (9, 7),
                                (12, 10)]


def _open_all_but(maze: Maze, *closed: Wall) -> None:
    """Open every inner wall of a 3x3 maze except ``closed``."""
    for wall in INNER_WALLS:
        if wall not in closed:
            maze.open_wall(*wall)


def _closed_free_walls(maze: Maze) -> list[Wall]:
    """Return the closed inner walls between two free cells."""
    blocked = maze.blocked
    return [
        (x, y, direction)
        for x, y in maze.cells()
        for direction in (Direction.EAST, Direction.SOUTH)
        if (x, y) not in blocked
        and maze.neighbour(x, y, direction) not in (None, *blocked)
        and maze.has_wall(x, y, direction)
    ]


def _random_walk(
    maze: Maze, rng: random.Random
) -> list[tuple[Wall, bool, bool]]:
    """Try every closed wall once, keeping the maze free of 3x3 areas.

    Each wall is asked to :func:`would_open_3x3`, then opened, and the
    validator says whether a 3x3 area appeared; when it did, the wall
    is closed again.  The maze stays legal and grows dense, and the
    states close to a forbidden area are the interesting ones.

    Returns:
        One ``(wall, predicted, actual)`` triple per wall tried.
    """
    results: list[tuple[Wall, bool, bool]] = []
    walls = _closed_free_walls(maze)
    rng.shuffle(walls)
    for wall in walls:
        predicted = would_open_3x3(maze, *wall)
        maze.open_wall(*wall)
        actual = bool(open_areas_3x3(maze))
        if actual:
            maze.close_wall(*wall)
        results.append((wall, predicted, actual))
    return results


# ----------------------------------------------------------------------
# would_open_3x3
# ----------------------------------------------------------------------

@pytest.mark.parametrize("wall", INNER_WALLS)
def test_last_wall_completes_the_block(wall: Wall) -> None:
    """Each of the 12 inner walls counts, wherever it sits."""
    maze = Maze(3, 3)
    _open_all_but(maze, wall)
    assert would_open_3x3(maze, *wall)


@pytest.mark.parametrize("wall", INNER_WALLS)
def test_same_answer_from_both_sides(wall: Wall) -> None:
    """A wall is the same seen from either of its two cells."""
    maze = Maze(3, 3)
    _open_all_but(maze, wall)
    x, y, direction = wall
    target = maze.neighbour(x, y, direction)
    assert target is not None
    assert would_open_3x3(maze, target[0], target[1], direction.opposite)


@pytest.mark.parametrize("pair", list(combinations(INNER_WALLS, 2)))
def test_two_missing_walls_are_safe(pair: tuple[Wall, Wall]) -> None:
    """With two walls closed, opening either one is still legal."""
    maze = Maze(3, 3)
    _open_all_but(maze, *pair)
    assert not any(would_open_3x3(maze, *wall) for wall in pair)


def test_border_walls_never_complete_a_block() -> None:
    """No block holds a wall of the outer border."""
    maze = Maze(3, 3)
    _open_all_but(maze, INNER_WALLS[0])
    for x, y in maze.cells():
        for direction in Direction:
            if maze.neighbour(x, y, direction) is None:
                assert not would_open_3x3(maze, x, y, direction)


def test_blocked_cell_keeps_its_blocks_closed() -> None:
    """A wall of a pattern cell never completes a block."""
    maze = Maze(3, 3)
    maze.block(1, 1)
    for wall in INNER_WALLS:
        x, y, direction = wall
        if (1, 1) not in ((x, y), maze.neighbour(x, y, direction)):
            maze.open_wall(*wall)
    for direction in Direction:
        assert not would_open_3x3(maze, 1, 1, direction)


def test_cell_outside_the_grid_is_refused() -> None:
    """A cell outside is an error, not a question about its neighbour."""
    maze = Maze(3, 3)
    with pytest.raises(MazeError):
        would_open_3x3(maze, -1, 0, Direction.EAST)


def test_already_open_wall_is_answered_too() -> None:
    """Asking about an open wall describes the current state."""
    maze = Maze(3, 3)
    _open_all_but(maze)
    assert would_open_3x3(maze, 0, 0, Direction.EAST)


def test_the_maze_is_never_modified() -> None:
    """The check is a pure query, open or closed wall alike."""
    maze = Maze(4, 4)
    _open_all_but(maze, INNER_WALLS[3])
    before = maze.to_hex_lines()
    for x, y in maze.cells():
        for direction in Direction:
            would_open_3x3(maze, x, y, direction)
    assert maze.to_hex_lines() == before


@pytest.mark.parametrize("size", SIZES)
def test_agrees_with_the_validator(size: tuple[int, int]) -> None:
    """On dense random states, the prediction matches the validator."""
    width, height = size
    positives = 0
    for seed in range(15):
        maze = MazeGenerator(width, height, seed=seed,
                             perfect=True).generate()
        for wall, predicted, actual in _random_walk(
            maze, random.Random(seed)
        ):
            assert predicted == actual, f"{size} seed {seed} wall {wall}"
            positives += predicted
    assert positives > 0


# ----------------------------------------------------------------------
# dead_ends
# ----------------------------------------------------------------------

def test_hand_made_dead_ends() -> None:
    """A three-cell corridor has its two ends as dead ends."""
    maze = Maze(3, 3)
    maze.open_wall(0, 0, Direction.EAST)
    maze.open_wall(1, 0, Direction.EAST)
    assert dead_ends(maze) == [(0, 0), (2, 0)]


def test_pocket_of_the_pattern_is_not_real() -> None:
    """A dead end closed only by the pattern and the border is left out."""
    maze = Maze(3, 3)
    maze.block(1, 0)
    maze.open_wall(0, 0, Direction.SOUTH)
    assert maze.degree(0, 0) == 1
    assert dead_ends(maze) == [(0, 1)]


def test_blocked_cells_are_never_listed() -> None:
    """Pattern cells have no exit, so they are not dead ends."""
    maze = MazeGenerator(20, 15, seed=42, perfect=True).generate()
    assert not set(dead_ends(maze)) & maze.blocked


def test_row_major_order() -> None:
    """The list is deterministic: row by row, then column by column."""
    maze = MazeGenerator(20, 15, seed=7, perfect=True).generate()
    found = dead_ends(maze)
    assert found == sorted(found, key=lambda cell: (cell[1], cell[0]))


@pytest.mark.parametrize("size", SIZES + [(20, 15)])
def test_count_matches_the_validator(size: tuple[int, int]) -> None:
    """Same number of real dead ends as the validator, before and after."""
    width, height = size
    for seed in range(15):
        maze = MazeGenerator(width, height, seed=seed,
                             perfect=True).generate()
        assert len(dead_ends(maze)) == count_dead_ends(maze)[0]
        _random_walk(maze, random.Random(seed))
        assert len(dead_ends(maze)) == count_dead_ends(maze)[0]


# ----------------------------------------------------------------------
# braid
# ----------------------------------------------------------------------

def _random_tree(maze: Maze, rng: random.Random) -> None:
    """Carve a random spanning tree with union-find over shuffled walls.

    The backtracker never leaves a dead end stuck behind a 3x3 block
    (0 out of 11,530 measured mazes): its long corridors have few dead
    ends.  These bushier trees do it in about 1 small grid out of 9,
    which is what reaches the forced opening.  Test helper only, not
    the A8 algorithm.
    """
    blocked = maze.blocked
    parent: dict[Cell, Cell] = {
        cell: cell for cell in maze.cells() if cell not in blocked
    }

    def find(cell: Cell) -> Cell:
        while parent[cell] != cell:
            cell = parent[cell]
        return cell

    walls = _closed_free_walls(maze)
    rng.shuffle(walls)
    for x, y, direction in walls:
        target = maze.neighbour(x, y, direction)
        assert target is not None
        a, b = find((x, y)), find(target)
        if a != b:
            parent[a] = b
            maze.open_wall(x, y, direction)


def _is_playable(maze: Maze) -> bool:
    """Tell whether the maze passes every check of the playable mode."""
    try:
        validate(maze, perfect=False)
    except GenerationError:
        return False
    return True


def test_stuck_corner_is_forced_open() -> None:
    """A dead end with every side completing a 3x3 still gets fixed.

    Every inner wall is open but the east one of the corner, whose
    only other side is the border: opening it completes the block.
    """
    maze = Maze(3, 3)
    _open_all_but(maze, (0, 0, Direction.EAST))
    assert dead_ends(maze) == [(0, 0)]
    assert would_open_3x3(maze, 0, 0, Direction.EAST)
    assert braid(maze, random.Random(0)) == 0
    assert not dead_ends(maze)
    assert not open_areas_3x3(maze)
    assert is_connected(maze)
    assert count_loops(maze) == 3, "one wall opened, one closed"


def test_forced_opening_on_random_trees(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Bushy trees reach the forced opening, and still end playable."""
    forced: list[Cell] = []
    original = braiding._force_open

    def spy(maze: Maze, x: int, y: int, direction: Direction,
            rng: random.Random) -> None:
        forced.append((x, y))
        original(maze, x, y, direction, rng)

    monkeypatch.setattr(braiding, "_force_open", spy)
    for size in [(3, 3), (3, 5), (4, 4), (9, 7)]:
        for seed in range(60):
            maze = Maze(*size)
            _random_tree(maze, random.Random(seed))
            assert braid(maze, random.Random(seed)) == 0
            assert _is_playable(maze), f"{size} seed {seed}"
    assert forced, "the sweep never reached the forced opening"


def test_fix_reports_the_loops_it_really_adds() -> None:
    """Each fix adds the loops it claims, measured by the validator.

    A plain opening adds one loop, a forced one adds none: the loop
    guarantee of :func:`braid` relies on that bookkeeping.
    """
    forced = Maze(3, 3)
    _open_all_but(forced, (0, 0, Direction.EAST))
    cases = [forced]
    for seed in range(30):
        tree = Maze(3, 3)
        _random_tree(tree, random.Random(seed))
        cases.append(tree)
    seen: set[int] = set()
    for maze in cases:
        rng = random.Random(0)
        for x, y in dead_ends(maze):
            if maze.degree(x, y) != 1:
                continue
            before = count_loops(maze)
            _, added = braiding._fix_dead_end(maze, x, y, maze.blocked, rng)
            assert count_loops(maze) - before == added
            seen.add(added)
    assert seen == {0, 1}


@pytest.mark.parametrize("size", [(3, 3), (3, 4), (4, 3), (4, 4), (6, 3),
                                  (9, 7), (20, 15)])
def test_pipeline_gives_bonus_grade_boards(size: tuple[int, int]) -> None:
    """No real dead end, and enough loops even on serpent-like trees.

    3x4 and 4x3 are the sizes where a backtracker corridor joined at
    both ends left a single loop before the loop guarantee.
    """
    for seed in range(40):
        maze = MazeGenerator(*size, seed=seed).generate()
        assert not dead_ends(maze)
        assert count_loops(maze) >= MIN_LOOPS


@pytest.mark.parametrize("limit", [0, 1, 3, 10])
def test_returned_count_is_exact(limit: int) -> None:
    """The arithmetic count agrees with a fresh scan of the grid."""
    for seed in range(20):
        maze = MazeGenerator(20, 15, seed=seed, perfect=True).generate()
        left = braid(maze, random.Random(seed), max_dead_ends=limit)
        assert left == len(dead_ends(maze))
        assert left <= limit


def test_loops_are_added_when_no_dead_end_is_fixed() -> None:
    """A tolerance large enough to fix nothing still gives the loops."""
    maze = MazeGenerator(20, 15, seed=3, perfect=True).generate()
    before = len(dead_ends(maze))
    assert braid(maze, random.Random(3), max_dead_ends=10**6) == before
    assert count_loops(maze) == MIN_LOOPS
    assert not open_areas_3x3(maze)


def test_pattern_pockets_are_left_alone() -> None:
    """The three pockets of the 42 survive as tolerated dead ends."""
    maze = MazeGenerator(20, 15, seed=42).generate()
    assert count_dead_ends(maze) == (0, 3)
    for x, y in [(7, 6), (11, 6), (11, 8)]:
        assert maze.degree(x, y) == 1


def test_same_seed_same_board() -> None:
    """Braiding draws only from the given generator."""
    boards = [
        MazeGenerator(15, 11, seed=5).generate().to_hex_lines()
        for _ in range(2)
    ]
    assert boards[0] == boards[1]


def test_break_block_refuses_a_closed_block() -> None:
    """The guard behind the proof: no qualifying wall is an error."""
    with pytest.raises(GenerationError):
        braiding._break_block(Maze(3, 3), 0, 0, random.Random(0))


# ----------------------------------------------------------------------
# ensure_open
# ----------------------------------------------------------------------

def _key_cells(maze: Maze) -> list[Cell]:
    """Return the four corners and the centre."""
    return maze.corners() + [maze.centre()]


def test_ensure_open_does_nothing_after_a_full_braid() -> None:
    """With zero dead ends left, no key cell can be a trap."""
    for seed in range(20):
        maze = MazeGenerator(15, 11, seed=seed, perfect=True).generate()
        rng = random.Random(seed)
        braid(maze, rng)
        before = maze.to_hex_lines()
        ensure_open(maze, rng)
        assert maze.to_hex_lines() == before


def test_ensure_open_fixes_the_key_cells() -> None:
    """On a perfect maze, corners often are dead ends: not afterwards."""
    fixed = 0
    for seed in range(20):
        maze = MazeGenerator(20, 15, seed=seed, perfect=True).generate()
        trapped = set(_key_cells(maze)) & set(dead_ends(maze))
        ensure_open(maze, random.Random(seed))
        assert not set(_key_cells(maze)) & set(dead_ends(maze))
        assert not open_areas_3x3(maze)
        assert is_connected(maze)
        fixed += len(trapped)
    assert fixed > 0


def test_ensure_open_leaves_an_enclosed_key_cell() -> None:
    """A corner closed in by the pattern has nothing to open."""
    maze = Maze(3, 3)
    maze.block(1, 0)
    maze.open_wall(0, 0, Direction.SOUTH)
    ensure_open(maze, random.Random(0))
    assert maze.degree(0, 0) == 1
