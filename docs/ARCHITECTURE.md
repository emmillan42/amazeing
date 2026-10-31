# A-Maze-ing — Arquitectura y contrato

Documento vivo. Se **reescribe entero** cuando algo cambia, y la
versión nueva sustituye a la anterior en los documentos del proyecto.
Describe cómo está montado el proyecto ahora mismo.

El *porqué* de cada decisión no está aquí: está en `DECISIONS.md`, en
formato ADR y en orden cronológico. Aquí solo se cita el número.

Última actualización: 31 oct 2026 · **fase final**: S2, S3, C2 y C3
cerradas; C1 cerrada salvo la subida a vogsphere, que solo se puede
hacer desde el campus (ADR-031) · C3 dejó cinco arreglos en la
aplicación (ADR-030) y el clon limpio, un wheel reconstruido y una
protección contra CRLF en `make package` (ADR-031) · queda la subida a la intra y C4. El avance por tareas está en
`PLAN.md`.

---

## 1. Estado

| Bloque | Estado |
|---|---|
| `errors.py`, `maze.py` | implementados y probados |
| `pattern.py` | implementado y probado, con la colocación de ADR-025 (A9, ADR-026) |
| `solver.py` | implementado y probado: 207 tests contra un oráculo de fuerza bruta (A4) |
| `algorithms/backtracker.py` | implementado y probado (A3, ADR-016) |
| `algorithms/__init__.py`, `algorithms/base.py` | registro y clase base, hechos |
| `algorithms/kruskal.py` | implementado y probado (A8, bonus, ADR-027) |
| `validator.py` | completo: chequeos comunes (A5a, ADR-017) y por modo (A5b, ADR-019) |
| `braiding.py` | completo (A6, ADR-021 y ADR-022) |
| `generator.py` | completo: los dos modos, y errores reproducibles en los tres pasos que solo fallan por un bug (A7a, A7b, A8; ADR-020, ADR-023, ADR-027) |
| `mazegen/__init__.py` | fachada, hecha |
| `app/config_parser.py`, `writer.py`, `renderer.py`, `menu.py` | completos (B1, B3, B4, B5, ADR-024); el parser y el menú, con los arreglos de C3 (ADR-030) |
| `a_maze_ing.py` | completo (B2); el aviso del "42" llega al menú (ADR-030) |
| `mazegen/README.md`, `mazegen/py.typed` | documentación del módulo y marcador PEP 561, dentro del wheel (B6, ADR-028) |
| `tests/` | 845 tests: motor, vía B, analizador en ambos modos, documentación, README y casos límite (ADR-026, ADR-028, ADR-029, ADR-030) |
| `Makefile`, `.gitignore`, `.gitattributes`, `requirements-dev.txt`, `.flake8`, `mypy.ini` | hechos (T0.1; `.gitattributes`, ADR-024; targets `package` y `package-test`, ADR-028; protección contra CRLF, ADR-031) |
| `config.txt` | hecho (T0.2) |
| `pyproject.toml`, `LICENSE.md` | hechos (B6, B7, ADR-028) |
| `mazegen-1.0.0-py3-none-any.whl` | en la raíz y subido; reproducible bit a bit, comprobado en un clon limpio (B6, ADR-028, ADR-031) |
| `README.md` | completo y vigilado por `test_readme.py` (B8, ADR-029) |
| `docs/GUIA_ESTUDIO.md`, `docs/GUIA_DEFENSA.md`, `docs/COMO_FUNCIONA.md` | material de C4, comprobado contra el código el 31 de octubre |

**Verificado en el repo real y en un clon limpio de GitHub.** En el
repo de trabajo, con la copia local del analizador: `make lint` y
`make lint-strict` pasan en 39 ficheros y `make test` da 845 passed. En
el clon, como lo verá el evaluador: 38 ficheros, 796 passed y 34
skipped (los que necesitan el analizador), `make package-test` en verde,
y `make package` deja `git status` vacío. El wheel sale con el mismo
hash en las dos carpetas (ADR-031).

**S2 y S3 a mano**, con el `config.txt` del repo y `make run`: en modo
perfecto, *PERFECT maze*, 280 celdas alcanzables y 0 bucles, y el
fichero con 15 líneas de 20 caracteres, línea vacía, `0,0`, `19,14` y
el camino; con `SEED=42`, dos ejecuciones dan el mismo fichero. En
modo jugable, *bonus-grade* con `0 real + 3 enclosed` y 31 bucles. Con
el "42" y semilla 42 en 20x15, el motor da 27 bucles; con Kruskal,
`84 + 3` en perfecto y `0 + 3` con 58 bucles en jugable; con
`PATTERN=4`, *bonus-grade* y centro alcanzable en 9x7 y 20x15.

