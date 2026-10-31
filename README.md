*This project has been created as part of the 42 curriculum by emmmilla, lugarcia.*

# A-Maze-ing

A maze generator written in Python: it reads a configuration file,
generates a maze, writes it to a file in hexadecimal, draws it in the
terminal, and lets you play with it from a small menu.  The generation
logic lives in `mazegen`, a package you can install with `pip` and
reuse in another project.

## Description

The program builds two kinds of mazes on a rectangular grid:

- with `PERFECT=True`, a **perfect maze**: exactly one path between any
  two cells, so a single route from the entry to the exit;
- with `PERFECT=False`, the default, a **playable board** for a
  Pac-Man-like game: every corridor reachable, the four corners and the
  centre open, several independent routes, and no real dead end at all.

Both carry a "42" drawn with fully closed cells, both are solved (the
shortest path from the entry to the exit is computed with a
breadth-first search), and both are checked by a validator on every
generation, not only in the tests: borders closed, every free cell
reachable, no open 3x3 area, and the rules of the mode.

The same seed always gives the same maze.  The output passes the
`maze_analyzer.py` script provided with the subject, in both modes, and
the playable boards reach its bonus grade (`--max-dead-ends 0`).

## Instructions

Requirements: Python 3.10 or later.  The program itself uses the
standard library only, so it runs on a fresh clone with nothing to
install:

```sh
python3 a_maze_ing.py config.txt
```

The `Makefile` wraps the common tasks.  The development tools live in a
virtual environment, `.venv`, created by `make install` (on Debian or
Ubuntu, `python3 -m venv` needs the `python3-venv` package).

| Command | What it does |
|---|---|
| `make install` | Create `.venv` and install the pinned tools of `requirements-dev.txt` |
| `make run` | Run the program on `config.txt`; `make run CONFIG=other.txt` for another file |
| `make debug` | The same under `pdb` |
| `make lint` | `flake8` and `mypy` with the flags of the subject |
| `make lint-strict` | `flake8` and `mypy --strict` |
| `make test` | The test suite, with `pytest` |
| `make package` | Rebuild `mazegen-1.0.0-py3-none-any.whl` at the root |
| `make package-test` | Install that wheel in a new virtualenv outside the repository and run `a_maze_ing.py` with it |
| `make clean` / `make fclean` | Remove caches and build leftovers / and the virtual environment |

**Interactive menu.**  After the first maze is drawn, the program
offers: re-generate a new maze, show or hide the shortest path, change
the wall colours, save the current maze to the output file, and quit.
`Ctrl+C` and `Ctrl+D` quit cleanly.

**Errors.**  A wrong configuration never ends in a traceback: the
program prints `error: ...` with the reason and exits with code 1.  If
the grid is too small for the pattern, it prints a warning, generates
the maze without the pattern, and goes on.

**Output file.**  One hexadecimal digit per cell and one line per row
(bit 0 north, 1 east, 2 south, 3 west; a set bit is a closed wall),
then an empty line, the entry, the exit, and the shortest path as
`N`/`E`/`S`/`W` letters.  It is written once, for the first maze; the
menu can save a later one.

**Rebuilding and testing the package**, as asked during the
evaluation.  In a virtualenv, install the build tool and build from the
sources:

```sh
python3 -m venv /tmp/build-env
/tmp/build-env/bin/pip install build
/tmp/build-env/bin/python -m build --wheel --outdir .
```

Then install it in a *different* virtualenv and run the program with
it.  This has to happen **outside the repository**: inside it, `import
mazegen` finds the local `mazegen/` folder first and never the
installed package.  Copy `a_maze_ing.py`, `app/` (the application
layer, which is not part of the reusable package) and the configuration
file:

```sh
python3 -m venv /tmp/run-env
/tmp/run-env/bin/pip install mazegen-1.0.0-py3-none-any.whl
mkdir /tmp/try && cp -r a_maze_ing.py app config.txt /tmp/try/
cd /tmp/try && /tmp/run-env/bin/python a_maze_ing.py config.txt
```

`make package-test` does those steps and also checks that `mazegen` is
imported from `site-packages`.  `make package` writes a fixed date on
every file of the wheel, so rebuilding unchanged sources gives the very
same bytes: after `make package`, an empty `git status` proves that the
committed wheel matches the committed code.

## Resources

