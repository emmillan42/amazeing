# A-Maze-ing — Arquitectura y contrato

Documento vivo. Se **reescribe entero** cuando algo cambia, y la
versión nueva sustituye a la anterior en los documentos del proyecto.
Describe cómo está montado el proyecto ahora mismo.

El *porqué* de cada decisión no está aquí: está en `DECISIONS.md`, en
formato ADR y en orden cronológico. Aquí solo se cita el número.

Última actualización: 29 sep 2026 · Fase 0 cerrada · revisado contra la
hoja de evaluación y contra el analizador oficial · sin decisiones
abiertas.

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
El pipeline completo se ha validado con un prototipo desechable y el
analizador oficial: ver ADR-011.

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
| 008 | Paquete en la raíz, no en `src/` |
| 009 | El fichero de salida guarda el primer laberinto |
| 010 | Licencia MIT |
| 011 | Se mantiene la fuente 3x5: el bonus es alcanzable con ella |
| 012 | Clave `PATTERN`, no `DISPLAY` |

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
│   ├── maze.py            Maze, Direction, validate_geometry [hecho]
│   ├── pattern.py         glifos, tamaño mínimo, estampado   [hecho]
│   ├── solver.py          BFS → camino más corto             [stub]
│   ├── braiding.py        bucles, callejones, regla 3x3      [stub]
│   ├── validator.py       invariantes                        [stub]
│   ├── generator.py       MazeGenerator, pipeline            [parcial]
│   └── algorithms/
│       ├── __init__.py    registro y get_algorithm()
│       ├── base.py        Algorithm(ABC)
│       ├── backtracker.py DFS iterativo                      [stub]
│       └── kruskal.py     bonus, union-find                  [stub]
│
├── app/                   ← NO reutilizable
│   ├── config_parser.py   KEY=VALUE → Config                 [stub]
│   ├── writer.py          fichero de salida                  [stub]
│   ├── renderer.py        ASCII + ANSI                       [stub]
│   └── menu.py            bucle interactivo                  [stub]
│
└── tests/
    └── fixtures.py        laberinto 5x5 a mano               [hecho]
```

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
braiding.dead_ends(maze) -> list[Cell]        # solo los reales
validator.validate(maze, *, perfect) -> None
validator.count_dead_ends(maze) -> tuple[int, int]   # (real, enclosed)
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
  → Maze vacío (todos los muros cerrados)
  → estampar "42"      ¿no cabe? → pattern_skipped = True, sigue
  → validar entry/exit/esquinas contra las celdas bloqueadas
  → árbol de expansión sobre las celdas libres
  → si PERFECT=False: braiding (bucles y callejones) + ensure_open
  → validator (siempre, también en producción)
  → solver BFS → maze.set_solution(...)
  → writer (una sola vez, ADR-009) + renderer
```

Dos detalles de orden que importan. La regla del 3x3 solo se vigila
**dentro** del braiding, consultando `would_open_3x3` antes de cada
apertura extra, porque el árbol de expansión no puede crear áreas
abiertas (ADR-003). Y el generador no imprime nada: expone
`pattern_skipped` y es `a_maze_ing.py` quien saca el aviso por
`stderr`. Una librería que imprime es una librería que molesta en el
proyecto que la reutilice.

El validador comprueba conectividad total de las celdas libres, bordes
exteriores cerrados, ausencia de bloques 3x3 abiertos, callejones
reales y número de bucles independientes (`E - V + C`). Cuesta
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

**Las claves son insensibles a mayúsculas**: la hoja de evaluación dice
explícitamente que `width=20` es tan válido como `WIDTH=20`. Los
valores booleanos también (`true`, `True`, `TRUE`). El nombre del
fichero de salida y el del algoritmo se respetan tal cual. Un carácter
sin glifo en `PATTERN` es un `ConfigError` explícito (ADR-012).

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

Además, `SEED` tiene que poder fijarse desde aquí: el evaluador
comprueba la reproducibilidad editando el fichero de configuración, y
la hoja dice que no debería tener que tocar ningún otro fichero.

---

## 8. Cómo se evalúa

Repaso de la hoja de evaluación contra lo que tenemos. Todo lo que
aparece antes de los bonus es eliminatorio: cualquier elemento que
falte pone la nota a 0.