**Programa completo.** `python3 a_maze_ing.py config.txt` genera,
escribe el fichero, dibuja y abre el menú. Los cinco errores de la hoja
y todos los casos límite de C3 terminan con un mensaje claro y código
1, sin traceback; `tests/test_edge_cases.py` los recorre a través de
`main()` (ADR-030).

**Lo que falta.** Subir a vogsphere desde un ordenador del campus y
repetir allí las comprobaciones (ADR-031), C4 y el repaso conjunto de
`maze.py` y `braiding.py` (§10).

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
| 013 | Herramientas en `.venv` con versiones fijadas; lint configurado en `.flake8` y `mypy.ini` | Aceptada |
| 014 | `config.txt` solo con comentarios de línea completa; opcionales comentadas | Aceptada |
| 015 | `shortest_path` lanza `MazeError` si no hay camino; desempate N, E, S, O | Aceptada |
| 016 | Backtracker como DFS iterativo con pila explícita | Aceptada |
| 017 | El validador no reutiliza lo que valida; 3x3 abierto = 12 muros interiores abiertos | Aceptada |
| 018 | Analizador antes de B5: helpers provisionales en `tests/` | Aceptada |
| 019 | Chequeos por modo: `E − V + C` sobre las libres; umbrales del analizador como suelo | Aceptada |
| 020 | Generador: parámetros en el constructor, stubs como `GenerationError`, fallos internos reproducibles | Aceptada; ADR-027 retira la parte de los stubs |
| 021 | Braiding: atascos forzados abriendo y cerrando; esquinas y centro sin callejones reales; `braid` garantiza los bucles | Aceptada |
| 022 | Braiding: consultas puras, una sola lista de callejones contada por aritmética | Aceptada |
| 023 | Fallos del braiding como errores internos; el generador no se fía del recuento de `braid` | Aceptada |
| 024 | Vía B: se adaptan los ficheros en la integración; el parser solo comprueba sintaxis y tipos | Aceptada; matizada por ADR-030 |
| 025 | Patrón con una columna libre sobre la columna central; ancho mínimo `4n + 4` con `n` impar | Aceptada, implementada (ADR-026) |
| 026 | Implementación de ADR-025: la posición del patrón se busca, no se calcula | Aceptada |
| 027 | Kruskal: union-find sobre `dict` por celda, unión por tamaño, `find` iterativo; `_carve` informa sus fallos como error interno | Aceptada |
| 028 | Wheel reproducible en la raíz, con su documentación y `py.typed`, probado fuera del repo | Aceptada; completada por ADR-031 |
| 029 | El README y el analizador en ambos modos, vigilados por tests | Aceptada |
| 030 | C3: el aviso del "42" en el menú, `MAX_SIDE = 500`, un mensaje por tupla mal formada, BOM y entrada no UTF-8 | Aceptada |
| 031 | Clon limpio: `make package` rechaza CRLF; el analizador fuera del repo; GitHub como única fuente de verdad | Aceptada |

---

## 3. Árbol

