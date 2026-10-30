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

---

## ADR-016 — El backtracker es un DFS iterativo con pila explícita

**Fecha:** 2026-10-28 · **Estado:** Aceptada

**Contexto.** A3. El backtracker es el algoritmo por defecto: tiene que
producir un árbol de expansión sobre las celdas libres, ser
reproducible con la semilla, no tocar las celdas del patrón y funcionar
para cualquier tamaño que acepte `MazeGenerator`.

**Decisión.** Búsqueda en profundidad iterativa con una lista como
pila. La celda actual se consulta con `stack[-1]`, sin sacarla, y solo
sale de la pila cuando ya no le quedan vecinos sin visitar. El conjunto
`visited` se inicializa con las celdas bloqueadas, de modo que el
patrón queda fuera sin ninguna condición aparte. La celda de inicio se
elige con `rng.choice` entre las celdas libres, en orden de filas. Los
vecinos se recorren en el orden del enum `Direction` y `rng.choice`
elige entre pares `(dirección, celda)`.

**Medido antes de decidir.** La profundidad máxima de la pila es la
longitud del pasillo más largo que abre el DFS: 175 en 20x15, 672 en
40x30 y 4.023 en 100x100. El límite de recursión por defecto de Python
es 1.000.

**Alternativas descartadas.**
- *Versión recursiva.* Es la forma clásica de escribirlo, pero lanza
  `RecursionError` en cuanto el pasillo más largo supera las 1.000
  celdas, y eso ocurre en tamaños razonables. Subir el límite con
  `sys.setrecursionlimit` cambia el `RecursionError` por el riesgo de
  desbordar la pila de C del intérprete, que es peor.
- *`stack.pop()` en cada iteración.* Abandona la celda aunque le
  queden vecinos sin visitar y deja zonas sin conectar. Comprobado: los
  tests lo detectan.
- *Empezar siempre en la entrada.* Acopla el algoritmo a un concepto
  que su contrato no menciona: `Algorithm` habla de "las celdas
  libres". La corrección no depende del punto de inicio.
- *Filtrar las bloqueadas con una condición propia.* Misma garantía con
  dos condiciones en lugar de una, y `open_wall` las rechazaría de
  todos modos (invariante 3).

**Consecuencias.** El resultado es un árbol por construcción: cada
apertura se hace hacia una celda no visitada, así que añade exactamente
una celda al árbol y no puede cerrar un ciclo. Eso da V celdas libres
unidas por V − 1 aristas, todas conectadas, que es lo que comprueba
`tests/test_backtracker.py` con su propio recorrido. La terminación
depende de `visited`: sin él, el bucle no acaba nunca (comprobado). El
coste es lineal en el número de celdas. Misma semilla, mismo
laberinto, y el `random` global queda intacto (ADR-006, con test).
Cambiar el inicio por una celda fija no rompe ningún test, y es lo
esperado: cambia qué laberinto sale, no si es correcto.

---

## ADR-017 — El validador no reutiliza el código que valida; un 3x3 abierto son 12 muros interiores abiertos

**Fecha:** 2026-10-28 · **Estado:** Aceptada

**Contexto.** A5a. El validador corre sobre cada laberinto generado,
también en producción, y hacía falta decidir dos cosas: de dónde sale
cada medida y qué es exactamente un "área abierta de 3x3". El subject
solo dice que se permiten áreas de 2x3 y 3x2, pero nunca de 3x3.

**Decisión.** Cada chequeo usa código propio. La conectividad se mide
con un BFS del propio módulo (`_reachable`) que parte de la entrada,
igual que el analizador, y no con el solver. La regla del 3x3 se
comprueba sobre la rejilla final, no con `braiding.would_open_3x3`.

Un bloque de 3x3 es abierto cuando están abiertos sus **12 muros
interiores**: 6 verticales (2 por fila en 3 filas) y 6 horizontales (3
por fila en 2 huecos). Sus muros exteriores no cuentan.

