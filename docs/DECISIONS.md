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

**Fecha:** 2026-09-28 · **Estado:** Aceptada (ADR-025 la completa para
textos con un número impar de glifos)

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

**Fecha:** 2026-09-28 · **Estado:** Aceptada (confirmada 2026-09-29;
ADR-028 completa la prueba fuera del repo, 2026-10-31)

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

**Fecha:** 2026-10-10 · **Estado:** Aceptada (confirmada 2026-10-30: el
`pyproject.toml` de B6 no lleva `[tool.mypy]`, ADR-024)

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

**Fecha:** 2026-10-10 · **Estado:** Aceptada (confirmada 2026-10-30: el
parser de B1 solo admite comentarios de línea completa, ADR-024)

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

**Contexto.** La sincronización S1 pasa por el writer de vía B (B5),
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

**Fecha:** 2026-10-30 · **Estado:** Aceptada (ADR-027 retira la parte de
los stubs, 2026-10-31)

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

---

## ADR-024 — Vía B: se integran los ficheros de la vía B; el parser solo comprueba sintaxis y tipos

**Fecha:** 2026-10-30 · **Estado:** Aceptada; el parser comprueba además el límite superior de tamaño desde ADR-030 (2026-10-31)

**Contexto.** Con la vía A verificada en el repo, `make lint` solo
fallaba en `app/`, porque se estaba tranbajando con los stubs del
punto de partida:firmas, docstrings y `raise NotImplementedError`.

**Medido antes de decidir**, ejecutando los ficheros de vía B con solo
los imports añadidos:
- `renderer.py` recorría `range(height - 1)` y `range(width - 1)`: en
  5x4 dibujaba 3 filas y 4 columnas, y la salida, en la esquina
  opuesta, no aparecía nunca.
- `writer.py` escribía `(0, 0)` en vez de `0,0`, sin línea vacía ni
  `\n` final; el analizador lo rechazaba en la línea 5.
- `config_parser.py` no importaba `ConfigError`, distinguía mayúsculas
  (`width=20` daba "falta WIDTH") y dejaba escapar `FileNotFoundError`,
  un traceback; además imprimía su diccionario en cada arranque.
- `menu.py` exponía `run_menu(maze, generator)`, que no encajaba con
  `Menu(generator, config).run()` de `a_maze_ing.py`, y no tenía la
  entrada de guardar de ADR-009.
- Todos con finales de línea CRLF, código comentado y sin docstrings.

**Decisión.** Se adaptan los ficheros conservando su diseño: la
rejilla de celdas de 3 caracteres, sus paletas, el flujo del menú y la
conversión de `OSError` en `MazeError` del writer.

- *Parser.* Solo sintaxis y tipos: la geometría la valida
  `MazeGenerator`, para que cada regla viva en un sitio y con un único
  mensaje. Claves a mayúsculas al leerlas. Clave desconocida o repetida
  es un `ConfigError` con número de línea. `SEED` o `ALGORITHM` vacíos
  toman su valor por defecto; `PATTERN` vacío no dibuja nada (ADR-012).
  `OSError` y `UnicodeDecodeError` se convierten en `ConfigError`.
- *Writer.* El texto completo se construye antes de abrir el fichero,
  con `newline="\n"`; `format_maze` queda aparte para probar el formato
  sin disco.
- *Renderer.* Cada borde se dibuja desde los muros reales, incluidos el
  este y el sur del contorno. Las paletas pasan de diccionarios a un
  `dataclass` congelado, `Palette`: una clave mal escrita la ve `mypy`,
  no el evaluador. El "42" lleva color propio.
- *Menú.* La lógica de vía B dentro de la clase del contrato: regenerar
  sin tocar disco, camino, color, guardar y salir. Un fallo al guardar
  se muestra en el menú, no cierra el programa. Textos en inglés, como
  los errores del motor.
- *Entry point.* El aviso de "no cabe" usa `config.pattern`, no la
  constante.
- *Empaquetado.* `license = "MIT"` con `license-files`, porque la forma
  de tabla está obsoleta y `setuptools` anuncia su retirada en 2027.
- `.gitattributes` fija LF en todo el repo, para que los ficheros de los
  dos no choquen en los diffs.

**Alternativas descartadas.**
- *Sustituir por los stubs.* El programa dejaría de funcionar.
- *Arreglar solo los imports.* El lint pasaría, pero la salida seguiría
  sin dibujarse y el analizador seguiría rechazando el fichero.
- *Mantener las comprobaciones de geometría en el parser.* Duplicaban
  `validate_geometry` con otro mínimo (1 en lugar de 3) y otros
  mensajes.
- *Submenú de paletas.* Se pasa a la siguiente: una pulsación, y es lo
  que pide la hoja.

