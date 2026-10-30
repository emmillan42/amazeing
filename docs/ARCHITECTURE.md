# A-Maze-ing — Arquitectura y contrato

Documento vivo. Se **reescribe entero** cuando algo cambia, y la
versión nueva sustituye a la anterior en los documentos del proyecto.
Describe cómo está montado el proyecto ahora mismo.

El *porqué* de cada decisión no está aquí: está en `DECISIONS.md`, en
formato ADR y en orden cronológico. Aquí solo se cita el número.

Última actualización: 30 oct 2026 · T0.1, T0.2, A4, A3, A5a, A5b y
A7a cerradas · T0.3 pendiente de acordar con Lucas · ADR-013 y ADR-014 propuestas, a
falta de su confirmación. El avance por tareas está en `PLAN.md`.

---

## 1. Estado

| Bloque | Estado |
|---|---|
| `errors.py`, `maze.py`, `pattern.py` | implementados y probados |
| `solver.py` | implementado y probado: 207 tests contra un oráculo de fuerza bruta (A4) |
| `algorithms/backtracker.py` | implementado y probado (A3, ADR-016) |
| `algorithms/__init__.py`, `algorithms/base.py` | registro y clase base, hechos |
| `algorithms/kruskal.py` | firma y docstring, `NotImplementedError` (A8, bonus) |
| `validator.py` | completo: chequeos comunes (A5a, ADR-017) y por modo (A5b, ADR-019) |
| `generator.py` | modo perfecto cerrado y mensajes de error afinados (A7a, ADR-020); el modo jugable espera a A6 |
| `braiding.py` | firmas y docstrings, `NotImplementedError` (A6) |
| `app/*` | firmas y docstrings |
| `a_maze_ing.py` | implementado |
| `tests/fixtures.py` | laberinto 5x5 cableado, usable ya |
| `tests/test_solver.py` | hecho (A4) |
| `tests/test_backtracker.py`, `tests/test_validator.py` | hechos (A3, A5a, A5b) |
| `tests/test_generator.py` | hecho (A7a): cuándo sale cada error y qué dice |
| `tests/test_analyzer.py` | hecho; compara además `count_loops` y `count_dead_ends` con el analizador (A5b); se salta si no hay `maze_analyzer.py` local (ADR-018) |
| `tests/dump_maze.py` | provisional, se retira en S2 (ADR-018) |
| `Makefile`, `.gitignore`, `requirements-dev.txt`, `.flake8`, `mypy.ini` | hechos (T0.1) |
| `config.txt` | hecho (T0.2) |
| `pyproject.toml`, `README.md`, `LICENSE.md` | pendientes (vía B) |

Hasta A4, todo el árbol pasaba `make lint` y `make lint-strict` sin un
solo aviso, con las versiones fijadas en `requirements-dev.txt`. Los
ficheros de A3, A5a, A5b y A7a pasan `flake8`, `mypy` con los flags del
subject y `mypy --strict`, y unos 180 tests, pero verificados sobre una
reconstrucción de `errors.py`, `pattern.py`, `solver.py`,
`algorithms/__init__.py` y `algorithms/base.py`: falta repetirlo en el
repo (§10). La base de `validator.py` sí está comprobada: la parte A5a
del repo coincide carácter a carácter con la que se usó para A5b.

**Primer laberinto real del motor por el analizador oficial.** 20x15,
semilla 42, modo perfecto: coherencia de muros OK, 280 celdas
alcanzables y ninguna aislada, 0 bucles, `28 real + 3 enclosed`, y
veredicto *PERFECT maze*. Los 3 callejones *enclosed* son (7,6), (11,6)
y (11,8), los que predecía ADR-007.

**Modo perfecto cerrado en el motor.** `validate` comprueba ya los dos
modos, y sus medidas coinciden con las del analizador en todos los
laberintos conexos probados (ADR-019). El generador rechaza cualquier
parámetro imposible en el constructor y no deja escapar nada que no
sea `MazeError` (ADR-020).