```
.
├── a_maze_ing.py          entry point: argv, orquestación, errores [hecho]
├── config.txt             configuración por defecto                [hecho]
├── Makefile               install/run/.../package, sin CRLF        [hecho]
├── requirements-dev.txt   herramientas de desarrollo               [hecho]
├── .flake8                exclusiones de flake8                    [hecho]
├── mypy.ini               exclusiones de mypy                      [hecho]
├── .gitignore             re-incluye el wheel de la raíz           [hecho]
├── .gitattributes         LF en todo el repo                       [hecho]
├── pyproject.toml         construye mazegen-1.0.0                  [hecho]
├── mazegen-1.0.0-py3-none-any.whl  reproducible (ADR-028)          [hecho]
├── LICENSE.md             MIT                                      [hecho]
├── README.md              en inglés, vigilado por un test          [hecho]
│
├── docs/
│   ├── ARCHITECTURE.md    este fichero, se reescribe entero
│   ├── DECISIONS.md       ADRs, solo se añade al final
│   └── PLAN.md            inventario de tareas y cronogramas
│
├── mazegen/               ← REUTILIZABLE, esto es el wheel
│   ├── __init__.py        fachada: MazeGenerator, Maze, errores
│   ├── README.md          documentación del módulo           [hecho]
│   ├── py.typed           marcador PEP 561                   [hecho]
│   ├── errors.py          MazeError y subclases
│   ├── maze.py            Maze, Direction, validate_geometry [hecho]
│   ├── pattern.py         glifos, colocación, mínimo         [hecho]
│   ├── solver.py          BFS → camino más corto             [hecho]
│   ├── braiding.py        bucles, callejones, regla 3x3      [hecho]
│   ├── validator.py       invariantes, los dos modos         [hecho]
│   ├── generator.py       MazeGenerator, pipeline            [hecho]
│   └── algorithms/
│       ├── __init__.py    registro y get_algorithm()         [hecho]
│       ├── base.py        Algorithm(ABC)                     [hecho]
│       ├── backtracker.py DFS iterativo                      [hecho]
│       └── kruskal.py     bonus, union-find                  [hecho]
│
├── app/                   ← NO reutilizable
│   ├── __init__.py        marcador de la capa de aplicación
│   ├── config_parser.py   KEY=VALUE → Config, MAX_SIDE       [hecho]
│   ├── writer.py          fichero de salida                  [hecho]
│   ├── renderer.py        ASCII + ANSI, Palette              [hecho]
│   └── menu.py            bucle interactivo                  [hecho]
│
└── tests/                 sin __init__.py (ADR-018)
    ├── conftest.py        fixtures analyzer y judge          [hecho]
    ├── fixtures.py        laberinto 5x5 a mano               [hecho]
    ├── test_solver.py     BFS contra fuerza bruta            [hecho]
    ├── test_backtracker.py árbol de expansión, semilla       [hecho]
    ├── test_kruskal.py    árbol de expansión, union-find     [hecho]
    ├── test_kruskal_pipeline.py  Kruskal, generador y analizador [hecho]
    ├── test_pattern.py    colocación, mínimos, el "42" intacto   [hecho]
    ├── test_pattern_playable.py  analizador con textos impares   [hecho]
    ├── test_validator.py  cada chequeo, roto a propósito     [hecho]
    ├── test_braiding.py   braiding, validador como oráculo   [hecho]
    ├── test_generator.py  errores del pipeline               [hecho]
    ├── test_generator_playable.py  pipeline en modo jugable  [hecho]
    ├── test_analyzer.py   writer real vs analizador (S1)     [hecho]
    ├── test_analyzer_modes.py  cada algoritmo, ambos modos   [hecho]
    ├── test_package_docs.py  ejecuta la doc del módulo       [hecho]
    ├── test_readme.py     lo que la hoja castiga con un 0    [hecho]
    ├── test_config_parser.py  la hoja, caso a caso           [hecho]
    ├── test_edge_cases.py la lista de C3, a través de main() [hecho]
    ├── test_writer.py     formato exacto del fichero         [hecho]
    ├── test_renderer.py   cada muro, entrada, salida, camino [hecho]
    └── test_menu.py       sesiones de teclado guionizadas    [hecho]
```

`tests/` no es un paquete y sus módulos no se importan entre sí: con
`mypy .`, importar un módulo de `tests/` desde otro da *Source file
found twice* (ADR-018). Lo compartido va en `tests/conftest.py` como
fixture: `analyzer` importa el analizador o salta el test si no hay
copia local, y `judge` escribe un laberinto con el writer real y
devuelve el informe y el veredicto (ADR-026).

`maze_analyzer.py` no está en el árbol, y no va a estar: es de la intra
y está en el `.gitignore` (ADR-031). Se puede tener una copia local en
la raíz, y pasa el lint igualmente. Sin ella, los tests que lo usan se
saltan; con ella, en el repo de trabajo, no se salta ninguno (ADR-013,
ADR-018).

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
| `package` | Se niega a construir si algún fichero que entra en el paquete tiene CRLF (ADR-031). Borra `build/` y el wheel anterior y construye `mazegen-1.0.0-py3-none-any.whl` en la raíz, con fecha fija: mismo código, mismos bytes (ADR-028) |
| `package-test` | Instala el wheel en un virtualenv nuevo en `/tmp`, copia `a_maze_ing.py`, `app/` y la configuración, comprueba que `mazegen` viene de `site-packages` y ejecuta el programa |