**Verificado.** En la reconstrucción: los cinco errores de la hoja y
ocho más (fichero inexistente, sin argumentos, clave mal escrita o
repetida, directorio de salida inexistente, tamaño negativo, entrada
fuera, algoritmo desconocido) dan mensaje claro y código 1; el programa
completo escribe un fichero que el analizador da por *bonus-grade*; 48
tests nuevos, y cada uno de los cuatro fallos de vía B reintroducido lo
detecta alguno; el wheel se construye sin avisos y se instala y usa
fuera del repo. En el repo real: `make lint` y `make lint-strict` sobre
30 ficheros y `make test` con 580 tests, todo en verde. `PATTERN=7` da
`no glyph for character '7', available: 2, 4` y código 1.

**Consecuencias.** La autoría se escribe tal cual en el README. S1 se cierra:
`tests/test_analyzer.py` escribe con `app.writer.write_maze`, y
`tests/dump_maze.py` se retira (ADR-018). ADR-013 y ADR-014 quedan
confirmadas. Se borra `app/test.txt` y se corrigen los logins de
`LICENSE.md` y `pyproject.toml`. Queda de B6 construir el wheel en el
repo, dejarlo en la raíz y añadir su target al `Makefile`.

---

## ADR-025 — El patrón se coloca con una columna libre sobre la columna central; con un número impar de glifos, el ancho mínimo pasa a 4n + 4

**Fecha:** 2026-10-30 · **Estado:** Aceptada · Implementada el 2026-10-31
(A9, ADR-026) · Completa ADR-007

**Contexto.** Medido en el repo real con `PATTERN=4`: el analizador
busca el centro en (4, 3) en 9x7 y en (9, 7) y (10, 7) en 20x15, y las
tres celdas están bloqueadas. El veredicto es *Not Pac-Man-ready*
aunque el braiding deje 0 callejones. Además, el centro de ADR-004 cae
en un hueco del glifo: el jugador empezaría encerrado. Con el "42" no
pasa, por eso §8.2 lo daba por bueno.

**Causa.** El bloque mide `4n − 1` columnas, con `n` glifos, y se
centra. Con `n` par, la columna central de la rejilla es una columna de
separación entre glifos, siempre libre. Con `n` impar, es la columna
del medio de un glifo, y la fila central del glifo suele estar llena
(en el "4", `###`).

**Decisión.** El bloque se coloca de forma que una columna libre, de
separación o la de junto a un glifo único, coincida con la columna
`(W − 1) // 2`. Con `n` par es exactamente la colocación actual: el
"42" queda idéntico bit a bit y todas las medidas anteriores siguen
valiendo. Con `n` impar el bloque se desplaza 2 columnas respecto al
centrado, hacia el lado que tenga sitio.

Por qué esa columna resuelve las dos cosas: ADR-004 usa la columna
`(W − 1) // 2`, y el analizador mira `W // 2` con `W` impar o
`W / 2 − 1` y `W / 2` con `W` par, que incluyen esa misma columna. Al
estar libre la columna entera, la fila deja de importar.

**Medido.** Por fuerza bruta para 1 a 5 glifos y anchos hasta 80: con
`n` par la colocación centrada actual siempre cumple; con `n` impar el
desplazamiento es siempre de 2, y el ancho mínimo pasa de `4n + 1` a
`4n + 4` (el "4", de 5 a 8). Por encima del mínimo, todo ancho cabe.
El alto no cambia.

**Alternativas descartadas.**
- *Desplazar 1 columna.* La columna central caería en un borde del
  glifo, bloqueado en la fila central.
- *Desplazar en vertical.* Ninguna fila de los glifos está entera libre.
- *Rechazar en el parser los textos de longitud impar.* Castiga una
  opción que funciona en modo perfecto.
- *Documentarlo como limitación.* El README debe describir el fichero de
  configuración completo, y un evaluador podría probar `PATTERN=4`.

**Consecuencias.** Con `n` impar el dibujo queda descentrado 2
columnas. `minimum_grid` y `fits` deben dar el nuevo mínimo, para que
el aviso de "no cabe" sea cierto. Tests pendientes: para textos de 1 a
3 glifos y todos los tamaños desde el mínimo, la columna central está
libre; y el analizador da *usable* con `PATTERN=4` en 9x7 y 20x15.

---

## ADR-026 — Implementación de ADR-025: la posición del patrón se busca, no se calcula

**Fecha:** 2026-10-31 · **Estado:** Aceptada

**Contexto.** A9. ADR-025 fijó qué tiene que cumplir la colocación del
patrón; quedaba cómo escribirla en `pattern.py` sin mover el "42" ni un
bit.

**Decisión.**

- `_origin` recorre las posiciones horizontales en las que el bloque
  conserva su margen, se queda con las que dejan libre la columna
  `(W − 1) // 2` (porque cae fuera del bloque o sobre una columna sin
  `#`) y elige la más cercana a la centrada. El desplazamiento de 2 y el
  mínimo `4n + 4` de ADR-025 salen de la regla; los tests los comprueban
  en lugar de darlos por hechos.