| Apartado de la hoja | Dónde se cubre | Estado |
|---|---|---|
| Ficheros presentes: `README.md`, `a_maze_ing.py`, `mazegen-*.whl`, fichero de configuración, fuentes para reconstruir el paquete | raíz del repo | 3 de 5 pendientes |
| Norm (`flake8`) y `mypy` sobre los ficheros Python | todo el árbol | pasa, también `--strict` |
| README con sus 11 elementos obligatorios | `README.md` | pendiente, ver 8.1 |
| Laberinto aleatorio mostrado al arrancar con la config por defecto | `a_maze_ing.py` + `renderer.py` | falta `renderer` y `config.txt` |
| Menú: regenerar, mostrar/ocultar camino, cambiar color de muros | `menu.py` | firmas listas |
| Formato del fichero de configuración, claves en minúscula incluidas | `config_parser.py` | firmas listas, ver 7 |
| Gestión de los cinco errores de configuración | `config_parser.py` | firmas listas, ver 7 |
| Fichero de salida: `HEIGHT` líneas, línea vacía, entry, exit, camino | `writer.py` + ADR-009 | firmas listas |
| El camino del fichero coincide con el de la pantalla | ambos leen `maze.solution` | estructural |
| Coherencia de muros validada con el analizador | ADR-001 | estructural, medido |
| Todas las celdas alcanzables salvo el "42" | `validator.is_connected` | stub |
| Muros en todo el contorno | invariante 2 | estructural |
| Sin zonas abiertas de 3x3, y saber explicar cómo se verifica | `braiding.would_open_3x3` + `validator.open_areas_3x3` | stub |
| "42" presente, o mensaje en terminal si no cabe | `pattern.py` + aviso en `a_maze_ing.py` | hecho |
| Laberinto perfecto si `PERFECT=True` | `validator.count_loops == 0` | stub |
| Mismo laberinto con la misma semilla | ADR-006 + clave `SEED` | hecho en el motor |
| Parámetros inconsistentes (entry/exit fuera, tamaño negativo) | `validate_geometry` en el constructor | hecho |
| Reconstruir el paquete en un virtualenv e instalarlo en otro | `pyproject.toml` + README | pendiente, ver ADR-008 |

### 8.1 Elementos obligatorios del README

Los once. Que falte uno solo es un 0, así que se revisan en la fase
final con la hoja delante:

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

---

## 9. Reparto

**Vía A, motor** — Emmanuel: `maze.py`, `pattern.py`, `algorithms/`,
`solver.py`, `braiding.py`, `validator.py`, `generator.py`.

**Vía B, aplicación y entrega** — Lucas: `config_parser.py`,
`writer.py`, `renderer.py`, `menu.py`, empaquetado, licencia, README.

Innegociable: `maze.py` y `braiding.py` se repasan juntos
línea a línea, sean de quien sean.

Flujo git: `main`, ramas de feature, PR con revisión obligatoria del
otro antes de hacer merge.

Con `tests/fixtures.py` ya escrito, la vía B puede arrancar sin esperar
al motor: `toy_maze()` devuelve un 5x5 resuelto, con su hexadecimal
(`d5553 / 95556 / c5553 / 95556 / c5557`) y su camino de 24
movimientos.

---

## 10. Pendiente de cerrar

Ninguna decisión abierta. Las cinco que había se cerraron el 29 sep:
licencia (ADR-010), fuente del patrón (ADR-011), clave `PATTERN`
(ADR-012), confirmación del layout plano (ADR-008) y reparto (sección
9).

Cuando aparezca una nueva se anota aquí, y al decidirse se mueve a
`DECISIONS.md` como ADR.

---

## 11. Riesgos conocidos

- **El `.gitignore` puede tragarse el wheel.** Casi todas las
  plantillas de `.gitignore` para Python excluyen `dist/`, `build/` y
  `*.whl`, y el subject exige el wheel commiteado en la raíz. Hay que
  añadir la excepción y comprobar con `git status` que el fichero se
  está subiendo de verdad.
- **Probar el wheel fuera del repositorio.** Con el layout plano,
  ejecutar desde la raíz importa siempre la carpeta local, nunca el
  paquete instalado. La prueba de instalación que pide la hoja solo
  demuestra algo si se hace en otra carpeta, copiando `a_maze_ing.py` y
  el fichero de configuración (ADR-008).
- El braiding puede entrar en conflicto con la regla del 3x3 en
  laberintos pequeños. Medido hasta ahora: sin problemas desde 9x7 con
  un braiding ingenuo, pero el prototipo no es el código final.
- El empaquetado es lo único del proyecto que no cubre ningún módulo
  del cursus: contar 2 o 3 horas de aprendizaje, no 30 minutos.
- Los bonus solo cuentan si **todo** lo anterior está correcto. No
  tiene sentido tocar Kruskal mientras falte un elemento del README.

---
