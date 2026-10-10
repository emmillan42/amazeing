# Decisiones de diseño

Registro de decisiones arquitectónicas (ADR) de A-Maze-ing.

**Regla de este fichero: solo se añade al final.** Una decisión escrita
no se reescribe ni se borra nunca, ni cuando se demuestra equivocada:
si cambia, se añade una ADR nueva que la sustituye y se marca la
antigua como *Sustituida por ADR-XXX*. Lo único que se actualiza de una
ADR ya escrita es su línea de **Estado**, anotando la fecha del
cambio. Un fichero al que solo se añade
no se desincroniza jamás, y el histórico es justo lo que se pregunta en
la defensa.

Lo que **no** va aquí: decisiones aún abiertas. Esas viven en la
sección "Pendiente de cerrar" de `ARCHITECTURE.md`, que sí se
reescribe entera. Una decisión entra aquí el día que se cierra.

Estados: `Aceptada`, `Propuesta` (falta que la confirme la pareja),
`Sustituida por ADR-XXX`.

---

## ADR-001 — Los muros se guardan como aristas compartidas

**Fecha:** 2026-09-23 · **Estado:** Aceptada

**Contexto.** El subject exige que cada muro compartido esté codificado
igual por las dos celdas vecinas, y avisa de que es lo primero que
revisa el analizador. Es la fuente de fallos número uno del proyecto.

**Decisión.** Cada muro se guarda una sola vez, como arista:

```
v_walls[y][x]   muro vertical al oeste de (x, y),  x en 0..W
h_walls[y][x]   muro horizontal al norte de (x, y), y en 0..H
```

El muro norte de `(x, y)` y el sur de `(x, y-1)` son el mismo booleano.
El código hexadecimal se calcula solo al exportar, nunca se almacena.

**Alternativas descartadas.** Guardar 4 bits por celda, como el fichero
de salida. Es más directo de exportar, pero obliga a mantener la
coherencia a mano en cada operación: cada apertura son dos escrituras
que hay que acordarse de hacer, y un solo olvido rompe el fichero.

**Consecuencias.** La coherencia es estructural, no se valida: es
imposible violarla. El borde exterior son las columnas 0 y W de
`v_walls` y las filas 0 y H de `h_walls`, así que también es
estructural. A cambio hay un desfase de índice que hay que tener
presente al leer el código: el muro este de `(x, y)` es
`v_walls[y][x+1]`, no `[x]`.

---

## ADR-002 — El "42" se estampa antes de generar

**Fecha:** 2026-09-23 · **Estado:** Aceptada

**Contexto.** El laberinto debe mostrar un "42" dibujado con celdas
totalmente cerradas, que son la única excepción permitida a la regla
de "sin celdas aisladas".

**Decisión.** Orden fijo: estampar el patrón, marcar esas celdas como
bloqueadas, y generar el laberinto únicamente sobre las celdas libres.
El algoritmo nunca ve las celdas del patrón.

**Alternativas descartadas.** Generar primero y estampar después.
Rompe la conectividad (el patrón puede cortar el único camino hacia una
zona) y deja obsoleto el camino más corto ya calculado.

**Consecuencias.** Las celdas del patrón acaban con valor `f` de forma
natural, sin ningún paso extra. La entrada y la salida deben validarse
contra las celdas bloqueadas antes de generar. `Maze.open_wall` lanza
excepción si alguna de las dos celdas está bloqueada, así que ningún
bug posterior puede estropear el dibujo.

---

## ADR-003 — Los dos modos son el mismo algoritmo más un post-proceso

**Fecha:** 2026-09-23 · **Estado:** Aceptada

**Contexto.** El subject pide dos modos muy distintos: `PERFECT=True`
con un único camino, y `PERFECT=False` con bucles, esquinas y centro
abiertos y pocos callejones.

**Decisión.** `PERFECT=True` es un árbol de expansión sobre las celdas
libres. `PERFECT=False` es ese mismo árbol más un braiding que abre
muros para crear bucles y matar callejones, validando en cada apertura
que no se forme un bloque 3x3 abierto.