Regla: todo cambio en `mazegen/` va con `make package` en el mismo
commit. Comprobarlo es inmediato: tras `make package`, `git status`
tiene que salir vacío. Esa comprobación solo vale en una carpeta cuyos
ficheros estén como en el repo: el wheel se construye desde la carpeta
de trabajo, y por eso `package` rechaza los CRLF (ADR-031).

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
        # GenerationError: bug del algoritmo, del braiding o del
        # validador (el mensaje lleva los argumentos, la semilla y el
        # número de llamada). No queda ningún algoritmo stub.
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
    # deja como mucho max_dead_ends callejones reales, al menos
    # MIN_LOOPS bucles y ningún 3x3; devuelve los callejones que quedan
braiding.ensure_open(maze, rng) -> None
    # esquinas y centro no son callejones reales (ADR-021)
braiding.would_open_3x3(maze, x, y, d) -> bool   # consulta pura
braiding.dead_ends(maze) -> list[Cell]        # solo los reales, fila a fila
validator.validate(maze, *, perfect) -> None
validator.count_loops(maze) -> int                   # E - V + C
validator.count_dead_ends(maze) -> tuple[int, int]   # (real, enclosed)
validator.MIN_LOOPS = 2; validator.MAX_REAL_DEAD_ENDS = 2
pattern.stamp(maze, text="42") -> set[Cell]
pattern.minimum_grid(text="42") -> tuple[int, int]
pattern.fits(width, height, text="42") -> bool
algorithms.get_algorithm(name) -> Algorithm
app.config_parser.parse_config(path) -> Config      # ConfigError
app.writer.format_maze(maze) -> str
app.writer.write_maze(path, maze) -> None           # MazeError si no escribe
app.renderer.render(maze, show_path=False, palette=PALETTES[0]) -> str
app.renderer.PALETTES: tuple[Palette, ...]          # al menos 2 colores de muro
app.menu.Menu(generator, config, *, notice="").run() -> None
    # tras el primer generate(); notice se muestra en todas las
    # pantallas, bajo el laberinto (ADR-030)
app.config_parser.MAX_SIDE = 500     # máximo de WIDTH y HEIGHT (ADR-030)
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
  → estampar el patrón, con la columna (W − 1) // 2 libre (ADR-025)
                       ¿no cabe? → pattern_skipped = True, sigue
  → árbol de expansión sobre las celdas libres (backtracker o Kruskal)
  → si PERFECT=False: braid (0 callejones reales, ≥ 2 bucles)
    + ensure_open (esquinas y centro); un fallo aquí es un bug
  → validator (siempre, también en producción)
  → solver BFS → maze.set_solution(...)
  → writer (una sola vez, ADR-009) + renderer + menú (ADR-024)
