# A-Maze-ing — Plan de trabajo

Dos cronogramas sobre un mismo inventario de tareas: el **compartido**,
que es el oficial para Emmanuel y Lucas, y el **individual**, por si
Emmanuel recorre las dos vías. Los identificadores (`A3`, `B5`, `C1`)
son los mismos del plan inicial, para que nadie tenga que traducir.

Los bloques se miden en horas, no en fechas: cada uno son dos sesiones
de unas 3 horas. Poned las fechas encima según vuestra entrega.

✅ marca una tarea cerrada. El avance de la vía A lo anota Emmanuel y el
de la vía B, Lucas: una tarea de la vía B sin ✅ puede estar hecha y sin
anotar.

Última actualización: 30 oct 2026 · cerradas T0.1, T0.2, A4, A3, A5a,
A5b, A6, A7a, A7b, B1, B2, B3, B4, B5 y B7 (la vía B, corregida, ADR-024)
S1 cerrada · nueva tarea A9 por ADR-025.

---

## 1. Punto de partida

Al repartir ya estaba hecho y probado: `errors.py`, `maze.py`,
`pattern.py`, `tests/fixtures.py`, el `__init__` y el pipeline de
`generator.py`, el registro de algoritmos y `a_maze_ing.py`. Son unas 7
horas de la vía A invertidas antes del reparto, lo que explica que el
resto salga desigual.

| Vía | Estimado | Cerrado | Restante |
|---|---|---|---|
| Fase 0 | 2 h | 1 h 30 (T0.1, T0.2) | 30 min (T0.3) |
| Vía A (motor) | 16 h + 3 h de bonus | 15 h (A4, A3, A5a, A5b, A6, A7a, A7b) | 1 h (A9) + 3 h de bonus (A8) |
| Vía B (aplicación y entrega) | 22 h | 13 h (B1, B2, B3, B4, B5, B7) | 9 h (B6, B8a, B8b, B9) |
| Fase final conjunta | 9 h | — | 9 h |
| **Total** | **~52 h** con bonus | 29 h 30 | **~23 h** |

Las horas cerradas son las estimadas, no las reales. El total decía
~48 h, pero la suma de la tabla siempre dio 51; queda corregido, y
cuadra con el acumulado del cronograma individual. En pareja salen unas
25 h por cabeza. En solitario son unas 13 sesiones de 4 horas.

---

## 2. Inventario de tareas