El programa todavía no completa: el writer (B5) y el renderer (B3) son
stubs, así que `make run` no termina en ningún modo. Para ver un
laberinto real mientras tanto, `python3 -m tests.dump_maze 20 15 42`.
La configuración por defecto lleva `PERFECT=False` (ADR-014): hasta A6
termina con un error claro que pide `perfect=True`, no con un
traceback.

---

## 2. Decisiones

Índice. El detalle está en `DECISIONS.md`.

| ADR | Decisión | Estado |
|---|---|---|
| 001 | Muros como aristas compartidas (`v_walls` / `h_walls`) | Aceptada |
| 002 | El "42" se estampa antes de generar | Aceptada |
| 003 | Los dos modos son el mismo árbol de expansión más braiding | Aceptada |
| 004 | Centro = celda libre más cercana al centro geométrico | Aceptada |
| 005 | Render ASCII con ANSI, no MiniLibX | Aceptada |
| 006 | `random.Random(seed)` como instancia | Aceptada |
| 007 | Glifos 3x5, bloque 7x5, mínimo 9x7 | Aceptada |
| 008 | Paquete en la raíz, no en `src/` | Aceptada |
| 009 | El fichero de salida guarda el primer laberinto | Aceptada |
| 010 | Licencia MIT | Aceptada |
| 011 | Se mantiene la fuente 3x5: el bonus es alcanzable con ella | Aceptada |
| 012 | Clave `PATTERN`, no `DISPLAY` | Aceptada |
| 013 | Herramientas en `.venv` con versiones fijadas; lint configurado en `.flake8` y `mypy.ini` | Propuesta |
| 014 | `config.txt` solo con comentarios de línea completa; opcionales comentadas | Propuesta |
| 015 | `shortest_path` lanza `MazeError` si no hay camino; desempate N, E, S, O | Aceptada |
| 016 | Backtracker como DFS iterativo con pila explícita | Aceptada |
| 017 | El validador no reutiliza lo que valida; 3x3 abierto = 12 muros interiores abiertos | Aceptada |
| 018 | Analizador antes de B5: helpers provisionales en `tests/` | Aceptada |
| 019 | Chequeos por modo: `E − V + C` sobre las libres; umbrales del analizador como suelo | Aceptada |
| 020 | Generador: parámetros en el constructor, stubs como `GenerationError`, fallos internos reproducibles | Aceptada |

---

## 3. Árbol

```
.
├── a_maze_ing.py          entry point: argv, orquestación, errores
├── config.txt             configuración por defecto        [hecho]
├── Makefile               install/run/debug/clean/lint     [hecho]
├── requirements-dev.txt   herramientas de desarrollo       [hecho]
├── .flake8                exclusiones de flake8            [hecho]
├── mypy.ini               exclusiones de mypy              [hecho]
├── .gitignore             re-incluye el wheel de la raíz   [hecho]
├── pyproject.toml         construye mazegen-1.0.0          [pendiente]
├── mazegen-1.0.0-py3-none-any.whl                          [pendiente]
├── README.md  LICENSE.md                                   [pendiente]
│
├── docs/
│   ├── ARCHITECTURE.md    este fichero, se reescribe entero
│   ├── DECISIONS.md       ADRs, solo se añade al final
│   └── PLAN.md            inventario de tareas y cronogramas
│
├── mazegen/               ← REUTILIZABLE, esto es el wheel
│   ├── __init__.py        fachada: MazeGenerator, Maze, errores
│   ├── errors.py          MazeError y subclases
│   ├── maze.py            Maze, Direction, validate_geometry [hecho]
│   ├── pattern.py         glifos, tamaño mínimo, estampado   [hecho]
│   ├── solver.py          BFS → camino más corto             [hecho]
│   ├── braiding.py        bucles, callejones, regla 3x3      [stub]
│   ├── validator.py       invariantes, los dos modos         [hecho]
│   ├── generator.py       MazeGenerator, pipeline            [A7a hecha]
│   └── algorithms/
│       ├── __init__.py    registro y get_algorithm()         [hecho]
│       ├── base.py        Algorithm(ABC)                     [hecho]
│       ├── backtracker.py DFS iterativo                      [hecho]
│       └── kruskal.py     bonus, union-find                  [stub]
│
├── app/                   ← NO reutilizable
│   ├── config_parser.py   KEY=VALUE → Config                 [stub]
│   ├── writer.py          fichero de salida                  [stub]
│   ├── renderer.py        ASCII + ANSI                       [stub]
│   └── menu.py            bucle interactivo                  [stub]
│
└── tests/
    ├── fixtures.py        laberinto 5x5 a mano               [hecho]
    ├── test_solver.py     BFS contra fuerza bruta            [hecho]
    ├── test_backtracker.py árbol de expansión, semilla       [hecho]
    ├── test_validator.py  cada chequeo, roto a propósito     [hecho]
    ├── test_generator.py  errores del pipeline               [hecho]
    ├── test_analyzer.py   veredicto y medidas vs analizador  [hecho]
    └── dump_maze.py       volcado al formato del subject     [provisional]
```