```

Tres detalles de orden que importan. La regla del 3x3 solo se vigila
**dentro** del braiding, consultando `would_open_3x3` antes de cada
apertura extra, porque el árbol de expansión no puede crear áreas
abiertas (ADR-003). Cuando todas las salidas de un callejón crearían un
3x3, el braiding abre igualmente y cierra un muro del bloque que
completó, sin perder conectividad ni crear callejones (ADR-021). El validador corre **antes** que el solver: si la
conectividad falla, el error sale del validador con un mensaje
específico, y el `MazeError` de "sin camino" del solver queda como red
de seguridad que en producción no debería saltar nunca (ADR-015). Y el
generador no imprime nada: expone `pattern_skipped` y es
`a_maze_ing.py` quien construye el aviso, lo saca por `stderr` y se lo
pasa al menú, que lo muestra en cada pantalla; si no, el primer borrado
de pantalla lo haría desaparecer (ADR-030). Una librería que imprime es
una librería que molesta en el proyecto que la reutilice.

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

Errores del generador (ADR-020, ADR-023, ADR-027). Un parámetro
imposible falla en el constructor. Un fallo del algoritmo, del braiding
o del validador es un bug nuestro: sale como *internal error, please
report it*, con todo lo que reconstruye el laberinto. Ya no quedan
algoritmos stub, y un test sobre todo el registro lo garantiza. El
generador ignora lo que `braid` dice de sí mismo: lo mide el validador.
Nada sale del generador que no sea `MazeError`.

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

**El parser comprueba sintaxis, tipos y los límites del programa**
(ADR-024, ADR-030). Que el tamaño sea posible, que la entrada y la
salida estén dentro, o que el algoritmo exista, lo valida
`MazeGenerator`: una regla, un sitio. El parser solo pone el máximo,
`MAX_SIDE = 500` para `WIDTH` y `HEIGHT`, porque es un presupuesto de
esta aplicación, no una regla de la librería: 500x500 en modo jugable
tarda unos 9 segundos, y un tamaño mucho mayor agotaría la memoria
antes de cualquier comprobación. Un BOM al principio del fichero se
ignora. Una
clave desconocida o repetida es un error con número de línea, para que
un `SEDD=4` no se ignore en silencio. `SEED` o `ALGORITHM` vacíos toman
su valor por defecto; `PATTERN` vacío no dibuja nada.

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
| Romper el formato de tupla de `ENTRY` o `EXIT` | `parse_coords`: un solo mensaje con el valor completo (ADR-030) |

---

## 8. Cómo se evalúa

Repaso de la hoja de evaluación contra lo que tenemos. Todo lo que
aparece antes de los bonus es eliminatorio: cualquier elemento que
falte pone la nota a 0.

| Apartado de la hoja | Dónde se cubre | Estado |
|---|---|---|
| Ficheros presentes: `README.md`, `a_maze_ing.py`, `mazegen-*.whl`, fichero de configuración, fuentes para reconstruir el paquete | raíz del repo | todos hechos y subidos |
| Norm (`flake8`) y `mypy` sobre los ficheros Python | `make lint`, `make lint-strict` | pasa en los 38 ficheros del clon limpio, también `--strict` (ADR-031) |
| README con sus 11 elementos obligatorios | `README.md` | hecho; `test_readme.py` vigila la primera línea, las secciones, su orden y la documentación del módulo (ADR-029) |
| Laberinto aleatorio mostrado al arrancar con la config por defecto | `a_maze_ing.py` + `renderer.py` | hecho; todo muro, entrada y salida comprobados en `test_renderer.py` |
| Menú: regenerar, mostrar/ocultar camino, cambiar color de muros | `menu.py` | hecho, más guardar (ADR-009) |
| Formato del fichero de configuración, claves en minúscula incluidas | `config_parser.py` | hecho, ver 7 |
| Gestión de los cinco errores de configuración | `config_parser.py` | hecho, cada caso en `test_config_parser.py` |
| Fichero de salida: `HEIGHT` líneas, línea vacía, entry, exit, camino | `writer.py` + ADR-009 | hecho |
| El camino del fichero coincide con el de la pantalla | ambos leen `maze.solution` | estructural |
| El camino es el más corto | `solver.py` + `tests/test_solver.py` | hecho; nada externo lo comprueba, ver 8.2 |
| Coherencia de muros validada con el analizador | ADR-001 + `writer.py` | estructural; medido en 40 laberintos escritos con el writer real (S1) |
| Todas las celdas alcanzables salvo el "42" | `validator.is_connected` | hecho (A5a) |
| Muros en todo el contorno | invariante 2 + `validator.borders_closed` | estructural y comprobado (A5a) |
| Sin zonas abiertas de 3x3, y saber explicar cómo se verifica | `validator.open_areas_3x3` + `braiding.would_open_3x3` | hechos, 12 muros interiores (ADR-017), como mucho 6 bloques por muro (ADR-022) |
| "42" presente, o mensaje en terminal si no cabe | `pattern.py` + aviso en `a_maze_ing.py` y en el menú | hecho, también con textos de longitud impar; el aviso se queda en pantalla, bajo el laberinto (ADR-026, ADR-030) |
| Laberinto perfecto si `PERFECT=True` | backtracker (ADR-016) + `validator.count_loops == 0` | hecho y comprobado en cada generación (ADR-019) |
| Tablero Pac-Man si `PERFECT=False`: conexo, esquinas y centro, ≥ 2 bucles, pocos callejones | `braiding.py` + `validator` (ADR-019, ADR-021) | hecho y comprobado en cada generación |
| Bonus: ningún callejón real (`--max-dead-ends 0`) | `braid(..., max_dead_ends=0)` | hecho, medido en 865 tableros con el analizador (ADR-022), también sobre Kruskal (ADR-027) |
| Bonus: varios algoritmos de generación | `ALGORITHM=backtracker` o `kruskal` (ADR-016, ADR-027) | hecho; los dos pasan el analizador en ambos modos (`test_analyzer_modes.py`) y el README los describe |
| Mismo laberinto con la misma semilla | ADR-006 + clave `SEED` + solver determinista (ADR-015) | hecho en el motor, también con braiding |
| Parámetros inconsistentes (entry/exit fuera, tamaño negativo) | `validate_geometry` en el constructor; el máximo, en el parser | hecho, con la lista de C3 recorrida en `test_edge_cases.py` (ADR-030) |
| Reconstruir el paquete en un virtualenv e instalarlo en otro | `make package`, `make package-test` + Instructions del README (ADR-028) | hecho y probado en el repo, en un clon limpio y fuera de los dos, con el `a_maze_ing.py` real; el README da los comandos a mano (ADR-031) |

### 8.1 Elementos obligatorios del README

Los once. Que falte uno solo es un 0. Están todos, y
`tests/test_readme.py` comprueba su presencia (ADR-029); en la fase final
se revisa además su contenido con la hoja delante:

1. Primera línea en cursiva, exactamente: *This project has been
   created as part of the 42 curriculum by `<login1>`, `<login2>`.*
2. Sección **Description**: objetivo y visión general.
3. Sección **Instructions**: instalación y ejecución.
4. Sección **Resources**: referencias externas y cómo se ha usado
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

El punto 8 es la copia de `mazegen/README.md`, la documentación que va
dentro del wheel; si se edita una copia sin la otra, falla el test. La
sección *Planning and how it evolved* llega hasta C3 y el clon limpio;
si C4 cambia algo, se añade.

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
  dimensión es par, y le basta con que **una** sea alcanzable. Con el
  "42" nunca las bloquea todas: el bloque de 7 de ancho pone su
  columna de separación, siempre libre, justo en la columna central de
  la rejilla, tanto para anchuras pares como impares. Comprobado para
  todos los tamaños de 9x7 a 60x60. Con un número impar de glifos, el
  bloque centrado sí las bloqueaba (medido con `PATTERN=4`). Desde
  ADR-025 la columna central queda libre con cualquier texto, y
  `tests/test_pattern.py` lo comprueba.
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
La integración de las dos vías se hizo juntos, y durante ella se
ajustaron los ficheros de la aplicación al contrato (ADR-024). B6, B8 y B9
se cerraron juntos el 31 de octubre.

**Fase 0, común** — hecha por ambos: `Makefile`, `.gitignore`,
`.gitattributes`, `requirements-dev.txt`, `.flake8`, `mypy.ini` y
`config.txt`. ADR-013 y ADR-014 quedaron confirmadas con la vía B.

Innegociable: `maze.py` y `braiding.py` se repasan juntos
línea a línea, sean de quien sean.

Flujo git: `main` en GitHub, que es la única fuente de verdad. La
entrega se sube a vogsphere solo desde un ordenador del campus: se
clona GitHub, se añade el remote de la intra y se sube. Un arreglo
descubierto en el campus va primero a GitHub (ADR-031).

Con `tests/fixtures.py` ya escrito, la vía B puede arrancar sin esperar
al motor: `toy_maze()` devuelve un 5x5 resuelto, con su hexadecimal
(`d5553 / 95556 / c5553 / 95556 / c5557`) y su camino de 24
movimientos.

---

## 10. Pendiente de cerrar

Todo es de la fase final, que se hace entre los dos (PLAN, bloque 5).

- **La subida a vogsphere, en el campus** (ADR-031). Desde un
  ordenador del campus: clonar GitHub, `git remote add intra
  <url-vogsphere>` y `git push intra main`. Después, clonar la intra en
  una carpeta vacía y comprobar el hash; si el clon sale vacío porque el
  servidor espera `master`, `git push intra main:master`. En ese clon,
  lo que verá el evaluador: `make install`, `make lint`, `make
  lint-strict`, `make test` (796 passed, 34 skipped), `make package` con
  `git status` vacío, `make package-test`, el caso de entrada no UTF-8
  con el locale real del campus y el tiempo de 500x500. Si allí pasa de
  20 segundos, `MAX_SIDE` baja a 400 (ADR-030). Si el wheel sale
  modificado, se compara el contenido antes de nada: otra versión de
  zlib comprime distinto.
- **La etiqueta `v1.0.0`** en el commit entregado, una vez comprobado
  el clon de la intra. Se pone en casa y se sube a GitHub.
- **C4, el ensayo de defensa.** Cada uno explica los módulos del otro.
- **Una mutación del braiding que la suite no detecta.** En
  `_fix_dead_end`, elegir entre todos los lados (`openable`) en lugar de
  `safe or openable` deja los 845 tests en verde. El validador la para
  en producción: con Kruskal, 5x5 y semilla 182, sale un error interno
  por un 3x3 abierto. Un test que recorra el pipeline con varias
  semillas en rejillas pequeñas la detectaría. Opcional: no afecta a la
  nota, pero es la clase de hueco que ADR-022 quería cerrar.
- **El repaso conjunto de `maze.py` y `braiding.py`**, que sigue
  siendo innegociable (§9).
- **Semilla cuando no hay `SEED`.** Si el generador eligiera y guardara
  su propia semilla, cualquier fallo interno sería reproducible y el
  menú podría mostrarla. Cambia el significado de la propiedad `seed`
  del contrato, así que se decide juntos (ADR-020). Opcional.
- **Finales de línea en la máquina de Lucas.** `files.eol` en `\n` en su
  VS Code, y después de cada `pull`, `git ls-files --eol | awk '$2 ==
  "w/crlf"'` vacío. La protección de `make package` lo detecta, pero
  solo en los ficheros del paquete (ADR-031).