| ID | Fichero | Qué hay que hacer | Depende de | Est. | Dif. |
|---|---|---|---|---|---|
| **T0.1** ✅ | `Makefile`, `.gitignore` | Targets install/run/debug/clean/lint/lint-strict. El `.gitignore` **no** debe excluir el wheel | — | 1 h | Baja |
| **T0.2** ✅ | `config.txt` | Configuración por defecto, con las tres claves opcionales comentadas | — | 30 min | Baja |
| **T0.3** | — | Acordar flujo git: `main`, ramas de feature, PR revisado por el otro | — | 30 min | Baja |
| **A3** ✅ | `algorithms/backtracker.py` | DFS iterativo con pila explícita sobre las celdas libres | `maze.py` | 3 h | Media |
| **A4** ✅ | `solver.py` | BFS con `deque`, reconstrucción del camino | `maze.py` | 2 h | Baja |
| **A5a** ✅ | `validator.py` | Chequeos comunes: conectividad, bordes, bloques 3x3 | `maze.py` | 2 h | Media |
| **A5b** ✅ | `validator.py` | Chequeos por modo: bucles (`E-V+C`) y callejones reales | A5a | 1 h | Media |
| **A6** ✅ | `braiding.py` | `would_open_3x3`, `dead_ends`, `braid`, `ensure_open` | A3, A5 | 6 h | **Alta** |
| **A7a** ✅ | `generator.py` | Cerrar el pipeline en modo perfecto y afinar los mensajes de error | A3, A5 | 30 min | Baja |
| **A7b** ✅ | `generator.py` | Repasar pipeline y mensajes con el braiding dentro | A6 | 30 min | Baja |
| **A8** | `algorithms/kruskal.py` | Union-find sobre aristas barajadas. **Bonus** | A3, A7a | 3 h | Media-alta |
| **A9** | `pattern.py` | Columna libre sobre la columna central y mínimo `4n + 4` con `n` impar; el "42" no cambia (ADR-025) | — | 1 h | Baja |
| **B1** ✅ | `config_parser.py` | `parse_config` y los tres parsers, con los cinco errores de la hoja | `errors.py` | 3 h | Media |
| **B2** ✅ | `a_maze_ing.py` | Ajustar el entry point a lo que devuelva B1 | B1 | 30 min | Baja |
| **B3** ✅ | `renderer.py` | Muros, entrada, salida, camino, patrón, paletas ANSI | `fixtures.py` | 5 h | Media |
| **B4** ✅ | `menu.py` | Las cuatro interacciones más guardar (ADR-009) | B3 | 2 h | Baja |
| **B5** ✅ | `writer.py` | Formato exacto: hex, línea vacía, entry, exit, camino | `fixtures.py` | 2 h | Baja |
| **B6** | `pyproject.toml` | Construir el wheel y probarlo **fuera del repo**. *Hecho el `pyproject.toml`; falta el wheel en la raíz y su target* | A7a | 3 h | Media |
| **B7** ✅ | `LICENSE.md` | Texto MIT con el año y los dos nombres (ADR-010) | — | 30 min | Baja |
| **B8a** | `README.md` | Esqueleto con las 11 secciones obligatorias, vacías | — | 30 min | Baja |
| **B8b** | `README.md` | Rellenarlo entero | todo | 2 h 30 | Baja |
| **B9** | `tests/` | pytest de los invariantes + `maze_analyzer.py` en ambos modos. *Ya hay tests de toda la vía B y `test_analyzer.py` escribe con el writer real; falta el analizador en modo jugable sobre ficheros del writer* | A7b, B5 | 3 h | Media |
| **C1** | — | Integración y fricciones | todo | 3 h | — |
| **C2** | — | `flake8` y `mypy --strict` a cero | C1 | 1 h | — |
| **C3** | — | Casos límite (ver 6) | C1 | 3 h | — |
| **C4** | — | Ensayo de defensa: cada uno explica los módulos del otro | C3 | 2 h | — |

A7 estaba como una sola tarea que dependía de A3–A6, pero los dos
cronogramas la ponían antes del braiding. Se divide igual que A5: A7a
cierra el modo perfecto, que es lo que desbloquea S2 y el wheel, y A7b
repasa el pipeline cuando exista A6.

---

## 3. Cronograma compartido — Emmanuel (vía A) y Lucas (vía B)

### Bloque 0 · juntos · 1 h

Los dos: leer `ARCHITECTURE.md` §4 (el contrato) y §8 (cómo se evalúa).
T0.1, T0.2 y T0.3. A partir de aquí nadie cambia una firma del contrato
sin avisar al otro.

### Bloque 1 · en paralelo · «el primer laberinto real»

| Emmanuel (7 h) | Lucas (6 h) |
|---|---|
| A4 solver ✅ | B5 writer ✅ |
| A3 backtracker ✅ | B7 licencia MIT ✅ |
| A5a validador común ✅ | B8a esqueleto del README |
| | B1 config parser (empezar) |

Orden obligado en la vía A: `generate()` llama a `validate()` siempre,
así que hasta que A5a no exista el pipeline completo no corre. Hecho:
con A3 y A5a, `generate()` corre entero en modo perfecto.

**🔗 Sincronización S1.** Juntar A3 + A5a + B5 y generar el primer
fichero de salida real. Pasarle `maze_analyzer.py`. Debe decir *wall
coherence OK*. Si algo falla aquí, falla el contrato, no el código.
*Estado:* ✅ cerrada. `tests/test_analyzer.py` escribe sus 40
laberintos con `write_maze` y todos pasan el analizador (ADR-024).

### Bloque 2 · en paralelo · «programa completo en modo perfecto»

| Emmanuel (2 h + arranque de A6) | Lucas (5 h 30) |
|---|---|
| A5b chequeos por modo ✅ | B1 terminar ✅ |
| A7a cerrar el modo perfecto ✅ | B2 ajustar el entry point ✅ |
| empezar A6 ✅ | B3 renderer ✅ |

