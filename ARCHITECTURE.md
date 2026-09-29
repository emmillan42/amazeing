# A-Maze-ing — Arquitectura y contrato

Documento vivo. Se **reescribe entero** cuando algo cambia, y la
versión nueva sustituye a la anterior en los documentos del proyecto.
Describe cómo está montado el proyecto ahora mismo.

El *porqué* de cada decisión no está aquí: está en `DECISIONS.md`, en
formato ADR y en orden cronológico. Aquí solo se cita el número.

Última actualización: 28 sep 2026 · Fase 0 cerrada.

---

## 1. Estado

| Bloque | Estado |
|---|---|
| `errors.py`, `maze.py`, `pattern.py` | implementados y probados |
| `generator.py` | `__init__` y pipeline reales, pasos delegados |
| `solver.py`, `braiding.py`, `validator.py`, `algorithms/*` | firmas y docstrings, cuerpo `NotImplementedError` |
| `app/*` | firmas y docstrings |
| `a_maze_ing.py` | implementado |
| `tests/fixtures.py` | laberinto 5x5 cableado, usable ya |
| `pyproject.toml`, `Makefile`, `config.txt`, `README.md`, `LICENSE.md` | pendientes |

Todo el árbol pasa `flake8 .` y `mypy . --strict` sin un solo aviso.

---

## 2. Decisiones cerradas

Índice. El detalle está en `DECISIONS.md`.

| ADR | Decisión |
|---|---|
| 001 | Muros como aristas compartidas (`v_walls` / `h_walls`) |
| 002 | El "42" se estampa antes de generar |
| 003 | Los dos modos son el mismo árbol de expansión más braiding |
| 004 | Centro = celda libre más cercana al centro geométrico |
| 005 | Render ASCII con ANSI, no MiniLibX |
| 006 | `random.Random(seed)` como instancia |
| 007 | Glifos 3x5, bloque 7x5, mínimo 9x7 |
| 008 | Paquete en la raíz, no en `src/` *(propuesta)* |

---

## 3. Árbol

```
.
├── a_maze_ing.py          entry point: argv, orquestación, errores
├── config.txt             configuración por defecto        [pendiente]
├── Makefile               install/run/debug/clean/lint     [pendiente]
├── pyproject.toml         construye mazegen-1.0.0          [pendiente]
├── mazegen-1.0.0-py3-none-any.whl                          [pendiente]
├── README.md  LICENSE.md  .gitignore                       [pendiente]
│
├── docs/
│   ├── ARCHITECTURE.md    este fichero, se reescribe entero
│   └── DECISIONS.md       ADRs, solo se añade al final
│
├── mazegen/               ← REUTILIZABLE, esto es el wheel
│   ├── __init__.py        fachada: MazeGenerator, Maze, errores
│   ├── errors.py          MazeError y subclases
│   ├── maze.py            Maze, Direction                  [hecho]
│   ├── pattern.py         glifos, tamaño mínimo, estampado [hecho]
│   ├── solver.py          BFS → camino más corto           [stub]
│   ├── braiding.py        bucles, callejones, regla 3x3    [stub]
│   ├── validator.py       invariantes                      [stub]
│   ├── generator.py       MazeGenerator, pipeline          [parcial]
│   └── algorithms/
│       ├── __init__.py    registro y get_algorithm()
│       ├── base.py        Algorithm(ABC)
│       ├── backtracker.py DFS iterativo                    [stub]
│       └── kruskal.py     bonus, union-find                [stub]
│
├── app/                   ← NO reutilizable
│   ├── config_parser.py   KEY=VALUE → Config               [stub]
│   ├── writer.py          fichero de salida                [stub]
│   ├── renderer.py        ASCII + ANSI                     [stub]
│   └── menu.py            bucle interactivo                [stub]
│
└── tests/
    └── fixtures.py        laberinto 5x5 a mano             [hecho]
```

---

## 4. Contrato

Estas firmas no se tocan sin avisar al compañero. Son lo que permite
trabajar en paralelo.

```python
class Direction(Enum):          # valor = (bit, dx, dy)
    NORTH = (1, 0, -1); EAST = (2, 1, 0)
    SOUTH = (4, 0, 1);  WEST = (8, -1, 0)
    bit: int; delta: tuple[int, int]; letter: str; opposite: Direction


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
    def solution_string(self) -> str         # "ESEEN..."
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
    def generate(self) -> Maze
    maze, seed, algorithm, pattern_cells, pattern_skipped


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
braiding.braid(maze, rng, max_dead_ends=0) -> int
braiding.ensure_open(maze, rng) -> None
braiding.would_open_3x3(maze, x, y, d) -> bool
braiding.dead_ends(maze) -> list[Cell]
validator.validate(maze, *, perfect) -> None
pattern.stamp(maze, text="42") -> set[Cell]
pattern.minimum_grid(text="42") -> tuple[int, int]
pattern.fits(width, height, text="42") -> bool
algorithms.get_algorithm(name) -> Algorithm
app.writer.write_maze(path, maze) -> None
app.renderer.render(maze, show_path, palette) -> str
```