- Python documentation: [`random`](https://docs.python.org/3/library/random.html),
  [`enum`](https://docs.python.org/3/library/enum.html),
  [`abc`](https://docs.python.org/3/library/abc.html),
  [`dataclasses`](https://docs.python.org/3/library/dataclasses.html)
  and [`typing`](https://docs.python.org/3/library/typing.html).
- [PEP 8](https://peps.python.org/pep-0008/) (style),
  [PEP 257](https://peps.python.org/pep-0257/) (docstrings),
  [PEP 484](https://peps.python.org/pep-0484/) (type hints) and
  [PEP 561](https://peps.python.org/pep-0561/) (the `py.typed` marker).
- [Python Packaging User Guide](https://packaging.python.org/) and the
  [setuptools documentation](https://setuptools.pypa.io/) on
  `pyproject.toml`; [`SOURCE_DATE_EPOCH`](https://reproducible-builds.org/docs/source-date-epoch/)
  for a reproducible wheel.
- The documentation of [mypy](https://mypy.readthedocs.io/),
  [flake8](https://flake8.pycqa.org/) and [pytest](https://docs.pytest.org/).
- Jamis Buck, *Mazes for Programmers* (Pragmatic Bookshelf, 2015), and
  his [maze generation articles](https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap)
  on the recursive backtracker and Kruskal.
- Walter D. Pullen, [*Think Labyrinth: Maze Algorithms*](https://www.astrolog.org/labyrnth/algrithm.htm),
  for perfect and braid mazes.
- Wikipedia: [Maze generation algorithm](https://en.wikipedia.org/wiki/Maze_generation_algorithm),
  [Disjoint-set data structure](https://en.wikipedia.org/wiki/Disjoint-set_data_structure)
  and [ANSI escape code](https://en.wikipedia.org/wiki/ANSI_escape_code).
- [choosealicense.com](https://choosealicense.com/licenses/mit/), to
  choose the MIT licence.

### How AI was used

We used **AI** mainly for documentation and tests:

- **Tests and measurements**: writing tests, breaking the code on purpose
  to check that the tests catch it, and measuring the generator
  over thousands of mazes with the analyzer.
- **Documentation**: docstrings, the architecture document, the plan,
  the package documentation and this README.

## Configuration file

One `KEY=VALUE` pair per line.  Lines starting with `#` are comments;
the default file only uses whole-line comments.  Keys are case
insensitive (`width=20` is the same as `WIDTH=20`), and so are boolean
values (`True`, `true`, `TRUE`).

| Key | Mandatory | Format | Default | Meaning |
|---|---|---|---|---|
| `WIDTH` | yes | integer | | Number of columns, at least 3 |
| `HEIGHT` | yes | integer | | Number of rows, at least 3 |
| `ENTRY` | yes | `x,y` | | Entry cell; `x` is the column, `y` the row, `0,0` the north-west corner |
| `EXIT` | yes | `x,y` | | Exit cell, inside the grid and different from the entry |
| `OUTPUT_FILE` | yes | file name | | Where the maze is written, kept as written |
| `PERFECT` | yes | `True` / `False` | | Perfect maze, or playable board |
| `SEED` | no | integer | random | Same seed, same mazes; empty means random |
| `ALGORITHM` | no | `backtracker` / `kruskal` | `backtracker` | Carving algorithm, see below |
| `PATTERN` | no | text | `42` | Characters drawn with closed cells (`4` and `2` have glyphs); empty draws nothing |

The default `config.txt`:

```
# Mandatory keys
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=False

# Optional keys.  Remove the leading '#' to use them.
# SEED=42
# ALGORITHM=backtracker
# PATTERN=42
```

The optional keys are commented out with their default values, so
uncommenting one as is changes nothing; uncommenting `SEED` makes every
run give the same maze.

The parser checks syntax and types; the generator checks what only
makes sense with the whole configuration.  Each of these gives a clear
error with the line number when there is one:

- a missing mandatory key, an unknown key (a typo such as `SEDD=4` is
  not ignored), or a key given twice;
- a line without `=`;
- letters where a number is expected, or a boolean other than
  `True` or `False`;
- coordinates that are not `x,y`, or fall outside the grid, or an entry
  equal to the exit, or an entry or exit sitting on the pattern;
- an unknown algorithm, or a pattern character with no glyph;
- a configuration file that does not exist or cannot be read, and an
  output file that cannot be written.

The pattern needs room: `42` needs at least 9x7.  A text with an odd
number of characters needs `4n + 4` columns and is drawn two columns
east of the centre, so that the centre column stays a corridor (the
player starts there in a Pac-Man game).

## Maze generation algorithm

The default algorithm is the **recursive backtracker**, written as an
iterative depth-first search.  From a random free cell, it opens the
wall towards a random unvisited neighbour and moves there; when every
neighbour has been visited, it steps back along its stack.  The cells
of the pattern are marked as visited from the start, so the algorithm
never touches them.  Every opening reaches a new cell, so the result is
a spanning tree of the free cells: connected, with no loop, which is
exactly a perfect maze.

The playable mode is the same tree followed by **braiding**: each dead
end gets one more wall opened, preferably towards another dead end, so
one wall fixes two.  An opening that would create an open 3x3 area is
avoided; when every side of a dead end would create one, the wall is
opened anyway and one wall of the completed block is closed again,
chosen so that no dead end appears and nothing gets disconnected.
Braiding also guarantees at least two independent loops.

### Why this algorithm

- **Correct by construction.**  Each step adds one cell to the tree,
  so connectivity and the absence of loops do not depend on luck; the
  validator confirms it on every maze anyway.
- **Long, winding corridors**, which make a good perfect maze: in a
  20x15 grid it leaves about 30 dead ends on average, against about 81
  for Kruskal.  Fewer dead ends also means less work for braiding.
- **Linear time and no recursion limit.**  An explicit stack replaces
  recursion: the longest corridor of a 100x100 maze is about 4,000
  cells, far beyond Python's default limit of 1,000 frames.
- **Reproducible**: it only draws from the seeded random generator it
  receives, never from the global one.

### Advanced features

- **Two algorithms** (bonus).  `ALGORITHM=kruskal` uses randomised
  Kruskal: every inner wall is shuffled and opened when it joins two
  different components, tracked with a union-find structure (union by
  size, path halving, an iterative `find`).  It gives short corridors
  and many junctions.  Both algorithms pass the analyzer in both modes.
- **No dead end at all** (bonus) in playable mode: the analyzer reports
  `bonus-grade (perfectly braided)` with `--max-dead-ends 0`.
- **Custom pattern** with the `PATTERN` key.
- **Colours**: several wall palettes switched from the menu, and a
  colour of its own for the "42".
- **Save** the maze currently displayed from the menu.

## Reusable module

Everything under `mazegen/` is reusable: the maze structure, the
pattern, both algorithms, braiding, the validator, the solver and the
`MazeGenerator` class.  It has no dependency outside the standard
library and never prints anything.  The application layer (`app/`:
configuration parser, output writer, terminal renderer and menu) and
`a_maze_ing.py` are not part of it.

The package is the file `mazegen-1.0.0-py3-none-any.whl` at the root
of the repository.  The documentation below ships inside it as
`mazegen/README.md`.

A reusable maze generator. It builds two kinds of mazes on a
rectangular grid:

- **perfect** mazes, with exactly one path between any two cells;
- **playable** boards, with loops, open corners and centre and no real
  dead end, ready to host a Pac-Man-like game.

Both can carry a pattern drawn with fully closed cells (`42` by
default).  Pure standard library, Python 3.10 or later, fully typed
(the package ships a `py.typed` marker, so `mypy --strict` checks your
use of it).

### Install

```sh
pip install mazegen-1.0.0-py3-none-any.whl
```

### Quick start

```python
from mazegen import MazeGenerator

generator = MazeGenerator(20, 15, seed=42, perfect=True)
maze = generator.generate()
print("\n".join(maze.to_hex_lines()))
print(maze.solution_string())
```

### Parameters

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

### The maze structure

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

### The solution

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

### License

MIT, see `LICENSE.md`.

## Team and project management

### Roles

- **emmmilla** (Emmanuel): the engine, `mazegen/` — maze structure,
  pattern, both algorithms, solver, braiding, validator and generator.
- **lugarcia** (Lucas): the application, `app/` and `a_maze_ing.py` —
  configuration parser, output writer, terminal renderer and menu — and
  the licence.
- **Together**: the shared setup (`Makefile`, `.gitignore`,
  `config.txt`), the integration of the two parts, during which
  Emmanuel reviewed and corrected the application files to the agreed
  interface, the packaging and this README.

### Planning and how it evolved

The plan split the work into two parallel tracks, the engine and the
application, joined by three synchronisation points: a first real
output file checked by the analyzer, a complete program in perfect
mode, and the Pac-Man mode.  Before splitting, we wrote the interface
between the two tracks (every function signature both sides depend
on), so that neither had to wait for the other.  The first estimate was
about 48 hours, later corrected to 52 with the bonuses.  Two choices of
order were deliberate: braiding, the hardest part, went near the end,
when a complete program in perfect mode already existed; and the wheel
was planned early, because a missing wheel is a zero.

What changed on the way:

- About 7 hours of the engine were done before the split, so the two
  tracks ended up uneven, and the engine finished first.
- The integration came later than planned.  When the two tracks met,
  several application files did not match the agreed interface yet;
  we fixed them together, keeping their design, instead of replacing
  them.
- Measuring with the analyzer found a problem nobody had planned for:
  with a pattern of one character, its centre fell on a blocked cell.
  It became a task of its own and a new placement rule.
- The second algorithm, planned after the tests, was done earlier,
  while the engine track was free.
- Packaging took more than expected: the documentation has to ship
  inside the package, the installed package has to be tested outside
  the repository, and the wheel had to become reproducible.

### What worked well and what could be improved

Worked well:

- **The interface written first.**  Both tracks could work in parallel,
  and when something did not fit, the question was "who breaks the
  contract", not "whose code is right".
- **Measuring before deciding.**  Each design decision is recorded with
  its alternatives and the numbers behind it, in `docs/DECISIONS.md`.
  The analyzer of the subject served as an independent referee, and
  the test suite (775 tests) checks every rule against code written
  separately from the code it checks.

Could be improved:

- **Synchronising tasks and matching our schedules.**  We worked at
  different times, and the integration happened late; a fixed weekly
  slot to merge and run both tracks together would have caught the
  interface mismatches much earlier.

### Tools

- **Git**, with a working repository on **GitHub**.
- **Python tooling**: `venv`, `flake8`, `mypy`, `pytest`, `build` and
  `setuptools`, with exact versions pinned in `requirements-dev.txt`.
- **make**, for every common task.
- **`maze_analyzer.py`**, the analysis script provided with the
  subject, run by the tests on files written by the real writer.