**Alternativas descartadas.** Dos algoritmos independientes. Duplica el
código que hay que defender y duplica las formas de incumplir la regla
del 3x3.

**Consecuencias.** Un árbol de expansión no tiene ciclos, así que no
puede crear ningún área abierta: la regla del 3x3 solo hay que
vigilarla dentro del braiding, nunca como pasada de limpieza al final.
El bonus de cero callejones sale del mismo bucle llevado al límite. Y
el modo perfecto queda funcionando mucho antes que el otro, es decir,
hay algo entregable si el tiempo aprieta.

---

## ADR-004 — El centro es la celda libre más cercana al centro geométrico

**Fecha:** 2026-09-28 · **Estado:** Aceptada

**Contexto.** En modo Pac-Man el centro debe ser un pasillo abierto,
porque ahí empieza el jugador, pero el "42" se dibuja centrado. Los dos
requisitos compiten por la misma celda.

**Decisión.** "Centro" se define como la celda libre más cercana al
centro geométrico, con desempate determinista por fila y columna.
Implementado en `Maze.centre()` sobre `Maze.nearest_free()`.

**Alternativas descartadas.** Desplazar el patrón para dejar libre el
centro exacto. Funciona para un tamaño concreto y hay que recalcularlo
para cada rejilla; además descoloca visualmente el "42".

**Consecuencias.** Vale para cualquier tamaño sin casos especiales. En
20x15 el centro cae en (9, 7), que es la columna de separación entre el
4 y el 2: un pasillo de paso, no un bolsillo. La definición es una
consulta sobre el laberinto, no un parámetro, así que no hay nada que
configurar ni que documentar en el fichero de configuración.

---

## ADR-005 — Render ASCII con colores ANSI, no MiniLibX

**Fecha:** 2026-09-23 · **Estado:** Aceptada

**Contexto.** El subject permite elegir entre render en terminal o una
ventana gráfica con MiniLibX.

**Decisión.** Render ASCII con caracteres de caja y secuencias de
escape ANSI para el color.

**Alternativas descartadas.** MiniLibX. Usarla desde Python exige
escribir bindings con `ctypes` y un servidor X funcionando; son días de
trabajo para un requisito que el subject da por cumplido con la
terminal.

**Consecuencias.** Cero dependencias: funciona en cualquier máquina del
campus y en cualquier terminal del evaluador. El cambio de color es una
lista de paletas y un índice. El render queda en `app/`, fuera del
paquete reutilizable, así que la decisión no compromete al proyecto que
reutilice `mazegen`.

---

## ADR-006 — `random.Random(seed)` como instancia, nunca el `random` global

**Fecha:** 2026-09-23 · **Estado:** Aceptada

**Contexto.** El subject exige generación aleatoria pero reproducible
mediante semilla.

**Decisión.** El generador crea su propia instancia
`random.Random(seed)` y la pasa a los algoritmos y al braiding como
parámetro.

**Alternativas descartadas.** `random.seed()` sobre el módulo global.
Es estado compartido de proceso: cualquier otra librería que llame a
`random` altera nuestra secuencia, y dos generadores en el mismo
programa se pisan.

**Consecuencias.** Reproducibilidad garantizada y tests deterministas.
El `rng` aparece en la firma de `Algorithm.carve` y de las funciones de
`braiding`, lo que hace explícito qué partes son aleatorias.

---

## ADR-007 — Glifos del "42" en 3x5 y tamaño mínimo 9x7

**Fecha:** 2026-09-28 · **Estado:** Aceptada

**Contexto.** Había que fijar la forma exacta del patrón antes de nada,
porque determina el tamaño mínimo del laberinto y la cuenta de
callejones del modo jugable.

**Decisión.** Bitmap de 3x5 por dígito, trazo de 1 celda, 1 columna de
separación. Bloque de 7x5. Margen de 1 celda libre entre el patrón y el
borde, de donde sale el mínimo de 9x7.

```
#.# ###
#.# ..#
### ###
..# #..
..# ###
```