`validate` comprueba en este orden: borde cerrado, conectividad, 3x3.
Cada fallo lanza `GenerationError` con la cuenta y la primera celda
afectada; por eso la lógica de conectividad vive en `_unreachable`,
que devuelve la lista, y `is_connected` es solo su versión booleana.
Los chequeos por modo, bucles y callejones, son A5b; hasta entonces el
parámetro `perfect` no se usa.

**Alternativas descartadas.**
- *Reutilizar el solver o `would_open_3x3`.* Si el validador comparte
  código con lo que valida, un bug en ese código pasa los dos filtros a
  la vez y se tapa solo. Es el mismo motivo por el que
  `tests/test_solver.py` usa un oráculo independiente. Además,
  `shortest_path` responde si hay camino entre dos celdas, no si se
  alcanzan todas.
- *"Nueve celdas conectadas" como definición de área abierta.* Un 3x3
  recorrido en serpiente tiene sus 9 celdas conectadas con 8 aristas y
  es un pasillo normal. Ese criterio marcaría como prohibidos
  laberintos válidos.
- *Omitir `borders_closed` porque el borde es estructural (invariante
  2).* Cuesta 2(W+H) lecturas, es defensa en profundidad y la hoja de
  evaluación pide saber explicar cómo se verifica.

**Consecuencias.** La definición da el argumento de ADR-003 en una
línea: un árbol sobre 9 celdas tiene como mucho 8 aristas y un 3x3
abierto necesita 12, así que el árbol de expansión no puede contener
ninguno. Los tests cierran uno a uno los 12 muros para comprobar que
cada uno cuenta. El coste medido es de unos 2 ms en 20x15 y 128 ms en
100x100: despreciable, pero no "microsegundos", como decía
`ARCHITECTURE.md`. `_reachable` servirá en A5b para contar las
componentes C de `E − V + C`. Mientras A5b no exista, que un laberinto
perfecto no tenga bucles lo garantiza la construcción (ADR-016) y lo
comprueba `tests/test_analyzer.py`, no `validate`.

---

## ADR-018 — Comprobación con el analizador antes de B5: helpers provisionales en `tests/`

**Fecha:** 2026-10-28 · **Estado:** Aceptada

**Contexto.** La sincronización S1 pasa por el writer de Lucas (B5),
pero el motor ya genera laberintos perfectos y conviene pasarlos por el
analizador oficial cuanto antes. `maze_analyzer.py` está en el
`.gitignore` (ADR-013), así que no siempre existe en el repo.

**Decisión.** `tests/test_analyzer.py` importa el analizador con
`pytest.importorskip`: si no hay copia local en la raíz, el módulo se
salta con un aviso en lugar de fallar. Escribe cada laberinto con un
formateador propio de 8 líneas y comprueba coherencia, conectividad,
cero bucles y veredicto `PERFECT` en 40 laberintos, de 3x3 a 41x25.
Para probarlo a mano, `tests/dump_maze.py` vuelca un laberinto en el
formato del subject (`python3 -m tests.dump_maze 20 15 42`). Los
módulos de `tests/` no se importan entre sí.

**Medido antes de decidir.** Con `test_analyzer.py` importando el
formateador desde `tests.dump_maze`, `mypy .` se detiene con *Source
file found twice under different module names*, porque `tests/` no es
un paquete.

**Alternativas descartadas.**
- *Añadir `tests/__init__.py`.* Arregla mypy, pero cambia cómo pytest
  nombra e importa los módulos de test, y puede romper los imports de
  `test_solver.py`. No compensa por 8 líneas.
- *Lanzar `dump_maze` como subproceso desde el test.* Sin import, pero
  40 procesos de Python por ejecución.
- *Esperar a B5.* Pierde justo lo que S1 quiere: detectar pronto un
  fallo de contrato.

**Consecuencias.** Hay 8 líneas duplicadas entre los dos ficheros, y
las dos copias tienen fecha de caducidad. En S1, `test_analyzer.py`
pasa a escribir con `app.writer.write_maze`, porque eso es lo que S1
comprueba de verdad. `dump_maze.py` se retira cuando
`python3 a_maze_ing.py` funcione con `PERFECT=True` (S2). Si B9
necesita helpers compartidos entre tests, el sitio natural es
`tests/conftest.py`, que pytest carga sin que nadie lo importe.