`tests/` no es un paquete y sus módulos no se importan entre sí: con
`mypy .`, importar un módulo de `tests/` desde otro da *Source file
found twice* (ADR-018). Si hacen falta helpers compartidos, van a
`tests/conftest.py`.

`maze_analyzer.py` no está en el árbol: es de la intra y está en el
`.gitignore`. Se puede tener una copia local en la raíz, y pasa el lint
igualmente. Si B9 lo necesita dentro del repo, basta con quitar esa
línea del `.gitignore` (ADR-013).

### 3.1 Targets del Makefile

| Target | Qué hace |
|---|---|
| `install` | Crea `.venv` e instala `requirements-dev.txt`. Solo se rehace si los requisitos cambian (fichero marcador `.venv/.installed`) |
| `run` | `python3 a_maze_ing.py config.txt` con el intérprete del sistema; `CONFIG=` lo sobrescribe |
| `debug` | Lo mismo bajo `python3 -m pdb` |
| `clean` | `__pycache__`, cachés de mypy y pytest, `build/`, `dist/`, `*.egg-info`. Nunca el wheel de la raíz |
| `fclean` | `clean` más el `.venv` |
| `lint` | `flake8 .` y `mypy .` con los flags exactos del subject |
| `lint-strict` | `flake8 .` y `mypy . --strict` |
| `test` | `python -m pytest` (no `pytest`: ver ADR-013) |

El target de empaquetado se añade con B6, cuando exista
`pyproject.toml`.

---

## 4. Contrato

Estas firmas no se tocan sin avisar al otro. Son lo que permite
trabajar en paralelo.

```python
class Direction(Enum):          # valor = (bit, dx, dy)
    NORTH = (1, 0, -1); EAST = (2, 1, 0)
    SOUTH = (4, 0, 1);  WEST = (8, -1, 0)
    bit: int; delta: tuple[int, int]; letter: str; opposite: Direction


def validate_geometry(width, height, entry, exit) -> Cell
    # comprueba tamaño, límites y entry != exit; devuelve el exit
    # resuelto. La usan Maze y MazeGenerator, para que un parámetro
    # inconsistente se rechace en el constructor y no al generar.


class Maze:
    def __init__(self, width: int, height: int,
                 entry: Cell = (0, 0), exit: Cell | None = None) -> None
    width, height, entry, exit, blocked: frozenset[Cell]
    # geometría
    def in_bounds(self, x, y) -> bool
    def cells(self) -> list[Cell]
    def neighbour(self, x, y, d: Direction) -> Cell | None
    def neighbours(self, x, y) -> list[Cell]
    def corners(self) -> list[Cell]
    def centre(self) -> Cell
    def nearest_free(self, x, y) -> Cell
    # muros
    def has_wall(self, x, y, d) -> bool
    def open_wall(self, x, y, d) -> None     # rechaza borde y bloqueada
    def close_wall(self, x, y, d) -> None
    def block(self, x, y) -> None            # celda del patrón
    def is_blocked(self, x, y) -> bool
    # consultas
    def open_directions(self, x, y) -> list[Direction]
    def open_sides(self, x, y) -> list[str]
    def open_neighbours(self, x, y) -> list[Cell]
    def degree(self, x, y) -> int
    # solución y export
    solution: list[Cell]
    def set_solution(self, path: list[Cell]) -> None
    def solution_string(self) -> str         # "ESEEN...", n celdas → n-1 letras
    def cell_code(self, x, y) -> int
    def to_hex_lines(self) -> list[str]


class MazeGenerator:
    def __init__(self, width: int, height: int, *,
                 entry: Cell = (0, 0),
                 exit: Cell | None = None,
                 perfect: bool = False,
                 seed: int | None = None,
                 algorithm: str = "backtracker",
                 pattern: str | None = "42") -> None
        # InvalidGeometryError o ConfigError: todo parámetro imposible,
        # entrada o salida sobre el "42" incluidas, falla aquí.
    def generate(self) -> Maze
        # GenerationError: paso aún sin implementar, o bug (el mensaje
        # lleva los argumentos, la semilla y el número de llamada).
    maze, seed, algorithm, pattern_cells, pattern_skipped
        # pattern_cells y pattern_skipped, válidos desde el constructor


@dataclass(frozen=True)
class Config:
    width: int; height: int
    entry: Cell; exit: Cell
    output_file: str; perfect: bool
    seed: int | None = None
    algorithm: str = "backtracker"
    pattern: str | None = "42"
```