**Alternativas descartadas.** Fuente de trazo grueso (2 celdas), con
contadores de 2 de ancho. Elimina los callejones forzados, porque cada
celda del hueco tendría grado 2, pero lleva el bloque a 13x10 y el
mínimo a 15x12, lo que deja fuera tamaños de laberinto razonables.

**Consecuencias.** El margen de 1 celda no es estético: garantiza que
las celdas restantes formen un anillo conexo y que cada hueco interior
del glifo desemboque en él. Por debajo de 9x7 el patrón se omite y se
avisa por `stderr`, como permite el subject. Y los huecos de 1 celda de
ancho producen **exactamente 3 callejones que ningún braiding puede
eliminar** (en 20x15 son (7,6), (11,6) y (11,8)): encaja con lo que
tolera el subject, pero deja en el aire el bonus `--max-dead-ends 0`.
Esa parte sigue abierta, ver `ARCHITECTURE.md`.

---

## ADR-008 — El paquete vive en la raíz, no en `src/`

**Fecha:** 2026-09-28 · **Estado:** Aceptada (confirmada 2026-09-29)

**Contexto.** El plan inicial situaba el paquete reutilizable en
`src/mazegen/`, que es el layout recomendado hoy para paquetes de
Python.

**Decisión.** `mazegen/` en la raíz del repositorio, junto a `app/` y
`a_maze_ing.py`.

**Alternativas descartadas.** `src/mazegen/` más `pip install -e .` en
el target `install` del Makefile. Con ese layout, un
`python3 a_maze_ing.py config.txt` sobre un repo recién clonado falla
con `ModuleNotFoundError` mientras no se instale el paquete, y el
subject define esa línea como *la* forma de ejecutar el programa: no
podemos depender de que el evaluador haga `make install` primero.

**Consecuencias.** El programa arranca sin instalar nada, que es lo que
comprueba el apartado *Standard usage* de la hoja de evaluación. El
wheel sale idéntico, solo cambia la configuración de `pyproject.toml`.
La frontera entre lo reutilizable y lo que no lo es la sigue marcando
el límite del paquete, que es el argumento que hay que defender, no la
carpeta `src`. Revertirlo son dos pasos: mover la carpeta y añadir
`pip install -e .` al Makefile.

Contrapartida que hay que conocer: ejecutando desde la raíz del repo,
`import mazegen` encuentra primero la carpeta local, nunca el paquete
instalado. La hoja de evaluación pide instalar el wheel en un virtualenv
distinto y probarlo con `a_maze_ing.py`; para que esa prueba demuestre
algo hay que hacerla **fuera del repositorio**, copiando `a_maze_ing.py`
y el fichero de configuración a otra carpeta. Va documentado en el
README y es un paso del ensayo de defensa.

---

## ADR-009 — El fichero de salida guarda el primer laberinto

**Fecha:** 2026-09-28 · **Estado:** Aceptada

**Contexto.** La hoja de evaluación dice, literalmente, que hay que
verificar que *el primer laberinto generado y mostrado* está también
guardado en el fichero de salida, y que la secuencia del camino más
corto del fichero coincide con la representación visual. El menú, en
cambio, permite regenerar tantas veces como se quiera.

**Decisión.** El fichero de salida se escribe una sola vez, justo
después de la primera generación. Regenerar desde el menú **no** lo
reescribe. Se añade una entrada de menú explícita para guardar el
laberinto que está en pantalla, que cuenta como interacción extra de
las que el subject permite.

**Alternativas descartadas.** Reescribir el fichero en cada
regeneración. Parece lo natural, pero deja el fichero apuntando al
último laberinto: si el evaluador regenera dos veces y después abre el
fichero para compararlo con lo que vio al arrancar, no coincide, y ese
apartado de la hoja se marca como fallado.

**Consecuencias.** El fichero y la primera pantalla siempre concuerdan.
El evaluador puede además guardar cualquier laberinto posterior si
quiere validarlo con el script de análisis, sin que eso rompa la
garantía anterior. `Menu._regenerate` no toca disco; `Menu._save` sí.

---

## ADR-010 — Licencia MIT