A5b va antes que A6 sin excepción: el braiding crea bucles y necesita
que alguien los mida.

Durante este bloque se trabaja con una copia local del `config.txt` con
`PERFECT=True`: es el único modo que funciona hasta que exista el
braiding. El `config.txt` del repo se queda con `PERFECT=False`
(ADR-014). Desde A7a, con la configuración por defecto el programa ya
no rompe: sale con un error claro que pide `perfect=True` (ADR-020).

*Estado:* la parte de la vía A del bloque está hecha. `validate`
comprueba los dos modos y el generador no deja escapar ningún error
que no sea `MazeError`. A6 también está hecha (bloque 3), así que la
copia local con `PERFECT=True` ya no hace falta: la configuración por
defecto genera.

**🔗 Sincronización S2.** `python3 a_maze_ing.py <copia>` genera,
muestra y escribe un laberinto perfecto. **Este es el primer punto en
el que hay algo entregable.** Etiquetadlo en git y retirad
`tests/dump_maze.py` (ADR-018).
*Estado:* `dump_maze.py` retirado y el programa funciona. Queda hacerlo
a mano con `make run` y `PERFECT=True`, pasar el `maze.txt` por el
analizador, y poner la etiqueta.

### Bloque 3 · en paralelo · «modo Pac-Man»

| Emmanuel (6 h) | Lucas (5 h) |
|---|---|
| A6 braiding completo ✅, A7b ✅ | B4 menú ✅ |
| A9 patrón con `n` impar (ADR-025) | B6 empaquetado y wheel |

**🔗 Sincronización S3.** Cambiar el `config.txt` a `PERFECT=False` y
pasar `maze_analyzer.py --max-dead-ends 0`. Objetivo: *0 real + 3
enclosed*. Y aquí va el repaso innegociable de `maze.py` y
`braiding.py` línea a línea, los dos juntos.
*Estado:* el motor da *0 real + 3 enclosed* y *bonus-grade* en 20x15 con
semilla 42 en el repo real, y el programa completo escribe ficheros que
el analizador da por *bonus-grade*. Queda hacerlo a mano con `make run`
y el repaso conjunto.

### Bloque 4 · en paralelo · «bonus y pruebas»

| Emmanuel (3 h) | Lucas (5 h 30) |
|---|---|
| A8 Kruskal | B9 tests |
| ayudar con B9 | B8b README |

Emmanuel va más holgado en este bloque porque ya invirtió 7 h antes de
empezar el reparto: lo razonable es que coja parte de B9 y de C3.

### Bloque 5 · juntos · 9 h

C1, C2, C3 y C4. Nada de esto se hace por separado.

---

## 4. Cronograma individual — Emmanuel en las dos vías

Mismo inventario, un solo orden. El criterio es doble: atacar siempre
lo que desbloquea más cosas, y llegar cuanto antes a un programa que
funcione de punta a punta, para tener red de seguridad si el tiempo
aprieta.

| # | Tareas | Acumulado | Al terminar tienes |
|---|---|---|---|
| 1 | T0.1 ✅, T0.2 ✅, T0.3 | 2 h | `make run` y `make lint` funcionando |
| 2 | A4 solver ✅ | 4 h | camino más corto sobre `toy_maze()` |
| 3 | A3 backtracker ✅ | 7 h | laberintos de verdad en memoria |
| 4 | A5a validador común ✅ | 9 h | `generate()` corre entero en modo perfecto |
| 5 | B5 writer ✅ | 11 h | **fichero de salida validado por el analizador** |
| 6 | B7 licencia ✅, B8a esqueleto del README | 12 h | dos riesgos de nota 0 eliminados |
| 7 | B1 config parser ✅ | 15 h | el programa lee su configuración |
| 8 | B2 ajuste del entry point ✅ | 15 h 30 | `python3 a_maze_ing.py config.txt` |
| 9 | B3 renderer ✅ | 20 h 30 | **se ve el laberinto y el "42"** |
| 10 | B4 menú ✅ | 22 h 30 | todas las interacciones obligatorias |
| 11 | A5b chequeos por modo ✅, A7a ✅ | 24 h | *Hito: modo perfecto completo y evaluable* |
| 12 | B6 empaquetado y wheel | 27 h | *Hito: entregable con nota, aunque falte el braiding* |
| 13 | A6 braiding ✅, A7b ✅ | 33 h 30 | modo Pac-Man y bonus de cero callejones |
| 14 | B9 tests y analizador en ambos modos | 36 h 30 | red de seguridad ante regresiones |
| 15 | A9 patrón con `n` impar, A8 Kruskal | 40 h 30 | `PATTERN` de cualquier longitud y segundo bonus |
| 16 | B8b README completo | 43 h | los 11 elementos obligatorios |
| 17 | C1, C2, C3, C4 | 52 h | listo para defender |