- Un empate se resuelve hacia el este. Es el lado que recibe la columna
  sobrante cuando el hueco libre es impar, así que en el ancho mínimo es
  el único que cabe; preferirlo siempre evita que el dibujo cambie de
  lado según el ancho.
- La fila no se busca: es la centrada. Ninguna fila de los glifos está
  entera libre (ADR-025).
- `minimum_grid` busca el ancho hacia arriba desde el bloque más su
  margen. El bucle termina siempre: con unas dos veces el ancho del
  bloque, este cabe entero al este de la columna central.
- `_block` compone los glifos en un único sitio, y de ahí leen el
  tamaño, las columnas libres y las celdas. Un texto vacío pasa a ser un
  `ConfigError`; antes era un `ValueError` de `max()`, un traceback. Solo
  es alcanzable usando `mazegen` como librería: el parser convierte
  `PATTERN` vacío en "sin dibujo" (ADR-024).

**Alternativas descartadas.**
- *Fórmula por paridad* (con `n` impar, desplazar 2 y sumar 3 al
  mínimo). Solo vale para glifos de 3 de ancho con la columna central
  llena: guarda la medida de ADR-025 en vez de la regla.
- *Empate hacia el oeste.* Igual de correcto, pero el dibujo saltaría de
  lado entre el ancho mínimo y los demás.

**Medido.** En la reconstrucción: 11.596 colocaciones de textos pares,
el "42" incluido, idénticas a las del código anterior; para textos
impares de 1 a 5 glifos, mínimo `4n + 4`, monótono hasta 80 de ancho y
desplazamiento siempre +2; 1.566 tableros jugables con textos impares,
todos *bonus-grade*. En el repo real, con `PATTERN=4`: *bonus-grade* y
centro alcanzable en 9x7 (7 bucles, `0 + 1`) y en 20x15 (29 bucles,
`0 + 1`), con las mismas cifras que la reconstrucción. El centro de
ADR-004 pasa a ser el geométrico exacto, (4, 3) y (9, 7); antes, en 9x7,
caía en (4, 2), dentro del hueco del 4. En 7x7 el programa avisa de que
el 4 *needs at least 8x7*: el entry point toma el mínimo de
`minimum_grid` y el aviso es cierto también con textos impares.

**Consecuencias.** `tests/test_pattern.py`, 84 tests: mínimos, monotonía,
columna central libre y margen para los 14 textos de 1 a 3 glifos,
centro geométrico, textos pares idénticos a la colocación anterior
(reescrita dentro del test), desplazamiento +2 y los dibujos de 9x7 y
8x7. `tests/test_pattern_playable.py`, 8 tests: el analizador da *usable*
con `PATTERN=4` en 9x7 y 20x15, y con `2` y `424`. Con el `pattern.py`
anterior fallan 44; tres mutaciones (empate al oeste, ignorar las
columnas libres, fila redondeada hacia arriba) las detecta alguno. Nace
`tests/conftest.py` con las fixtures `analyzer` y `judge`, que escriben
con el writer real y preguntan al analizador; el analizador se registra
en `sys.modules` antes de ejecutarlo, porque su `@dataclass` se busca
ahí. Con `n` impar el dibujo queda 2 columnas al este del centro.

---

## ADR-027 — Kruskal: union-find sobre un `dict` por celda, unión por tamaño y `find` iterativo; `_carve` informa sus fallos como error interno

**Fecha:** 2026-10-31 · **Estado:** Aceptada · Retira la parte de los
stubs de ADR-020 · Cierra la medida pendiente de ADR-021

**Contexto.** A8. El capítulo VIII del subject cita como bonus *Support
multiple maze generation algorithms*. Había que elegir la estructura de
union-find, el recorrido de los muros, y qué hacer con el guardia de
`_carve` que traducía el stub de Kruskal a `GenerationError`.

**Decisión.**

- `_DisjointSets`, privado en `kruskal.py`: un `dict[Cell, Cell]` de
  padres y un `dict[Cell, int]` de tamaños, solo con las celdas libres.
  `union` devuelve si ha unido, de modo que comprobar y unir es una sola
  llamada y `carve` se lee "si une, abre": nunca se abre un muro entre
  dos celdas ya conectadas, así que el resultado es un árbol.
- Unión por tamaño y *path halving*. `find` es un bucle, no una
  recursión.
- Los muros se toman desde su celda oeste o norte, mirando al este y al
  sur, en el orden de filas de `Maze.cells()`, y se barajan con el `rng`
  recibido (ADR-006).
- En `generator._carve`, fuera la traducción de `NotImplementedError`:
  ya no queda ningún stub, y un test sobre todo el registro lo garantiza.
  En su lugar, un `MazeError` del algoritmo pasa por `_internal_error`,
  igual que en `_braid` y `_validate`. Solo `MazeError`, como en ADR-023.