Funciones sueltas:

```python
solver.shortest_path(maze, start, goal) -> list[Cell]
    # start y goal incluidos; [start] si son la misma celda.
    # Desempate determinista en orden N, E, S, O.
    # MazeError si una celda está fuera o bloqueada, o si no hay
    # camino (ADR-015).
braiding.braid(maze, rng, max_dead_ends=0) -> int
braiding.ensure_open(maze, rng) -> None
braiding.would_open_3x3(maze, x, y, d) -> bool
braiding.dead_ends(maze) -> list[Cell]        # solo los reales
validator.validate(maze, *, perfect) -> None
validator.count_loops(maze) -> int                   # E - V + C
validator.count_dead_ends(maze) -> tuple[int, int]   # (real, enclosed)
validator.MIN_LOOPS = 2; validator.MAX_REAL_DEAD_ENDS = 2
pattern.stamp(maze, text="42") -> set[Cell]
pattern.minimum_grid(text="42") -> tuple[int, int]
pattern.fits(width, height, text="42") -> bool
algorithms.get_algorithm(name) -> Algorithm
app.writer.write_maze(path, maze) -> None
app.renderer.render(maze, show_path, palette) -> str
```

`write_maze` recibe solo el laberinto porque el `Maze` ya lleva dentro
la entrada, la salida y la solución. La conversión de celdas a letras
NESW la hace `Maze.solution_string()`, no el solver.

Excepciones, todas bajo `MazeError`: `ConfigError`,
`InvalidGeometryError`, `PatternTooLargeError`, `GenerationError`. Se
capturan en un único `try/except` en `a_maze_ing.py`, que imprime un
mensaje legible en `stderr` y sale con código 1. Nunca un traceback en
pantalla: la hoja de evaluación pone un 0 ante cualquier terminación
inesperada.

---

## 5. Invariantes que garantiza `Maze`

Nada de esto se valida a posteriori: o es estructural, o salta una
excepción en el momento.

1. **Coherencia de muros compartidos**: un solo booleano por arista
   (ADR-001).
2. **Borde exterior cerrado**: `open_wall` lanza `MazeError` si el
   vecino cae fuera. No hay forma de abrir el borde.
3. **El "42" no se puede estropear**: `open_wall` lanza `MazeError` si
   alguna de las dos celdas está bloqueada, venga de donde venga la
   llamada (ADR-002).
4. **Entrada y salida válidas y distintas**: `validate_geometry`, desde
   el constructor.

---

## 6. Pipeline