---

## ADR-019 — Chequeos por modo: `E − V + C` sobre las celdas libres y umbrales del analizador como suelo

**Fecha:** 2026-10-30 · **Estado:** Aceptada

**Contexto.** A5b. `validate` tenía que distinguir los dos modos: cero
bucles con `PERFECT=True`, y un tablero jugable con `PERFECT=False`.
Las dos medidas, bucles y callejones, tenían que dar exactamente el
número que da el analizador oficial, para poder comparar sin traducir
nada (ADR-011). Quedaba por decidir con qué fórmula, sobre qué grafo y
con qué umbrales.

**Decisión.**

- `count_loops` es `E − V + C` sobre el grafo de celdas libres: muros
  abiertos entre dos celdas libres, contados una vez mirando solo al
  este y al sur; celdas libres; componentes conexas, contadas con el
  `_reachable` de A5a.
- `count_dead_ends` devuelve `(real, enclosed)` sobre las celdas libres
  de grado 1. Un callejón es *enclosed* cuando todos sus muros cerrados
  dan al borde o a una celda bloqueada, y se mira el conjunto
  `maze.blocked`, no el código `f` de la celda.
- `validate` corre siempre primero los chequeos comunes. Después, en
  modo perfecto exige cero bucles; en modo jugable, al menos
  `MIN_LOOPS = 2` bucles y como mucho `MAX_REAL_DEAD_ENDS = 2`
  callejones reales. Son los valores por defecto del analizador, como
  constantes del módulo.

**Medido antes de decidir.** 400 comparaciones contra el analizador
(5 tamaños de 3x3 a 41x25, 10 semillas, abriendo 5 muros al azar entre
medida y medida para recorrer muchos números de bucles): 0
discrepancias en bucles y en callejones. En 20x15 con semilla 42 da
`0` bucles y `(28, 3)`, lo mismo que el analizador en A5a. Solo hay
discrepancia en laberintos **no conexos**, y ahí la nuestra es la
correcta: dos cuadrados abiertos de 2x2 separados dan 2 bucles con
`E − V + C` y 1 en el analizador, que solo mira la región de la
entrada; un callejón junto a una celda libre aislada es real para
nosotros y *enclosed* para él, que toma por "42" toda celda cerrada por
sus cuatro lados. `validate` rechaza un laberinto no conexo antes de
contar nada, así que en producción las dos medidas coinciden siempre.

**Alternativas descartadas.**
- *`E − V + 1`, como el analizador.* Da −1 en el caso de los dos
  cuadrados. Solo vale con una componente, y `count_loops` es una
  función pública que los tests usan sobre laberintos hechos a mano.
- *Contar las celdas bloqueadas como vértices.* Sorprendentemente, no
  cambia el resultado: cada celda bloqueada suma 1 a V y 1 a C. Se
  excluyen igualmente, porque el grafo que interesa es el de las
  celdas libres, y así el filtro de aristas tiene sentido.
- *Código `f` para reconocer el patrón.* Es lo que puede hacer el
  analizador, que solo lee un fichero. El `Maze` sabe qué celdas son
  del patrón; usar un indicio teniendo el dato es peor.
- *Umbral de 0 callejones en el validador.* Es el bonus, no el
  requisito. Un validador que exige el bonus convierte en error fatal
  un braiding que deja un callejón real en una rejilla difícil. El
  validador es el suelo del subject; el objetivo de 0 vive en
  `braid(..., max_dead_ends=0)`.
- *Umbrales como parámetros de `validate`.* Cambia una firma del
  contrato para algo que nadie necesita variar hoy.
- *Chequeo propio de esquinas y centro.* Redundante: son celdas libres
  (el generador lo impone), y los chequeos comunes ya probaron que toda
  celda libre es alcanzable.