**Medido antes de decidir**, en 100x100 con el "42": `dict` 20 ms,
lista plana 11 ms, reetiquetado del conjunto menor 19 ms; construir la
lista de muros cuesta 21 ms y el pipeline perfecto entero 355 ms. Un
union-find ingenuo forma árboles de 523 niveles en 100x100 y de 1.899 en
200x200; con unión por tamaño, la profundidad máxima es 8. Tallar con
Kruskal cuesta 55 ms, frente a 73 del backtracker. Y antes del cambio,
un algoritmo con un bug salía del generador como `MazeError: cannot open
the outer border at (0, 0)`, sin tamaño ni semilla.

**Alternativas descartadas.**
- *Lista plana indexada por `y·W + x`.* Ahorra 9 ms que no se notan, a
  cambio de una aritmética de índices que puede mezclar dos celdas en
  silencio y de otro vocabulario que el resto del motor. Con el `dict`,
  una celda bloqueada no existe en la estructura: un bug da `KeyError`.
- *Reetiquetar el conjunto menor.* Mismo coste, más estado (etiquetas y
  listas de miembros), y no es un union-find.
- *`find` recursivo.* Sin unión por tamaño daría `RecursionError`, el
  riesgo que ADR-016 evita en el backtracker. Con ella no pasaría, pero
  la seguridad dependería de dos cosas en vez de una.
- *Parar al llegar a V − 1 aperturas.* Un contador más para ahorrar
  poco.
- *Mantener el guardia de `NotImplementedError`.* Código muerto, como
  en ADR-023.
- *Quitar el guardia sin más.* Un bug del algoritmo seguiría saliendo
  sin la receta para reproducirlo.
- *Capturar `Exception` en `_carve`.* Escondería errores de programación
  de cualquier tipo bajo un mensaje genérico.

**Medido con Kruskal real.** En la reconstrucción, 11.830 tableros
jugables de 3x3 a 15x15 con 70 semillas: la apertura forzada se usa en
12, 10 de ellos en 3x3 (el 14 % de esas rejillas), y con el backtracker
en ninguno; todos acaban con 0 callejones reales. 390 tableros de 3x3 a
60x40 por el analizador: los 195 perfectos dan *PERFECT maze* y los 195
jugables, *bonus-grade* con `--max-dead-ends 0`. En 20x15 perfecto,
Kruskal deja de media 81 callejones reales y el backtracker 30. En el
repo real, 20x15 con semilla 42: perfecto `84 + 3`; jugable `0 + 3` con
58 bucles y *bonus-grade*, y el mismo fichero en dos ejecuciones; 3x3
jugable, *bonus-grade* con el aviso del "42". Las cinco cifras coinciden
exactamente con la reconstrucción, braiding incluido: las medidas que
solo se hicieron allí valen.

**Consecuencias.** `tests/test_kruskal.py`, 88 tests: los del
backtracker más los del union-find (`union` dice si ha unido, una cadena
de 5.000 celdas sin recursión, celdas desconocidas).
`tests/test_kruskal_pipeline.py`, 13 tests: cada algoritmo del registro genera
en los dos modos, el analizador en los dos modos, y un espía exige que
se llegue a la apertura forzada en 3x3 (22 de 200 semillas). En
`tests/test_generator.py`, `StubAlgorithm` pasa a `BrokenAlgorithm`, que
intenta abrir el borde, y el test del stub se sustituye por
`test_buggy_algorithm_names_how_to_rebuild_it`. Las mutaciones abrir
todo, `random` global, sin barajar, solo muros al este y guardia antiguo
las detecta algún test. Quitar solo la unión por tamaño, o solo el *path
halving*, no lo detecta ninguno: son rendimiento, no corrección, y la
docstring lo dice. El README debe describir `ALGORITHM=kruskal` y la
diferencia de textura (capítulo VII y §8.1 puntos 6 y 7). Repo real:
`make lint` y `make lint-strict` sobre 35 ficheros y 773 tests, sin
ninguno saltado.

---

## ADR-028 — El wheel se construye reproducible en la raíz, lleva su documentación y `py.typed`, y se prueba fuera del repo copiando también `app/`

**Fecha:** 2026-10-31 · **Estado:** Aceptada · Completa ADR-008; ADR-031 añade la protección contra CRLF (2026-10-31)

**Contexto.** B6. El `pyproject.toml` estaba hecho, pero faltaban el
wheel en la raíz y su target. Al releer el capítulo VI del subject y la
hoja de evaluación aparecieron requisitos que no estaban en el plan. El
módulo tiene que estar *(código y documentación)* en un solo fichero, y
el README principal *no* forma parte de él. Y la hoja pide instalar el
paquete en otro virtualenv y probarlo *con `a_maze_ing.py` y su fichero
de configuración*.