Cuando aparezca una decisión nueva se anota aquí, y al decidirse se
mueve a `DECISIONS.md` como ADR.

---

## 11. Riesgos conocidos

- **Un wheel desfasado.** Si se cambia `mazegen/` sin `make package`,
  el wheel subido deja de corresponder al código. Se detecta al
  instante: tras `make package`, `git status` no sale vacío (ADR-028).
- **Un wheel construido desde ficheros en CRLF.** El wheel sale de la
  carpeta de trabajo, no del repo: ya pasó con `LICENSE.md`, y solo lo
  sacó el clon limpio. `make package` se niega ahora a construir con un
  CRLF en los ficheros del paquete (ADR-031).
- **Probar el wheel fuera del repositorio.** Con el layout plano,
  ejecutar desde la raíz importa siempre la carpeta local, nunca el
  paquete instalado. La prueba solo demuestra algo en otra carpeta, y
  hay que copiar también `app/`: `make package-test` lo hace (ADR-028).
- **`make package` necesita red** la primera vez, para descargar
  `setuptools` en su entorno aislado.
- **`make install` necesita el módulo `venv` y red.** En Debian y
  Ubuntu, `python3 -m venv` exige el paquete `python3-venv`. Se
  comprueba al subir a vogsphere desde el campus (§10).