Dos cosas que parecen fuera de sitio y no lo están:

El puesto 1 dice `make run` funcionando, pero `make run` no termina
hasta tener el writer y el renderer: lo que deja T0.1 es el target, no
el programa.

**El braiding va en el puesto 13, casi al final.** Es lo más difícil
del proyecto, y cuando llegas ahí ya tienes un programa completo,
empaquetado y entregable en modo perfecto. Si se tuerce, se entrega sin
el modo Pac-Man; si fuera lo primero, un braiding a medias te deja sin
nada que enseñar.

**El wheel se construye en el puesto 12, no al final.** La hoja pone un
0 si el `mazegen-*.whl` no está en la raíz del repo. Un wheel antiguo
commiteado pronto vale infinitamente más que uno perfecto que se te
olvida generar la última noche. Se reconstruye en C1.

---

## 5. La vía B en paralelo de Emmanuel

Esto va **encima** de las 24 h del cronograma compartido, no dentro.
Presupuesto realista: unas 8 h, la mitad de lo que le cuesta a Lucas,
porque no hay que decidir nada, solo escribir.

Cuatro reglas, ya recogidas en `ARCHITECTURE.md` §9:

1. Vive fuera de `main`, en una rama propia o fuera del repo. Nunca se
   mergea.
2. Se escribe **después** de que Lucas haya commiteado su versión.
   Antes convierte la revisión en dictado.
3. Lo que salga de comparar entra como sugerencia en el PR. La decisión
   final sobre un fichero de la vía B es de Lucas.
4. En el README los roles se escriben como son. Tener una versión
   paralela no cambia la autoría de lo entregado.

Orden sugerido, siempre a rebufo de Lucas: B5 → B1 → B3 → B4. B6, B7 y
B8 no tiene sentido duplicarlos.

---

## 6. Casos límite de C3

La lista, para no improvisarla el último día:

- `WIDTH=1`, `HEIGHT=0`, valores negativos
- `ENTRY` igual a `EXIT`
- coordenadas fuera de rango
- fichero de configuración inexistente, o sin permisos de lectura
- `WIDTH=abc`, `PERFECT=quizá`, `ENTRY=3`, `ENTRY=a,b`
- clave obligatoria ausente, línea sin `=`, clave duplicada
- laberinto demasiado pequeño para el "42" (avisa y sigue)
- `PATTERN=7`, sin glifo (error de configuración explícito)
- `OUTPUT_FILE` en un directorio que no existe o sin permisos
- `Ctrl+C` y `Ctrl+D` en el menú
- opción del menú inválida: letras, número fuera de rango, línea vacía

Ninguno de estos puede terminar en traceback. La hoja pone un 0 ante
cualquier terminación inesperada.

---

## 7. Riesgos de calendario

- **El braiding se come su estimación.** Cerrado: A6 y A7b hechas en
  su estimación, con el bonus de cero callejones medido.
- **El empaquetado no es programar.** Es leer documentación de
  `pyproject.toml`, `build` y wheels: 2 o 3 h de aprendizaje que no
  produce código visible. No es tiempo perdido, es el capítulo VI.
- **El README es un riesgo de nota 0, no un trámite.** Por eso el
  esqueleto se crea en la sesión 6 y se va rellenando, no se escribe la
  última noche.
- **Los bonus solo cuentan si todo lo anterior está correcto.** A8 va
  después de B9 a propósito.