**Consecuencias.** El modo perfecto queda verificado por `validate` en
cada generación: conexo más cero bucles es exactamente un árbol de
expansión, ya no descansa solo en la construcción ni en
`tests/test_analyzer.py`. `tests/test_analyzer.py` compara las dos
medidas con el analizador en 320 puntos: 40 laberintos a los que se
van abriendo muros al azar. El filtro de
aristas hacia celdas bloqueadas solo es alcanzable escribiendo el
almacenamiento a mano, igual que el borde roto de A5a, y tiene su test.
Para A6 quedan dos datos: el analizador cuenta como real un callejón
aunque abrirlo crease un 3x3, así que el braiding no puede descartar
candidatos sin buscar alternativa; y, con la conectividad garantizada,
toda celda libre tiene ya al menos un lado abierto, de modo que
`ensure_open`, tal como está documentado, no haría nada.

---

## ADR-020 — Errores del generador: parámetros en el constructor, stubs como `GenerationError`, fallos internos reproducibles

**Fecha:** 2026-10-30 · **Estado:** Aceptada

**Contexto.** A7a. Con A5b el modo perfecto queda cerrado, pero el
pipeline seguía teniendo tres salidas feas. Una entrada sobre el "42"
solo se detectaba al generar, aunque el resto de parámetros se
rechazan en el constructor. `PERFECT=False`, que es la configuración
por defecto (ADR-014), y `ALGORITHM=kruskal` llegaban a un
`NotImplementedError`, que no es `MazeError`: traceback en pantalla, un
0 en la hoja. Y un fallo del validador, que siempre es un bug nuestro,
se presentaba al usuario como si fuera culpa suya y sin forma de
reproducirlo.

**Decisión.**

- El constructor estampa el patrón en un laberinto en blanco y
  comprueba entrada, salida y, en modo jugable, esquinas. El estampado
  es determinista, así que el resultado es el de cualquier `generate`.
- `_carve` y `_braid` convierten un `NotImplementedError` en
  `GenerationError` con un mensaje que dice qué falta y, para el modo
  jugable, qué usar mientras tanto.
- `_validate` envuelve el error del validador como *internal error,
  please report it* y añade todo lo que reconstruye ese laberinto:
  tamaño, algoritmo, modo, patrón, semilla y número de llamada a
  `generate()`, porque cada llamada consume el mismo `rng`.
- El error de tamaño pasa a decir *invalid maze size 1x15: each side
  must be at least 3*. Antes empezaba por *maze too small*, igual que
  el aviso, no fatal, de que el "42" no cabe.

**Alternativas descartadas.**
- *Un `except Exception` en `a_maze_ing.py`.* Es la red de último
  recurso que muchos ponen, pero se traga los bugs sin decir de dónde
  vienen, y es el fichero de B2. Aquí cada error que sabemos que puede
  salir tiene su mensaje propio.
- *Quitar Kruskal del registro hasta A8.* Daría un `ConfigError` en el
  constructor, más temprano todavía, pero es otro fichero, y A8 tendría
  que acordarse de volver a registrarlo. El guardia de `_carve` vale
  para cualquier algoritmo futuro a medias.
- *Comprobar entrada y salida en `generate`, como antes.* Correcto,
  pero tardío: un uso de la librería con un parámetro imposible
  construía el generador sin quejarse.
- *Que el generador elija su propia semilla cuando no se le da.* Haría
  reproducible cualquier fallo, también sin `SEED`, pero cambia el
  significado de la propiedad `seed` del contrato. Queda abierto en
  `ARCHITECTURE.md`.

**Consecuencias.** Ningún camino del generador termina en traceback:
todo lo que sale de `MazeGenerator` es `MazeError`, que es lo único que
captura `a_maze_ing.py`. `pattern_skipped` y `pattern_cells` se conocen
desde el constructor. `tests/test_generator.py` prueba los stubs con
`monkeypatch`, de modo que sus tests no cambian de significado cuando
llegue A6. En A7b hay que decidir si el guardia de `_braid` se queda:
con el braiding hecho es código muerto. Sin semilla, la receta de
reproducción del mensaje queda incompleta, y el mensaje lo dice
(`seed=unset`).