**Fecha:** 2026-09-29 · **Estado:** Aceptada

**Contexto.** El subject exige un `LICENSE.md` propio en la raíz, con
una licencia que permita explícitamente la reutilización y la
distribución del generador por los proyectos posteriores que se apoyen
en él. Elegirla forma parte del ejercicio.

**Decisión.** MIT.

**Alternativas descartadas.** Apache-2.0 añade una concesión expresa de
patentes y obligaciones de notificación de cambios: pensada para
proyectos corporativos, aquí solo añade texto que habría que saber
defender. BSD-3-Clause es prácticamente equivalente a MIT con una
cláusula extra sobre el uso del nombre, sin ninguna ventaja para este
caso. Las licencias copyleft (GPL) quedan descartadas de raíz: obligan
al proyecto que reutilice `mazegen` a adoptar la misma licencia, que es
justo lo contrario de lo que pide el subject.

**Consecuencias.** Cuatro párrafos de texto, permisiva, universalmente
reconocida, y la más fácil de justificar en la defensa: permite reusar,
modificar y redistribuir con la única condición de conservar el aviso
de copyright. El año y los dos nombres van en el fichero.

---

## ADR-011 — Se mantiene la fuente 3x5: el bonus es alcanzable con ella

**Fecha:** 2026-09-29 · **Estado:** Aceptada · Cierra el punto abierto
de ADR-007

**Contexto.** ADR-007 dejó en el aire si los 3 callejones que los
huecos del "4" y del "2" producen inevitablemente impedían el bonus
`--max-dead-ends 0`, y si por tanto había que pasar a una fuente de
trazo grueso con contadores de 2 celdas.

**Decisión.** Se mantiene la fuente 3x5. No hace falta fuente gruesa.

**Justificación medida.** El analizador oficial clasifica los
callejones en dos grupos: *real* cuando alguno de sus muros cerrados
podría abrirse hacia una celda normal, y *enclosed* cuando todos dan a
una celda totalmente cerrada del "42" o al borde exterior. La opción
`--max-dead-ends` solo limita los reales. Los 3 callejones de nuestros
glifos tienen un único vecino no bloqueado, el mismo por el que
conectan, así que caen siempre en la categoría tolerada.

Comprobado con un prototipo desechable (árbol de expansión más braiding
ingenuo) y el analizador oficial, en 9x7, 11x9, 15x11, 20x15, 30x20 y
41x25: en los seis, `0 real + 3 enclosed by the '42' (tolerated)` y
veredicto *bonus-grade (perfectly braided)*.

**Consecuencias.** El mínimo se queda en 9x7 en lugar de irse a 15x12.
El braiding solo persigue callejones **reales**: intentar abrir los del
patrón rompería el dibujo, así que `braiding.dead_ends()` los excluye
por construcción. `validator.count_dead_ends()` devuelve la misma
pareja `(real, enclosed)` que el analizador, para poder comparar
resultados sin traducir nada.

---

## ADR-012 — Clave `PATTERN` en el fichero de configuración, no `DISPLAY`

**Fecha:** 2026-09-29 · **Estado:** Aceptada

**Contexto.** El subject permite añadir claves opcionales. `SEED` y
`ALGORITHM` estaban claras; faltaba decidir la tercera, que se barajaba
como `DISPLAY`.

**Decisión.** La tercera clave opcional es `PATTERN`, con valor `42`
por defecto y vacío para no dibujar nada. `DISPLAY` se descarta.

**Alternativas descartadas.** `DISPLAY` seleccionaría el modo de
representación, pero tras ADR-005 solo existe uno: sería una clave con
un único valor válido, es decir, ruido que hay que documentar, parsear
y defender sin que aporte nada. El modo de visualización que sí varía,
el color, se cambia en caliente desde el menú y no necesita fichero.

**Consecuencias.** `PATTERN` cuesta tres líneas en el parser y hace
demostrable en la defensa que `pattern.py` es genérico: los glifos
viven en un diccionario y el texto es un parámetro. Permite además
probar laberintos por debajo de 9x7 sin tocar código. Un carácter sin
glifo es un `ConfigError` explícito, no un "no cabe" silencioso: si
alguien escribe `PATTERN=7`, el programa lo dice en lugar de generar un
laberinto sin dibujo.