`write_maze` recibe solo el laberinto porque el `Maze` ya lleva dentro
la entrada, la salida y la solución.

Excepciones, todas bajo `MazeError`: `ConfigError`,
`InvalidGeometryError`, `PatternTooLargeError`, `GenerationError`. Se
capturan en un único `try/except` en `a_maze_ing.py`, que imprime un
mensaje legible en `stderr` y sale con código 1. Nunca un traceback en
pantalla.

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
4. **Entrada y salida válidas y distintas**: se comprueba en el
   constructor de `Maze`, no en el generador.

---

## 6. Pipeline

```
Config validada
  → Maze vacío (todos los muros cerrados)
  → estampar "42"      ¿no cabe? → pattern_skipped = True, sigue
  → validar entry/exit/esquinas contra las celdas bloqueadas
  → árbol de expansión sobre las celdas libres
  → si PERFECT=False: braiding (bucles y callejones) + ensure_open
  → validator (siempre, también en producción)
  → solver BFS → maze.set_solution(...)
  → writer + renderer
```

Dos detalles de orden que importan. La regla del 3x3 solo se vigila
**dentro** del braiding, consultando `would_open_3x3` antes de cada
apertura extra, porque el árbol de expansión no puede crear áreas
abiertas (ADR-003). Y el generador no imprime nada: expone
`pattern_skipped` y es `a_maze_ing.py` quien saca el aviso por
`stderr`. Una librería que imprime es una librería que molesta en el
proyecto que la reutilice.

El validador comprueba conectividad total de las celdas libres, bordes
exteriores cerrados, ausencia de bloques 3x3 abiertos, número de
callejones y número de bucles independientes (`E - V + C`). Cuesta
microsegundos y avisa antes que el peer-evaluator.

---

## 7. Fichero de configuración

```
# Comentarios con almohadilla; una pareja KEY=VALUE por línea
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=False
# opcionales
SEED=42
ALGORITHM=backtracker     # backtracker | kruskal
PATTERN=42                # vacío para no dibujar nada
```

---

## 8. Reparto

**Vía A, motor:** `maze.py`, `pattern.py`, `algorithms/`, `solver.py`,
`braiding.py`, `validator.py`, `generator.py`.
**Vía B, aplicación y entrega:** `config_parser.py`, `writer.py`,
`renderer.py`, `menu.py`, empaquetado, licencia, README.

Innegociable: `maze.py` y `braiding.py` se repasan juntos línea a
línea, sean de quien sean. Son las dos partes que garantizan preguntas
en la defensa.

Flujo git: `main`, ramas de feature, PR con revisión obligatoria del
otro antes de hacer merge. La revisión no es burocracia: es lo que
asegura que los dos sabemos explicar el código ajeno.

Con `tests/fixtures.py` ya escrito, la vía B puede arrancar sin esperar
al motor: `toy_maze()` devuelve un 5x5 resuelto, con su hexadecimal
(`d5553 / 95556 / c5553 / 95556 / c5557`) y su camino de 24
movimientos.

---

## 9. Pendiente de cerrar

Cuando una de estas se decida, se añade como ADR nueva en
`DECISIONS.md` y se borra de aquí.

- [ ] **Licencia**: MIT frente a Apache-2.0. MIT es lo razonable aquí:
      permite explícitamente la reutilización que pide el subject.
- [ ] **Fuente gruesa para el bonus `--max-dead-ends 0`**. Los glifos
      actuales dejan 3 callejones inevitables (ADR-007). Antes de
      decidir hay que abrir `maze_analyzer.py` y ver si descuenta los
      callejones adyacentes al patrón.
- [ ] **Clave `PATTERN`** como tercera opcional del fichero de
      configuración, en lugar de la `DISPLAY` que se barajaba. El modo
      de display se cambia desde el menú en caliente; el patrón sí
      necesita clave, porque condiciona el tamaño mínimo.
- [ ] **Confirmar ADR-008** (layout plano en lugar de `src/`).

---

## 10. Riesgos conocidos

- El braiding puede entrar en conflicto con la regla del 3x3 en
  laberintos pequeños: en algunos tamaños no se llegará a cero
  callejones. El bonus es un ideal, no un requisito.
- La wheel tiene que estar commiteada en la raíz del repo aunque sea un
  binario. Va contra la costumbre, pero el subject lo pide.
- El empaquetado es lo único del proyecto que no cubre ningún módulo
  del cursus: contar 2 o 3 horas de aprendizaje, no 30 minutos.

---
