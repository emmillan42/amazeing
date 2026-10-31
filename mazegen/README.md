# mazegen

A reusable maze generator. It builds two kinds of mazes on a
rectangular grid:

- **perfect** mazes, with exactly one path between any two cells;
- **playable** boards, with loops, open corners and centre and no real
  dead end, ready to host a Pac-Man-like game.

Both can carry a pattern drawn with fully closed cells (`42` by
default).  Pure standard library, Python 3.10 or later, fully typed
(the package ships a `py.typed` marker, so `mypy --strict` checks your
use of it).

## Install

```sh
pip install mazegen-1.0.0-py3-none-any.whl
```

## Quick start

```python
from mazegen import MazeGenerator

generator = MazeGenerator(20, 15, seed=42, perfect=True)
maze = generator.generate()
print("\n".join(maze.to_hex_lines()))
print(maze.solution_string())
```

## Parameters

Every parameter but the size is a keyword argument.

| Parameter | Default | Meaning |
|---|---|---|
| `width`, `height` | required | Size of the grid, at least 3 on each side |
| `entry` | `(0, 0)` | Entry cell, as `(x, y)` |
| `exit` | `None` | Exit cell; `None` means the south-east corner |
| `perfect` | `False` | `True` for a perfect maze, `False` for a playable board |
| `seed` | `None` | Seed of the random generator: same seed, same mazes |
| `algorithm` | `"backtracker"` | `"backtracker"` (long winding corridors) or `"kruskal"` (short corridors, many junctions) |
| `pattern` | `"42"` | Text drawn with closed cells, `None` for no drawing |

A wrong parameter fails in the constructor, never later.  Every error
the package raises is a `MazeError`:

```python
from mazegen import MazeError, MazeGenerator

try:
    MazeGenerator(20, 15, entry=(6, 5))
except MazeError as error:
    print(error)  # the entry falls on the "42"
```

When the grid is too small for the pattern, the maze is generated
without it and `generator.pattern_skipped` is `True`: the package never
prints anything, warning the user is up to you.

## The maze structure

`generate()` returns a `Maze`.  Coordinates are `(x, y)` pairs: `x` is
the column, `y` the row, and `y` grows southwards, so `(0, 0)` is the
north-west corner.

```python
from mazegen import MazeGenerator
from mazegen.maze import Direction

maze = MazeGenerator(9, 7, seed=1).generate()
x, y = maze.entry
assert maze.has_wall(x, y, Direction.NORTH)  # the border is closed
print(maze.open_neighbours(x, y))  # cells reachable in one step
print(sorted(maze.blocked))        # cells drawing the pattern
print(maze.cell_code(x, y))        # 4 bits, N=1 E=2 S=4 W=8, 1 = wall
```

`maze.to_hex_lines()` gives the whole grid as one hexadecimal digit per
cell, row by row.  Each wall is stored once and shared by its two
cells, so the grid is always coherent.

## The solution

Every generated maze is solved: `maze.solution` is the shortest path
from the entry to the exit, both included, and
`maze.solution_string()` the same path as `N`/`E`/`S`/`W` moves.

```python
from mazegen import MazeGenerator

first = MazeGenerator(20, 15, seed=7).generate()
again = MazeGenerator(20, 15, seed=7).generate()
assert first.to_hex_lines() == again.to_hex_lines()
assert first.solution[0] == first.entry
assert first.solution[-1] == first.exit
assert len(first.solution_string()) == len(first.solution) - 1
```

Calling `generate()` again on the same generator gives a new maze; the
last one stays available as `generator.maze`.

## License

MIT, see `LICENSE.md`.