**Decisión.**

- **`make package`** construye el wheel directamente en la raíz
  (`--outdir .`). Antes borra `build/`, `*.egg-info` y el wheel
  anterior, y construye con `SOURCE_DATE_EPOCH` fijado al 2026-09-23,
  el día en que empezó el proyecto.
- **`make package-test`** crea un virtualenv nuevo en `/tmp`, instala el
  wheel, copia `a_maze_ing.py`, `app/` y la configuración, comprueba que
  `mazegen` se importa desde `site-packages` y ejecuta el programa.
- En `pyproject.toml`, `setuptools==84.2.1` se fija exacto en
  `[build-system]`.
- **Documentación dentro del paquete.** `readme` apunta a
  `mazegen/README.md`, y ese fichero y `mazegen/py.typed` van como
  `package-data`.
- Los targets se llaman `package` y no `build`, para no confundirlos con
  la carpeta `build/` ni con la herramienta del mismo nombre.

**Medido antes de decidir.**
- *`build/` contamina el wheel.* Un módulo creado, construido y borrado
  seguía dentro del wheel de la construcción siguiente; con `build/`
  borrado, no.
- *Bytes del wheel.* Dos construcciones seguidas daban hashes distintos,
  por las fechas del zip. Con la fecha fija salen idénticas. Con
  `setuptools` 77.0.3 y 84.2.1, el mismo código da bytes distintos.
- *`py.typed`.* Un proyecto que reutiliza el wheel instalado falla con
  `mypy --strict` (`Returning Any`) sin el marcador, y pasa con él.
- *Layout plano.* Fuera del repo, el mismo virtualenv importa `mazegen`
  desde `site-packages`; desde la raíz del repo, la carpeta local.
- *El procedimiento de ADR-008 estaba incompleto.* Copiaba solo
  `a_maze_ing.py` y la configuración, pero `a_maze_ing.py` importa
  `app/`, que no va en el wheel.

**Alternativas descartadas.**
- *Construir en `dist/` y copiar a la raíz.* Un paso más para el mismo
  resultado.
- *Construir también el sdist.* El subject admite uno u otro, y un solo
  fichero es más fácil de vigilar.
- *Dependencias de fichero en Make en vez de reconstruir siempre.* Con
  la construcción reproducible, reconstruir no cuesta nada, y las fechas
  que deja `git checkout` confunden a Make.
- *Fecha tomada del último commit.* Sería circular: cada commit cambia
  la fecha, y la fecha nueva cambia el wheel que acaba de subirse.
- *`--no-isolation`, con `setuptools` en `requirements-dev.txt`.* El
  evaluador construirá aislado; mejor construir igual que él.
- *El README del proyecto como `readme`.* El subject separa las dos
  documentaciones.
- *Meter `app/` en el wheel.* No es reutilizable (ADR-002).

**Consecuencias.** `tests/test_package_docs.py` ejecuta, en orden, todos
los bloques `python` de `mazegen/README.md`, así que un nombre que no
exporte el paquete falla en los tests y no en un proyecto futuro.

Verificado en el repo real:
- 775 tests y lint en 36 ficheros.
- Dos `make package` seguidos dan el mismo hash (`1f6e8d95…`), sin
  restos de `build/`, y todas las fechas del zip son las del
  2026-09-23.
- El wheel lleva el código, la documentación, `py.typed` y la licencia,
  sin `app/` ni `tests/`, y `git status` lo ve.
- `make package-test` pasa con el `a_maze_ing.py` real.
- Tras el commit, `make package` deja `git status` vacío: el wheel
  subido corresponde al código subido.

Regla desde ahora: todo cambio en `mazegen/` va con `make package` en
el mismo commit. El primer `make package` necesita red, porque
descarga `setuptools`.

---

## ADR-029 — Lo que la hoja castiga con un 0 en el README, y el analizador en ambos modos, se vigilan con tests

**Fecha:** 2026-10-31 · **Estado:** Aceptada

**Contexto.** B8 y B9. Que falte un elemento del README pone la nota a 0,
y el subject exige además que el README principal contenga la
documentación del módulo, que ADR-028 ya mete en el wheel: dos copias
del mismo texto que pueden divergir. En B9, los tests que pasaban
tableros jugables por el analizador eran solo de Kruskal o de
`PATTERN=4`: la combinación que verá el evaluador, backtracker con el
"42", no pasaba por él.

**Decisión.**

- **README en inglés**, como recomienda el subject y como está el
  código.
- La primera línea es la exacta del capítulo VII. **Description**,
  **Instructions** y **Resources** llevan esos nombres literales y van
  en ese orden, que es el que sigue la hoja; el resto de elementos
  obligatorios van después, en el orden del subject.
- La sección **Reusable module** contiene `mazegen/README.md` sin su
  título y con los encabezados un nivel más abajo.