```
Config validada
  → MazeGenerator(...): tamaño, geometría, algoritmo, y entry/exit/
    esquinas contra un "42" estampado en blanco (ADR-020)
  → generate(): Maze vacío (todos los muros cerrados)
  → estampar "42"      ¿no cabe? → pattern_skipped = True, sigue
  → árbol de expansión sobre las celdas libres
  → si PERFECT=False: braiding (bucles y callejones) + ensure_open
  → validator (siempre, también en producción)
  → solver BFS → maze.set_solution(...)
  → writer (una sola vez, ADR-009) + renderer
```

Tres detalles de orden que importan. La regla del 3x3 solo se vigila
**dentro** del braiding, consultando `would_open_3x3` antes de cada
apertura extra, porque el árbol de expansión no puede crear áreas
abiertas (ADR-003). El validador corre **antes** que el solver: si la
conectividad falla, el error sale del validador con un mensaje
específico, y el `MazeError` de "sin camino" del solver queda como red
de seguridad que en producción no debería saltar nunca (ADR-015). Y el
generador no imprime nada: expone `pattern_skipped` y es
`a_maze_ing.py` quien saca el aviso por `stderr`. Una librería que
imprime es una librería que molesta en el proyecto que la reutilice.

El validador comprueba, en este orden, borde exterior cerrado,
conectividad total de las celdas libres desde la entrada y ausencia de
bloques 3x3 abiertos (A5a). Después, según el modo (A5b): cero bucles
independientes en modo perfecto, que junto con la conectividad es la
definición de árbol de expansión; o al menos 2 bucles y como mucho 2
callejones reales en modo jugable. Esos umbrales son los del
analizador por defecto, el suelo del subject; el bonus de 0 callejones
lo persigue el braiding, no lo exige el validador (ADR-019). Los
comunes van primero porque `E − V + C` y la división de callejones solo
coinciden con el analizador en un laberinto conexo. Mide siempre con
código propio (ADR-017). Cuesta unos 2 ms en 20x15 y 80 ms en 100x100.

Errores del generador (ADR-020). Un parámetro imposible falla en el
constructor. Un paso que todavía es stub (braiding, Kruskal) sale como
`GenerationError` con un mensaje que dice qué falta. Un fallo del
validador es un bug nuestro: sale como *internal error, please report
it*, con todo lo que reconstruye el laberinto. Nada sale del generador
que no sea `MazeError`.

---

## 7. Fichero de configuración

El `config.txt` por defecto, tal cual está en el repo:

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

(El fichero real lleva además una cabecera y una explicación de cada
clave opcional, siempre en líneas de comentario completas.)

**Solo comentarios de línea completa** (ADR-014). El subject define las
líneas que empiezan por `#` y nada más. Si el parser admite o no
comentarios al final de una línea es decisión de B1, pero el fichero
por defecto no depende de ello: funciona con la lectura más estricta.

**Las claves son insensibles a mayúsculas**: la hoja de evaluación dice
explícitamente que `width=20` es tan válido como `WIDTH=20`. Los
valores booleanos también (`true`, `True`, `TRUE`). El nombre del
fichero de salida y el del algoritmo se respetan tal cual. Un carácter
sin glifo en `PATTERN` es un `ConfigError` explícito (ADR-012).

**Las opcionales van comentadas.** Sin `SEED`, cada ejecución da un
laberinto distinto; para comprobar la reproducibilidad, el evaluador
quita una almohadilla y no toca ningún otro fichero, que es lo que pide
la hoja. `ALGORITHM` y `PATTERN` aparecen con su valor por defecto, así
que descomentarlas tal cual no cambia nada.

El evaluador va a editar este fichero delante de vosotros para provocar
errores. Los cinco casos exactos que probará, todos con mensaje claro y
salida con código 1:

| Qué hace el evaluador | Quién lo detecta |
|---|---|
| Borrar una clave obligatoria | `parse_config`, lista `MANDATORY_KEYS` |
| Añadir una línea sin `=` | `parse_config` |
| Poner letras donde van números | `parse_int` |
| Poner un booleano inválido en `PERFECT` | `parse_bool` |
| Romper el formato de tupla de `ENTRY` o `EXIT` | `parse_coords` |