---

## ADR-021 — Braiding: un callejón atascado se fuerza abriendo y cerrando; esquinas y centro no son callejones reales; `braid` garantiza los bucles

**Fecha:** 2026-10-30 · **Estado:** Aceptada · Cierra los dos puntos
abiertos de ADR-019

**Contexto.** A6, antes de escribir código. ADR-019 dejó dos preguntas:
qué hace el braiding cuando todas las salidas posibles de un callejón
crearían un 3x3, porque el analizador lo sigue contando como real, y
qué significa `ensure_open`, porque con la conectividad garantizada
toda celda libre ya tiene un lado abierto. Al medir apareció una
tercera: nadie garantizaba los `MIN_LOOPS = 2` bucles que exige el
validador.

**Geometría del atasco.** En un 3x3 abierto, cada celda tiene abiertos
todos sus muros interiores: 2 en las esquinas del bloque, 3 en los
laterales, 4 en el centro. Un callejón pasa de grado 1 a grado 2 al
abrirlo, así que solo puede completar un bloque del que sea esquina, y
ese bloque tiene que tener ya abiertos sus otros 11 muros. Un árbol
tiene como mucho 8 aristas dentro de un 3x3 (ADR-017): hacen falta al
menos 3 aperturas del braiding en el mismo bloque. Las esquinas del
laberinto, que no tienen "fuera", son el caso típico.

**Decisión.**

- *Callejón atascado.* Se abre igualmente y, en el bloque que completa,
  se cierra un muro interior cuyas dos celdas tienen grado ≥ 3. No
  desconecta, porque todo muro interior de un 3x3 abierto está en un
  ciclo de 2x2; no crea callejones, porque las dos celdas se quedan con
  grado ≥ 2; y siempre existe, porque los 4 radios del centro del bloque
  cumplen. Balance +1 −1 aristas: los bucles no cambian.
- *`ensure_open`.* Significa "las esquinas y el centro no son callejones
  **reales**". Reales y no "grado ≥ 2", porque una celda clave encerrada
  por el patrón no tiene arreglo y no debe lanzar nada. Usa el mismo
  arreglo por celda que `braid`.
- *Bucles.* Los garantiza `braid`, cuya docstring de módulo ya decía que
  su trabajo es crear bucles y quitar callejones. Partiendo de un árbol,
  cada apertura normal suma exactamente un bucle a `E − V + C` y cada
  apertura forzada suma cero, así que los bucles se cuentan sin medir.
  Si faltan, se abren muros al azar que respeten el 3x3. El umbral se
  importa de `validator.MIN_LOOPS`: una sola fuente de verdad.

**Medido antes de decidir.** Sobre una reconstrucción de los módulos
(el backtracker reproduce el 20x15 de semilla 42 de ADR-019), con 11.530
laberintos por tipo de árbol, de 3x3 a 15x15. Además del backtracker se
usó un árbol tipo Kruskal, porque `braid` recibe "un laberinto
tallado" y A8 traerá árboles con más hojas.

- Atascos con un braiding que solo abre: 0 con el backtracker; 25 con
  Kruskal, 22 de ellos en 3x3 (el 11 % de esas rejillas). Siempre
  dejan exactamente 1 callejón real.
- Con la apertura forzada: 0 callejones reales en los 23.060, todos
  pasan `validate`, y 2.060 pasados por el analizador con
  `--max-dead-ends 0` dan *bonus-grade*, de 3x3 a 41x25.
- Bucles: sin la garantía, 60 laberintos del backtracker (3x4 el 10 %,
  4x3, 4x4, 4x5, 4x6, 5x4, 3x6, 6x3, 8x3) y 5 de Kruskal acaban con un
  solo bucle: un pasillo en serpiente cuyos extremos se unen. Sería un
  *internal error*.