- Resources lista solo las referencias que el equipo confirmó haber
  consultado.
- La redacción del uso de la IA la decidió el equipo, después de
  repasar lo que pide la hoja: tareas *y partes* del proyecto.
- `tests/test_readme.py` comprueba la primera línea, las 13 secciones,
  su orden y que la copia de la documentación del módulo es idéntica.
- `tests/test_analyzer_modes.py` pasa por el analizador cada algoritmo
  de `available()`, en 3x3, 9x7, 20x15 y 41x25, con tres semillas, el
  "42" y el writer real: *PERFECT maze* en modo perfecto, y
  *bonus-grade* con `--max-dead-ends 0` en modo jugable.

**Alternativas descartadas.**
- *Enlazar la documentación del módulo en vez de copiarla.* El subject
  pide que el README la contenga.
- *Revisar el README solo a mano, con la hoja delante.* Una edición
  posterior puede romper un elemento sin que nadie lo note.
- *Ampliar los tests de Kruskal con el backtracker.* El test recorre el
  registro, así que un tercer algoritmo quedaría cubierto sin tocarlo.

**Medido.** `test_readme.py` falla si se cambia un login de la primera
línea, o una palabra de solo una de las dos copias de la documentación.
`test_analyzer_modes.py` falla en 6 de 16 casos si el braiding se
conforma con dejar un callejón. En el repo real: 807 tests, lint en 38
ficheros, y Ctrl+C sale del menú sin traceback.

**Consecuencias.** Toda la vía B queda cerrada. Cualquier cambio en
`mazegen/README.md` tiene que repetirse en el README principal, o falla
el test. Si cambia la planificación hasta la entrega, la sección
*Planning and how it evolved* se actualiza en la fase final.

---

## ADR-030 — C3: el aviso del "42" se queda en pantalla, `WIDTH` y `HEIGHT` tienen un máximo, y cuatro entradas más dejan de terminar en traceback o en un mensaje confuso

**Fecha:** 2026-10-31 · **Estado:** Aceptada · Matiza ADR-024

**Contexto.** C3: la lista de casos límite de PLAN §5, recorrida contra
el programa real. Los casos de la lista daban mensaje claro y código 1,
pero leyendo el código y repitiendo cada caso aparecieron cinco
problemas fuera de lo que cubrían los tests.

**Medido antes de decidir**, en el repo real, con el código anterior:

- *El aviso del "42" era invisible.* Con `WIDTH=8`, el aviso salía por
  `stderr` y la línea siguiente de la salida era `\033[H\033[J`, el
  borrado de pantalla con el que empieza cada frame del menú. La hoja
  pide un mensaje en terminal cuando el patrón no cabe, y ese mensaje
  no lo llegaba a ver nadie.
- *Un tamaño enorme agotaba la memoria.* `WIDTH=100000000`, con la
  memoria limitada a 2 GB, terminaba en `MemoryError` desde
  `Maze.__init__`, que crea `height` listas de `width + 1` booleanos al
  estampar el patrón en blanco (ADR-020). Sin límite, el sistema mata el
  proceso: una terminación inesperada.
- *Bytes que no son UTF-8 en el menú.* Con `stdin` decodificado en modo
  estricto, que es lo que hace Python con un locale real como
  `en_US.UTF-8`, `printf '\377\n' | python3 a_maze_ing.py config.txt`
  terminaba en `UnicodeDecodeError`. En casa no se reproduce, porque con
  `C.UTF-8` Python decodifica con `surrogateescape` y el menú respondía
  `unknown choice '\udcff'`; se reprodujo forzando
  `PYTHONIOENCODING=utf-8:strict`.
- *`ENTRY=(0,0)` daba* `ENTRY must be an integer, got '(0'`: cita medio
  token y no dice que el formato es `x,y`. Es el quinto error de la hoja.
- *Un fichero guardado con BOM* fallaba en la primera línea, aunque
  fuera un comentario: `line 1: expected KEY=VALUE, got '\ufeff# A-Maze-ing…'`.

**Decisión.**

- *El aviso.* `pattern_warning()`, en `a_maze_ing.py`, solo construye
  el texto. `main` lo imprime por `stderr`, que es lo que queda si el
  programa termina antes del menú (un fichero de salida que no se puede
  escribir), y se lo pasa al menú: `Menu(generator, config, *,
  notice="")` lo muestra en todas las pantallas, bajo el laberinto. Es
  persistente porque la condición también lo es: regenerar mantiene el
  tamaño. Sin `notice`, el frame es idéntico al anterior.
- *El tamaño.* `MAX_SIDE = 500` en `app/config_parser.py`, con
  `parse_side` para `WIDTH` y `HEIGHT`: `WIDTH must be at most 500, got
  …`. Solo el máximo: el mínimo es una regla de lo que es un laberinto y
  sigue en el generador; el máximo es un presupuesto de este programa,
  tiempo y memoria. Esto matiza ADR-024: el parser comprueba sintaxis,
  tipos y los límites del programa; lo que hace posible un laberinto lo
  sigue comprobando `MazeGenerator`.