---

## 8. Cómo se evalúa

Repaso de la hoja de evaluación contra lo que tenemos. Todo lo que
aparece antes de los bonus es eliminatorio: cualquier elemento que
falte pone la nota a 0.

| Apartado de la hoja | Dónde se cubre | Estado |
|---|---|---|
| Ficheros presentes: `README.md`, `a_maze_ing.py`, `mazegen-*.whl`, fichero de configuración, fuentes para reconstruir el paquete | raíz del repo | hechos `a_maze_ing.py` y `config.txt`; faltan README, wheel y `pyproject.toml` |
| Norm (`flake8`) y `mypy` sobre los ficheros Python | `make lint`, `make lint-strict` | pasa, también `--strict` |
| README con sus 11 elementos obligatorios | `README.md` | pendiente, ver 8.1 |
| Laberinto aleatorio mostrado al arrancar con la config por defecto | `a_maze_ing.py` + `renderer.py` | `config.txt` y motor en modo perfecto hechos; faltan `renderer`, `writer` y el braiding |
| Menú: regenerar, mostrar/ocultar camino, cambiar color de muros | `menu.py` | firmas listas |
| Formato del fichero de configuración, claves en minúscula incluidas | `config_parser.py` | firmas listas, ver 7 |
| Gestión de los cinco errores de configuración | `config_parser.py` | firmas listas, ver 7 |
| Fichero de salida: `HEIGHT` líneas, línea vacía, entry, exit, camino | `writer.py` + ADR-009 | firmas listas |
| El camino del fichero coincide con el de la pantalla | ambos leen `maze.solution` | estructural |
| El camino es el más corto | `solver.py` + `tests/test_solver.py` | hecho; nada externo lo comprueba, ver 8.2 |
| Coherencia de muros validada con el analizador | ADR-001 | estructural, medido en 40 laberintos generados (`test_analyzer.py`) |
| Todas las celdas alcanzables salvo el "42" | `validator.is_connected` | hecho (A5a) |
| Muros en todo el contorno | invariante 2 + `validator.borders_closed` | estructural y comprobado (A5a) |
| Sin zonas abiertas de 3x3, y saber explicar cómo se verifica | `validator.open_areas_3x3` + `braiding.would_open_3x3` | validador hecho, 12 muros interiores (ADR-017); braiding pendiente (A6) |
| "42" presente, o mensaje en terminal si no cabe | `pattern.py` + aviso en `a_maze_ing.py` | hecho |
| Laberinto perfecto si `PERFECT=True` | backtracker (ADR-016) + `validator.count_loops == 0` | hecho y comprobado en cada generación (ADR-019) |
| Mismo laberinto con la misma semilla | ADR-006 + clave `SEED` + solver determinista (ADR-015) | hecho en el motor |
| Parámetros inconsistentes (entry/exit fuera, tamaño negativo) | `validate_geometry` en el constructor | hecho |
| Reconstruir el paquete en un virtualenv e instalarlo en otro | `pyproject.toml` + `build` en `requirements-dev.txt` + README | pendiente, ver ADR-008 |

### 8.1 Elementos obligatorios del README

Los once. Que falte uno solo es un 0, así que se revisan en la fase
final con la hoja delante:

1. Primera línea en cursiva, exactamente: *This project has been
   created as part of the 42 curriculum by `<login1>`, `<login2>`.*
2. Sección **Description**: objetivo y visión general.
3. Sección **Instructions**: instalación y ejecución.
4. Sección **Resources**: referencias externas **y** cómo se ha usado
   la IA, diciendo en qué tareas y en qué partes del proyecto.
5. Descripción completa del fichero de configuración.
6. Algoritmo de generación elegido.
7. Por qué ese algoritmo.
8. Documentación breve del módulo reutilizable: instanciarlo, pasarle
   parámetros, acceder a la estructura y a una solución.
9. Roles de cada miembro del equipo.
10. Planificación prevista y cómo evolucionó.
11. Qué funcionó bien, qué mejoraríamos, y qué herramientas concretas
    usamos.