- Celdas clave: con `braid(..., 0)` ninguna esquina ni el centro queda
  como callejón. Con `max_dead_ends=2`, una de ellas sí en el 20 % de los
  9x7, 18 % de los 15x11, 9,5 % de los 20x15 y 3 % de los 30x20.

**Alternativas descartadas.**
- *Rendirse ante el atasco.* El validador lo tolera, pero el bonus sería
  falso en 1 de cada 9 rejillas 3x3 con Kruskal.
- *Reintentar con otro orden.* Sin garantía de terminar bien y con un
  número arbitrario de intentos.
- *Procesar primero las esquinas.* Baja la probabilidad, no la anula.
- *Cerrar un muro cualquiera del bloque.* Puede desconectar o crear un
  callejón.
- *`ensure_open` como "un lado abierto".* Siempre cierto: un test que no
  puede fallar.
- *Eliminar `ensure_open`.* `max_dead_ends` está en el contrato, y la
  garantía que pide el subject no debe depender de ese parámetro.
- *Los bucles en `ensure_open`, o midiendo con `count_loops`.* Lo
  primero mezcla responsabilidades con un nombre que no lo dice; lo
  segundo haría que `braid` y el validador compartieran la medida, que
  es lo que ADR-017 evita.

**Consecuencias.** ADR-003 se matiza sin sustituirse: el braiding puede
cerrar un muro, pero solo dentro del 3x3 que acaba de completar y nunca
con pérdida neta. En producción `ensure_open` no hace nada, y un test lo
demuestra. De paso apareció un problema fuera de A6, medido solo en la
reconstrucción: con `PATTERN=4`, el bloque de 3 de ancho pone el trazo
del glifo en la columna central, y el analizador encuentra bloqueadas
todas sus celdas "centro" en 4 de 5 tamaños. Queda en `ARCHITECTURE.md`
§10 para verificarlo en el repo.

---

## ADR-022 — Implementación del braiding: consultas puras, una sola lista de callejones contada por aritmética

**Fecha:** 2026-10-30 · **Estado:** Aceptada

**Contexto.** A6. Con ADR-021 cerrada quedaba cómo escribir las cuatro
funciones para que fueran correctas, baratas y defendibles.

**Decisión.**

- `would_open_3x3` es una consulta pura: no abre nada, trata el muro
  candidato como abierto mientras mira los bloques. Cada muro se
  escribe desde su celda oeste o norte, para compararlos con `==`.
  Solo mira los bloques que contienen las dos celdas del muro: empiezan
  en la menor coordenada o antes y acaban en la mayor o después, que
  son 2 × 3 = 6 como mucho. El borde y las celdas del patrón no
  necesitan caso propio: ningún bloque contiene un muro del borde, y un
  bloque con una celda bloqueada siempre conserva uno de sus muros
  cerrados. Una celda fuera de la rejilla lanza `MazeError`, porque
  `neighbour` respondería sobre otra celda sin avisar.
- `dead_ends` devuelve solo los reales, fila a fila. No filtra las
  bloqueadas: tienen grado 0. No reutiliza nada del validador; los
  tests usan cada uno como oráculo del otro.
- `braid` calcula la lista de callejones una sola vez, la baraja y lleva
  la cuenta restando 1, o 2 si el vecino también era callejón. Es
  posible porque nunca aparece un callejón nuevo: abrir solo añade
  salidas, y la apertura forzada solo cierra muros entre celdas de grado
  ≥ 3.
- Al elegir lado se prefiere un vecino que también sea callejón: un
  muro arregla dos.
- La apertura forzada completa **exactamente un** bloque: es el que
  contiene la única salida del callejón y el muro que se abre. Lo
  destapó una mutación que sobrevivía (quitar la recomprobación de los
  demás bloques no rompía ningún test); se quitó ese código.
- Si `_break_block` no encuentra muro que cerrar lanza `GenerationError`,
  no `AssertionError`: un `assert` se puede desactivar y, si salta, es
  un traceback.