---

## ADR-013 — Herramientas en `.venv` con versiones fijadas; lint configurado en `.flake8` y `mypy.ini`

**Fecha:** 2026-10-10 · **Estado:** Propuesta (falta que Lucas confirme
el punto que afecta a `pyproject.toml`)

**Contexto.** El subject exige que `make lint` ejecute literalmente
`flake8 .` y `mypy .` con unos flags concretos, recomienda un entorno
virtual, y la hoja de evaluación pide reconstruir el paquete desde las
fuentes. El programa, en cambio, solo usa la biblioteca estándar.

**Decisión.** Las herramientas de desarrollo (`flake8`, `mypy`,
`build`, `pytest`) viven en `.venv`, instaladas por `make install`
desde `requirements-dev.txt` con versiones exactas. `run` y `debug`
usan el `python3` del sistema, sin venv. Las exclusiones de lint van en
ficheros propios de cada herramienta, `.flake8` y `mypy.ini`. `make
test` llama a `python -m pytest`, no a `pytest`.

**Medido antes de decidir.** Con un `.venv` dentro del repo, `flake8 .`
analizó todo lo instalado y devolvió 62.473 avisos: flake8 no excluye
los entornos virtuales por defecto. `mypy .` sí se salta `.venv`,
porque ignora las carpetas ocultas, pero no `venv/` ni `build/`, y tras
construir el wheel `build/lib/mazegen/` es una segunda copia del
paquete que para la comprobación con un error de módulo duplicado.
`pytest` a secas no encuentra `mazegen` porque no pone la raíz del repo
en `sys.path`; `python -m pytest` sí.

**Alternativas descartadas.**
- *Exclusiones como flags en el Makefile.* El comando tiene que ser
  `flake8 .` tal cual, y un evaluador que lo lance a mano no pasaría
  por el Makefile.
- *Configuración en `pyproject.toml`.* flake8 no lee ese fichero, y el
  `pyproject.toml` es de B6.
- *Configuración en `setup.cfg`.* Para mypy es el fichero de menor
  prioridad: una sección `[tool.mypy]` añadida más tarde lo anularía
  sin avisar.
- *Versiones sin fijar.* Un cambio de versión de flake8 o mypy puede
  cambiar el veredicto, y el de la máquina del evaluador es el que
  cuenta.
- *`run` desde el venv.* Haría depender la ejecución de `make install`,
  justo lo que ADR-008 quiere evitar.

**Consecuencias.** `make lint` da el mismo resultado en cualquier
máquina, y sobre un clon recién hecho crea el venv él solo, porque
depende del fichero marcador `.venv/.installed`. mypy lee `mypy.ini`
antes que `pyproject.toml`, así que **el `pyproject.toml` no debe
llevar sección `[tool.mypy]`**: se ignoraría sin aviso. `make install`
necesita red y el módulo `venv` (paquete `python3-venv` en Debian y
Ubuntu). `make clean` borra `build/` y `dist/` pero nunca el wheel de
la raíz, y el `.gitignore` lo re-incluye con `!/mazegen-*.whl`, que
gana incluso a un `.gitignore` global (probado). `maze_analyzer.py`
queda en el `.gitignore` por ser código de la intra; pasa el lint, así
que subirlo para B9 no rompe nada.

---

## ADR-014 — `config.txt` solo con comentarios de línea completa; opcionales comentadas

**Fecha:** 2026-10-10 · **Estado:** Propuesta (falta que Lucas confirme
que su parser lo acepta tal cual)

**Contexto.** El `config.txt` por defecto es un entregable y lo primero
que ejecuta el evaluador. El ejemplo de `ARCHITECTURE.md` §7 tenía
comentarios al final de línea (`ALGORITHM=backtracker  # ...`), y el
subject solo define como comentario las líneas que empiezan por `#`.