- *El menú* trata un `UnicodeDecodeError` como una elección inválida:
  `unreadable input (not UTF-8), pick 1 to 5`.
- *Las tuplas.* `parse_coords` desempaqueta y convierte dentro de un
  solo `try`: una lista de longitud incorrecta y un `int()` que falla
  lanzan los dos `ValueError`, e `int()` ya ignora los espacios. Toda
  tupla mal formada da `must be two integers written x,y, got …`, con
  el valor completo.
- *El BOM.* El fichero se lee con `encoding="utf-8-sig"`, que lee igual
  un UTF-8 normal.
- La sección del fichero de configuración del README documenta los dos
  límites y el aviso.

**Alternativas descartadas.**
- *No borrar la pantalla en el primer frame.* El aviso desaparecería a
  la primera pulsación.
- *Que el menú calcule el aviso desde `pattern_skipped`.* El texto
  quedaría escrito en dos sitios.
- *Pedir "pulsa Enter" antes del menú.* Una pulsación de más para el
  evaluador, y rompe las sesiones guionizadas de `test_menu.py`.
- *El máximo en `mazegen`.* Cambiaría el contrato de la librería y
  obligaría a reconstruir el wheel, y limitaría a quien la reutilice.
  En `app/`, el wheel no cambia.
- *Capturar `MemoryError`.* Con la sobreasignación de memoria de Linux,
  el sistema puede matar el proceso antes de que llegue la excepción.
- *Un máximo por número de celdas.* El mensaje no podría nombrar la
  clave que el usuario tiene que cambiar.