El punto 8 tiene ya material: el contrato de `shortest_path` de la sección 4.

### 8.2 Qué mide exactamente el analizador

Leído del código de `maze_analyzer.py`. Son las reglas contra las que
se juega, así que conviene conocerlas antes de implementar:

- **Callejones.** Los divide en *real* y *enclosed*. Es real cuando
  alguno de sus muros cerrados da a una celda normal; es enclosed, y
  tolerado, cuando todos dan a una celda totalmente cerrada o al borde.
  `--max-dead-ends` solo limita los reales (ADR-011).
- **Bucles independientes.** `--min-loops`, por defecto 2. Los cuenta
  sobre la región alcanzable desde la entrada.
- **Esquinas y centro.** Exige las cuatro esquinas y *el centro* en la
  región alcanzable, pero define el centro como la celda central de la
  rejilla, o cualquiera de las dos o cuatro del medio si alguna
  dimensión es par, y le basta con que **una** sea alcanzable. Nuestro
  patrón nunca las bloquea todas: el bloque de 7 de ancho pone su
  columna de separación, siempre libre, justo en la columna central de
  la rejilla, tanto para anchuras pares como impares. Comprobado para
  todos los tamaños de 9x7 a 60x60.
- **Celdas aisladas.** Cuenta como corredor inalcanzable cualquier
  celda fuera de la región que no esté totalmente cerrada. Una celda
  del "42" está totalmente cerrada y no cuenta; una celda normal que
  quede aislada, sí, y hace el tablero no ganable.
- **Pie del fichero.** Parsea entrada y salida haciendo `int()` sobre
  las dos mitades de `x,y`. **No admite comentarios en esas líneas**:
  hay que escribir `0,0`, no `0,0   # entry`.
- **La línea del camino no la mira.** Del pie solo lee la entrada y la
  salida. Ni la validez ni la optimalidad del camino las comprueba
  nadie fuera de nuestros tests: `tests/test_solver.py` es la única
  garantía, y por eso compara contra un oráculo independiente.

---

## 9. Reparto

**Vía A, motor** — Emmanuel: `maze.py`, `pattern.py`, `algorithms/`,
`solver.py`, `braiding.py`, `validator.py`, `generator.py`.

**Vía B, aplicación y entrega** — Lucas: `config_parser.py`,
`writer.py`, `renderer.py`, `menu.py`, empaquetado, licencia, README.

**Fase 0, común** — hecha por Emmanuel: `Makefile`, `.gitignore`,
`requirements-dev.txt`, `.flake8`, `mypy.ini` y `config.txt`. Dos puntos
tocan la vía B y por eso ADR-013 y ADR-014 están como propuestas: el
`pyproject.toml` no debe llevar sección `[tool.mypy]`, y el parser debe
aceptar el `config.txt` por defecto tal cual.

Innegociable: `maze.py` y `braiding.py` se repasan juntos
línea a línea, sean de quien sean.

Flujo git: `main`, ramas de feature, PR con revisión obligatoria del
otro antes de hacer merge. Los detalles prácticos están en la sección
10.

Con `tests/fixtures.py` ya escrito, la vía B puede arrancar sin esperar
al motor: `toy_maze()` devuelve un 5x5 resuelto, con su hexadecimal
(`d5553 / 95556 / c5553 / 95556 / c5557`) y su camino de 24
movimientos.

---

## 10. Pendiente de cerrar

Casi todo esto se cierra en una conversación con Lucas, no en el
código.

- **S1, en cuanto exista B5.** Cambiar el formateador provisional de
  `tests/test_analyzer.py` por `app.writer.write_maze`, generar el
  primer fichero con el writer real y pasarlo por el analizador. Debe
  decir *wall coherence OK*; si no, falla el contrato (ADR-018).
- **Repetir lint y tests en el repo.** Los ficheros de A3, A5a, A5b y
  A7a se verificaron contra una reconstrucción de los módulos de los
  que dependen: `make lint`, `make lint-strict` y `make test` sobre el
  repo real.