**Decisión.** El fichero por defecto usa solo comentarios de línea
completa y claves en mayúsculas, como la tabla del subject. Valores
obligatorios: 20x15, `ENTRY=0,0`, `EXIT=19,14`, `OUTPUT_FILE=maze.txt`,
`PERFECT=False`. Las tres claves opcionales van comentadas: `SEED=42`
como ejemplo, y `ALGORITHM` y `PATTERN` con su valor por defecto.

**Alternativas descartadas.**
- *Comentarios al final de línea.* Si el parser no los recorta, el
  valor leído incluye el comentario, el fichero por defecto da un
  `ConfigError` y la nota es un 0. El fichero tiene que funcionar con
  la lectura más estricta del subject, sea cual sea la de B1.
- *`SEED=42` activa.* Cada ejecución daría el mismo laberinto, y la
  primera impresión del evaluador sería que no es aleatorio. Comentada,
  la reproducibilidad se prueba quitando una almohadilla, sin tocar
  ningún otro fichero, que es lo que pide la hoja.
- *`PERFECT=True` por defecto.* Funcionaría antes, sin esperar al
  braiding, pero el subject presenta el modo jugable como el exigido
  por defecto.

**Consecuencias.** El fichero por defecto no depende de cómo trate B1
los comentarios en línea; esa decisión sigue siendo suya.
Descomentar `ALGORITHM` o `PATTERN` tal cual no cambia el resultado.
Hasta que exista el braiding (A6), la configuración por defecto no se
puede ejecutar de punta a punta: durante el desarrollo se usa una
copia local con `PERFECT=True`.

---

## ADR-015 — `shortest_path` lanza `MazeError` si no hay camino; desempate N, E, S, O

**Fecha:** 2026-10-10 · **Estado:** Aceptada

**Contexto.** El contrato fijaba la firma
`shortest_path(maze, start, goal) -> list[Cell]`, pero no qué ocurre
cuando la meta es inalcanzable, ni cuál de varios caminos igual de
cortos se devuelve. En modo jugable hay bucles, así que suele haber
varios.

**Decisión.** BFS con `deque` y un diccionario `parent` que sirve a la
vez de conjunto de visitadas y de enlaces para reconstruir el camino.
La búsqueda para en cuanto descubre la meta. Devuelve las celdas con
`start` y `goal` incluidas, y `[start]` si son la misma celda. Lanza
`MazeError` si una de las dos está fuera de la rejilla o bloqueada, o
si no hay camino. Los vecinos se recorren en el orden del enum
`Direction` (N, E, S, O), de modo que el desempate es determinista y
el solver no recibe `rng`.

**Alternativas descartadas.**
- *Devolver `[]`.* No es ambiguo, porque `[start]` cubre el caso
  `start == goal`, pero es silencioso: `solution_string()` daría una
  cadena vacía, el writer escribiría una línea de camino vacía y nadie
  lo notaría hasta comparar el fichero con la pantalla.
- *Una subclase nueva, `NoPathError`.* Obligaría a tocar `errors.py`,
  que es contrato compartido, sin que nadie necesite distinguir este
  error de los demás.
- *DFS.* Encuentra un camino, que solo coincide con el más corto en
  modo perfecto.
- *A\*.* También óptimo, pero más código que defender para una rejilla
  sin pesos y pequeña.
- *Guardar caminos completos en la cola.* Memoria cuadrática, frente a
  un diccionario lineal.

**Consecuencias.** En el pipeline el validador corre antes y ya
garantiza la conectividad, así que el error de "sin camino" es una red
de seguridad: si salta, es un bug, y `a_maze_ing.py` lo convierte en
mensaje claro y código 1 en vez de en un fichero incorrecto. Misma
semilla da mismo fichero, línea del camino incluida. Quien reutilice
`mazegen` debe capturar `MazeError`, lo que va documentado en el
README. Como el analizador no comprueba la línea del camino,
`tests/test_solver.py` compara el resultado con un oráculo de fuerza
bruta en 200 laberintos aleatorios con bucles; cambiar `popleft()` por
`pop()`, es decir, convertir el BFS en un DFS, hace fallar 8 de ellos.