**Fuera de alcance, a propósito**: lo que no se provoca editando el
fichero de configuración o tecleando en el menú, que es lo que hace el
evaluador. `/dev/zero` como configuración, `kill -9`, `Ctrl+\`. Tampoco
`OUTPUT_FILE=config.txt`: no da traceback, pero sobrescribe la
configuración con el laberinto.

**Medido.** El valor de `MAX_SIDE`, generando en modo perfecto y
jugable con semilla 42:

| Tamaño | Perfecto | Jugable |
|---|---|---|
| 100x100 | 0,2 s | 0,3 s |
| 200x200 | 0,7 s | 1,3 s |
| 400x400 | 3,5 s | 5,6 s |
| 500x500 | — | 8,8 s |

Al doblar el lado, el tiempo se multiplica por unos 4,3: casi lineal en
celdas. Pico de memoria de 63 MB hasta 400x400. Medido en el portátil
de Emmanuel; la medida anterior, 876 ms en 100x100 jugable, se tomó
en una máquina unas tres veces más lenta. Criterio: el tablero máximo, en modo
jugable, por debajo de unos 20 segundos.

Después de los arreglos, en el repo real: `WIDTH=100000000` da el error
al instante; el aviso aparece dos veces, en `stderr` y en la pantalla
del menú; `ENTRY=(0,0)` da el mensaje nuevo; el fichero con BOM abre el
menú; con `stdin` estricto no hay traceback. Los mensajes del motor no
cambian: `ENTRY (6, 5) falls on the '42' pattern, choose a free cell`,
`unknown algorithm 'prim', pick one of backtracker, kruskal`, `cannot
write output file 'no/dir/m.txt': No such file or directory`.

`tests/test_edge_cases.py` recorre la lista de C3 a través de `main()`,
en el mismo proceso: una excepción que escape de `main` falla el test.
Cada caso parte del `config.txt` del repo y cambia una sola cosa. Los
mensajes del parser se comprueban literalmente; los del generador, solo
por el prefijo `error:`. El caso de tamaño usa `MAX_SIDE + 1`, para que
quitar el límite no agote la memoria del que pasa los tests. En la
reconstrucción, con el código anterior fallaban 9 de sus 38 tests, y
cada uno de los cinco arreglos lo detecta alguno. En el repo real: 845
tests y lint en 39 ficheros. Un test de `test_config_parser.py` esperaba
el mensaje antiguo de `EXIT=19,x` y se actualizó.

**Consecuencias.** Dos cambios de contrato en la aplicación: el
parámetro `notice` del menú y `MAX_SIDE`. `mazegen/` no cambia, ni el
wheel. Si el tablero de 500x500 pasa de 20 segundos en las máquinas del
campus, `MAX_SIDE` baja a 400: es una constante, y su test se ajusta
solo.

---

## ADR-031 — Clon limpio: el wheel se construye desde la carpeta de trabajo, así que `make package` rechaza los ficheros en CRLF; el analizador se queda fuera; GitHub es la única fuente de verdad

**Fecha:** 2026-10-31 · **Estado:** Aceptada · Completa ADR-028

**Contexto.** C1 y C2: clonar el repo de GitHub en una carpeta vacía y
repetir todo lo que hará el evaluador. En el clon, `make package`
produjo un wheel distinto del commiteado. La única diferencia era el
`LICENSE.md` de dentro: 1091 bytes frente a 1080, los 11 retornos de
carro de un fichero de 11 líneas.

**Causa.** `make package` construye desde la carpeta de trabajo, no
desde lo commiteado. En la de Emmanuel había siete ficheros en CRLF,
todos llegados desde la máquina de Lucas: `LICENSE.md`,
`pyproject.toml`, `a_maze_ing.py` y los cuatro de `app/`.
`.gitattributes` los guarda en LF en el repo, así que `git status` no
los mostraba, y la comprobación de ADR-028 tampoco podía verlo: en esa
carpeta, cada `make package` leía el mismo `LICENSE.md` en CRLF y daba
el mismo wheel. Solo una carpeta con los ficheros tal como están en el
repo saca la diferencia. VS Code, con `files.eol` en `auto`, conserva el
final de línea que tenía cada fichero al abrirlo.

**Decisión.**

- **Se reconstruye el wheel** desde los ficheros en LF. En la carpeta de
  trabajo, ya limpia, y en el clon, el hash es el mismo
  (`b1817f50…`): dos carpetas distintas, mismos bytes, que es lo que
  promete ADR-028.
- **`make package` se niega a construir** si alguno de los ficheros que
  entran en el paquete (`mazegen/`, `LICENSE.md`, `pyproject.toml`) tiene
  un retorno de carro, y dice cuál y cómo arreglarlo: `sed -i
  's/\r$//' FILE`. Busca con `grep -rlI`, que se salta los binarios
  como los `.pyc`. `package-test` depende de `package` y queda
  protegido igual.
- **`maze_analyzer.py` se queda fuera del repo.** Es código de la intra,
  el evaluador trae el suyo, y así el clon limpio es lo que verá él. Los
  dos cargadores (el de `test_analyzer.py` y la fixture de
  `conftest.py`) se quedan: unificarlos en la fase final es un cambio
  estético sin efecto en la nota.
- **El flujo de entrega.** Solo se puede subir a vogsphere desde un
  ordenador del campus. GitHub es la única fuente de verdad: en el
  campus se clona GitHub, se añade el remote de la intra, se sube, y se
  comprueba clonando la intra en una carpeta vacía. Un arreglo
  descubierto en el campus va primero a GitHub y después a la intra; al
  revés, los historiales divergen. Si el `HEAD` del servidor apunta a
  `master`, se sube con `main:master`.
- **Etiquetas anotadas.** `v1.0.0-rc1` en `2500735`, el código
  verificado a mano en S2 y S3 antes de los arreglos de C3; `v1.0.0`, en
  el commit que se entregue.
- `files.eol` en `\n` en el VS Code de los dos.

**Alternativas descartadas.**
- *Comprobar con `git ls-files --eol`.* Depende de git y mira todo el
  repo, no lo que entra en el paquete.
- *Normalizar los ficheros dentro del build.* Escondería el problema en
  vez de señalarlo.
- *No tocar nada y hacer siempre un clon limpio antes de empaquetar.*
  Hoy funcionó porque estaba en el plan; depende de que alguien se
  acuerde.
- *Proponer `rm FILE && git checkout -- FILE` como arreglo.* Perdería
  los cambios sin commitear de ese fichero; `sed` los conserva.

**Medido.** En el clon de GitHub: los siete ficheros obligatorios en el
repo, y en `git ls-files --eol` solo el wheel y `mazegen/py.typed`, que
está vacío. `make lint` y `make lint-strict` sin errores en 38 ficheros,
con flake8 7.4.1 y mypy 2.4.0. `make test`: 796 passed y 34 skipped sin
el analizador; con una copia, 845 passed. `make package-test` pasa,
`make clean` conserva el wheel, y tras el commit del wheel nuevo
(`4697ca8`), `make package` deja `git status` vacío también en el clon.
S2 y S3 a mano, antes: *PERFECT maze* con 280 celdas alcanzables y 0
bucles, el fichero con 15 líneas de 20 caracteres, la misma semilla da
el mismo fichero, y en modo jugable *bonus-grade* con `0 real + 3
enclosed` y 31 bucles. La protección, en la reconstrucción: deja
pasar una carpeta limpia con un `.pyc` que contiene un retorno de
carro, se para con un `.py` en CRLF, y vuelve a pasar tras el `sed`.

**Consecuencias.** Queda la parte de C1 que solo se puede hacer en el
campus: subir a vogsphere, clonarlo y repetir allí las comprobaciones,
que es el entorno del evaluador. Después de cada `pull`, conviene
comprobar `git ls-files --eol | awk '$2 == "w/crlf"'`.