**Medido.** En 100x100, recontar los callejones tras cada apertura,
como hacía el prototipo, cuesta 52 s; la versión final, 130 ms (5 ms en
20x15). La preferencia por vecinos callejón baja los atascos con
Kruskal de 68 a 25. Con todo dentro, 11.650 tableros del pipeline real
(`perfect=False`, de 3x3 a 15x15 más 20x15, 30x20, 41x25 y 60x40) y
otros 11.650 sobre árboles tipo Kruskal: 0 callejones reales y todos
pasan `validate`. 865 por el analizador con `--max-dead-ends 0`: todos
*bonus-grade*. En 100x100 el pipeline jugable tarda 876 ms frente a 355
del perfecto; la parte mayor es el validador (236 ms).

**Alternativas descartadas.**
- *Abrir, mirar y restaurar.* Usaba `_set_wall`, que es privado, y si
  el muro ya estaba abierto el `finally` lo cerraba: una consulta que
  modifica el laberinto.
- *Recontar con `dead_ends` tras cada apertura.* Cuadrático: los 52 s
  de arriba.
- *Reutilizar `validator._area_is_open`.* Un bug compartido pasaría los
  dos filtros a la vez (ADR-017).

**Consecuencias.** `tests/test_braiding.py` tiene 133 tests: los 12 muros
del 3x3 uno a uno, los 66 pares, el validador como oráculo sobre 1.740
muros (304 positivos), el atasco hecho a mano, árboles tipo Kruskal con
un espía que exige que se llegue a la apertura forzada, y la
contabilidad de bucles comparada con `count_loops`. De 9 mutaciones
deliberadas, las 8 que son bugs las detecta algún test; la novena era
el código sobrante. Todo verificado sobre la reconstrucción: falta
repetirlo en el repo.

---

## ADR-023 — Los fallos del braiding son errores internos reproducibles; el generador no se fía del recuento de `braid`

**Fecha:** 2026-10-30 · **Estado:** Aceptada · Cierra el punto de A7b
de ADR-020

**Contexto.** A7b. Con A6 hecha, el guardia de `_braid` que traducía
`NotImplementedError` a *the playable mode is not implemented yet* ya
no puede saltar. Y `braid` puede lanzar, aunque ADR-021 demuestre que
no ocurre, un `GenerationError` sin la receta de reproducción que
`_validate` añade.

**Decisión.**

- Fuera el guardia de `NotImplementedError` de `_braid`. El de `_carve`
  se queda: Kruskal sigue siendo stub hasta A8.
- `_braid` envuelve cualquier `MazeError` de `braid` o `ensure_open`
  igual que `_validate`: *internal error, please report it*, con tamaño,
  algoritmo, modo, patrón, semilla y número de llamada. El mensaje se
  construye en un único método, `_internal_error`, que usan los dos.
- El valor que devuelve `braid` se ignora a propósito: el validador
  mide el tablero con su propio código justo después, y un paso no
  califica su propio trabajo.
- El mensaje de `_break_block` deja de empezar por *internal error*,
  que ya lo añade el generador.

**Alternativas descartadas.**
- *Mantener el guardia.* Código muerto, como anticipaba ADR-020.
- *Usar el recuento de `braid` para fallar antes.* Duplica al validador
  y se fía de la palabra del paso que se comprueba.
- *Capturar solo `GenerationError`.* Un `MazeError` de `open_wall` dentro
  del braiding también es un bug nuestro.

**Consecuencias.** Con la configuración por defecto el motor genera ya
tableros de bonus; el programa completo sigue esperando a B3 y B5. El
test de `tests/test_generator.py` que simulaba el stub del braiding con
`monkeypatch` queda obsoleto y hay que quitarlo: ahora un
`NotImplementedError` del braiding no se traduce. Lo sustituye
`tests/test_generator_playable.py`, con 6 tests: la configuración por
defecto da `(0, 3)` en 20x15, tamaños pequeños sin callejones, un fallo
de `braid` o de `ensure_open` sale como error interno con la semilla, un
`braid` que no hace nada y devuelve 0 lo caza el validador, y el modo
perfecto nunca llama al braiding.