- **Para A6, antes de escribir código.** Qué significa exactamente
  `ensure_open`: con la conectividad garantizada, toda celda libre
  tiene ya al menos un lado abierto, así que "un lado abierto" no
  añade nada; ¿debe significar "no ser callejón"? Y el analizador
  cuenta como real un callejón aunque abrirlo crease un 3x3 (ADR-019):
  el braiding tiene que buscar otra salida, no rendirse.
- **Semilla cuando no hay `SEED`.** Si el generador eligiera y guardara
  su propia semilla, cualquier fallo interno sería reproducible y el
  menú podría mostrarla. Cambia el significado de la propiedad `seed`
  del contrato, así que se decide con Lucas (ADR-020).
- **Sugerencias para B2, a Lucas.** `warn_if_pattern_skipped` usa la
  constante `PATTERN`, no `config.pattern`: con `PATTERN=4` el aviso
  hablaría del "42" y de su tamaño mínimo. Y `a_maze_ing.py` solo
  captura `MazeError`: si `parse_config` o `write_maze` dejan escapar
  un `OSError` (fichero inexistente, `OUTPUT_FILE` en un directorio que
  no existe, ver C3), es un traceback. O lo envuelven B1 y B5, o lo
  captura el entry point.
- **Confirmar ADR-013 y ADR-014.** En concreto, que el `pyproject.toml`
  de B6 no llevará `[tool.mypy]`, y que el parser de B1 aceptará el
  `config.txt` por defecto. Si admite comentarios al final de línea o
  no, lo decide él.
- **T0.3, detalles del flujo git.** Propuesta: ramas con el ID de la
  tarea (`a3-backtracker`, `b1-config-parser`) y repo de trabajo en
  GitHub, porque el repo de entrega de la intra no tiene PR, con el de
  la intra como segundo remote para el push final.
- **`maze_analyzer.py` en el repo o fuera.** Hoy está en el
  `.gitignore`; B9 decide si lo necesita dentro.

Cuando aparezca una decisión nueva se anota aquí, y al decidirse se
mueve a `DECISIONS.md` como ADR.

---

## 11. Riesgos conocidos

- **El wheel y el `.gitignore`.** Mitigado: `!/mazegen-*.whl` lo
  re-incluye incluso contra un `.gitignore` global que excluya `*.whl`
  (probado). Aun así, tras el primer build, comprobar con `git status`
  que el fichero se está subiendo de verdad.
- **Probar el wheel fuera del repositorio.** Con el layout plano,
  ejecutar desde la raíz importa siempre la carpeta local, nunca el
  paquete instalado. La prueba de instalación que pide la hoja solo
  demuestra algo si se hace en otra carpeta, copiando `a_maze_ing.py` y
  el fichero de configuración (ADR-008).
- **`make install` necesita el módulo `venv` y red.** En Debian y
  Ubuntu, `python3 -m venv` exige el paquete `python3-venv`. Sin
  comprobar todavía en las máquinas del campus.
- **La config por defecto no arranca hasta A6.** `PERFECT=False` pasa
  por el braiding. Desde A7a sale con un error claro en lugar de un
  traceback, pero sigue sin generar. Con `PERFECT=True` el motor ya
  completa; el programa necesita además B3 y B5.
- **El validador puede tumbar un braiding casi perfecto.** Si `braid`
  se rinde con 3 callejones reales en alguna rejilla, `validate` lo
  convierte en *internal error* y el programa sale con código 1. Medir
  en A6 en todos los tamaños desde 3x3, incluidos los pequeños sin
  "42".
- El braiding puede entrar en conflicto con la regla del 3x3 en
  laberintos pequeños. Medido hasta ahora: sin problemas desde 9x7 con
  un braiding ingenuo, pero el prototipo no es el código final.
- El empaquetado es lo único del proyecto que no cubre ningún módulo
  del cursus: contar 2 o 3 horas de aprendizaje, no 30 minutos.
- Los bonus solo cuentan si **todo** lo anterior está correcto. No
  tiene sentido tocar Kruskal mientras falte un elemento del README.

---