- **El braiding y los árboles de Kruskal.** Cerrado (ADR-027): con el
  algoritmo real, la apertura forzada se usa en 1 de cada 7 a 9 rejillas
  de 3x3, y todos los tableros dan *bonus-grade*. Un test con un espía
  exige que se siga llegando a ella.
- **Los ficheros de los dos y los finales de línea.** `.gitattributes`
  guarda LF en el repo, pero una carpeta de trabajo puede tener ficheros
  en CRLF sin que `git status` lo muestre: siete en la de Emmanuel, que
  venían de la máquina de Lucas. Para arreglar uno sin perder cambios,
  `sed -i 's/\r$//' FICHERO`; si no tiene cambios sin commitear,
  también vale borrarlo y `git checkout -- FICHERO` (ADR-031).
- **El renderer en laberintos anchos.** Cada celda ocupa 4 columnas:
  un laberinto de 50 de ancho necesita una terminal de 201. No es un
  fallo, pero conviene que el evaluador no lo pruebe en una ventana
  pequeña sin saberlo.
- **El modo jugable cuesta más en rejillas grandes.** En el portátil de
  Emmanuel, 0,3 s en 100x100 y 8,8 s en 500x500, el máximo permitido;
  el coste crece casi lineal con las celdas. En una máquina tres veces
  más lenta, el máximo rondaría los 25 s: se mide en el campus (§10).
- **El menú borra la pantalla visible.** Lo que hubiera en la ventana
  antes de `make run` desaparece; el historial de la terminal se
  conserva. Es el borrado de cada frame. Dibujar en la pantalla
  alternativa lo evitaría, pero al salir desaparecería también el último
  laberinto, que hoy queda a la vista para compararlo con el fichero.
- Los bonus solo cuentan si **todo** lo anterior está correcto. Con los
  ficheros de la entrega completos y C3 cerrada, lo que puede poner un 0
  es que la subida a vogsphere no lleve lo que hemos verificado, o no
  saber explicar una parte del código en la defensa (C4).

---
