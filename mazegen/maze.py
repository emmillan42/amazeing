"""The :class:`Maze` data structure.

Walls are stored **once**, as shared edges, never as four bits per
cell::

    _v_walls[y][x]  vertical wall on the WEST side of cell (x, y),
                    with x in 0 .. width  (width + 1 columns)
    _h_walls[y][x]  horizontal wall on the NORTH side of cell (x, y),
                    with y in 0 .. height (height + 1 rows)

So the north wall of ``(x, y)`` and the south wall of ``(x, y - 1)``
are the very same boolean.  Coherence between neighbours is therefore
structural: no operation can break it, and the hexadecimal code of a
cell is computed only on export, never stored.

Coordinates are ``(x, y)`` pairs: ``x`` is the column, ``y`` the row,
and ``y`` grows southwards, so ``(0, 0)`` is the north-west corner,
which matches ``ENTRY=0,0`` in the configuration file.

ES — Estructura de datos :class:`Maze`.

Los muros se guardan **una sola vez**, como aristas compartidas, nunca
como cuatro bits por celda::

    _v_walls[y][x]  muro vertical al OESTE de la celda (x, y),
                    con x en 0 .. width  (width + 1 columnas)
    _h_walls[y][x]  muro horizontal al NORTE de la celda (x, y),
                    con y en 0 .. height (height + 1 filas)

Así, el muro norte de ``(x, y)`` y el sur de ``(x, y - 1)`` son el
mismo booleano. La coherencia entre vecinas es estructural: ninguna
operación puede romperla, y el código hexadecimal de una celda se
calcula solo al exportar, nunca se almacena.

Las coordenadas son parejas ``(x, y)``: ``x`` es la columna, ``y`` la
fila, y ``y`` crece hacia el sur, de modo que ``(0, 0)`` es la esquina
noroeste, que es lo que significa ``ENTRY=0,0`` en el fichero de
configuración.
"""
from __future__ import annotations

from enum import Enum

from mazegen.errors import InvalidGeometryError, MazeError

Cell = tuple[int, int]

ALL_WALLS: int = 0b1111


class Direction(Enum):
    """A cardinal direction, its output bit and its step on the grid.

    The value is ``(bit, dx, dy)``, where ``bit`` is the weight used by
    the hexadecimal output format of the subject.

    ES — Una dirección cardinal, su bit de salida y su desplazamiento.

    El valor es ``(bit, dx, dy)``, donde ``bit`` es el peso que usa el
    formato hexadecimal de salida que pide el subject.
    """

    NORTH = (0b0001, 0, -1)
    EAST = (0b0010, 1, 0)
    SOUTH = (0b0100, 0, 1)
    WEST = (0b1000, -1, 0)

    @property
    def bit(self) -> int:
        """Weight of this direction in the hexadecimal cell code.

        ES — Peso de esta dirección en el código hexadecimal.
        """
        return int(self.value[0])

    @property
    def delta(self) -> Cell:
        """Step ``(dx, dy)`` to reach the neighbour in this direction.

        ES — Desplazamiento ``(dx, dy)`` hasta la celda vecina.
        """
        return (int(self.value[1]), int(self.value[2]))

    @property
    def letter(self) -> str:
        """First letter, as used by the solution string.

        ES — Inicial, tal como la usa la cadena de la solución.
        """
        return self.name[0]

    @property
    def opposite(self) -> Direction:
        """The direction facing this one.

        ES — La dirección opuesta a esta.
        """
        return _OPPOSITE[self]


_OPPOSITE: dict[Direction, Direction] = {
    Direction.NORTH: Direction.SOUTH,
    Direction.EAST: Direction.WEST,
    Direction.SOUTH: Direction.NORTH,
    Direction.WEST: Direction.EAST,
}


def validate_geometry(
    width: int, height: int, entry: Cell, exit: Cell | None
) -> Cell:
    """Check a geometry and return the exit, resolved if it was None.

    Shared by :class:`Maze` and
    :class:`~mazegen.generator.MazeGenerator` so that a wrong entry or
    exit is rejected as soon as the caller asks for it, not only when
    the maze is finally built.

    Args:
        width: Number of columns.
        height: Number of rows.
        entry: Entry cell.
        exit: Exit cell, or ``None`` for the south-east corner.

    Returns:
        The exit cell, the south-east corner when ``exit`` was
        ``None``.

    Raises:
        InvalidGeometryError: If the size is not positive, if a cell
            falls outside the grid, or if entry and exit are the same.

    ES — Valida una geometría y devuelve la salida ya resuelta.

    La comparten :class:`Maze` y
    :class:`~mazegen.generator.MazeGenerator`, de modo que una entrada
    o una salida incorrectas se rechazan en cuanto alguien las pide, y
    no solo al construir el laberinto.

    Argumentos:
        width: Número de columnas.
        height: Número de filas.
        entry: Celda de entrada.
        exit: Celda de salida, o ``None`` para la esquina sureste.

    Devuelve:
        La celda de salida; la esquina sureste si ``exit`` era
        ``None``.

    Lanza:
        InvalidGeometryError: Si el tamaño no es positivo, si una celda
            cae fuera de la rejilla, o si entrada y salida coinciden.
    """
    if width < 1 or height < 1:
        raise InvalidGeometryError(
            f"invalid maze size: {width}x{height}"
        )
    if exit is None:
        exit = (width - 1, height - 1)
    for name, (x, y) in (("ENTRY", entry), ("EXIT", exit)):
        if not (0 <= x < width and 0 <= y < height):
            raise InvalidGeometryError(
                f"{name} ({x}, {y}) is outside a {width}x{height} maze"
            )
    if entry == exit:
        raise InvalidGeometryError(
            "ENTRY and EXIT must be two different cells"
        )
    return exit


class Maze:
    """A rectangular grid of cells and the walls between them.

    A new maze has every wall closed: generating means opening walls.

    Attributes:
        width: Number of columns.
        height: Number of rows.
        entry: Entry cell.
        exit: Exit cell.
        blocked: Cells closed on purpose by the ``42`` pattern.

    ES — Una rejilla rectangular de celdas y los muros entre ellas.

    Un laberinto recién creado tiene todos los muros cerrados: generar
    consiste en abrirlos.

    Atributos:
        width: Número de columnas.
        height: Número de filas.
        entry: Celda de entrada.
        exit: Celda de salida.
        blocked: Celdas cerradas a propósito por el patrón ``42``.
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: Cell = (0, 0),
        exit: Cell | None = None,
    ) -> None:
        """Build a maze where every wall is closed.

        Args:
            width: Number of columns, at least 1.
            height: Number of rows, at least 1.
            entry: Entry cell, north-west corner by default.
            exit: Exit cell, south-east corner by default.

        Raises:
            InvalidGeometryError: If the size is not positive, if a
                cell falls outside the grid, or if entry and exit are
                the same cell.

        ES — Construye un laberinto con todos los muros cerrados.

        Argumentos:
            width: Número de columnas, mínimo 1.
            height: Número de filas, mínimo 1.
            entry: Celda de entrada, esquina noroeste por defecto.
            exit: Celda de salida, esquina sureste por defecto.

        Lanza:
            InvalidGeometryError: Si el tamaño no es positivo, si una
                celda cae fuera de la rejilla, o si entrada y salida
                son la misma celda.
        """
        exit = validate_geometry(width, height, entry, exit)
        self._width: int = width
        self._height: int = height
        self._entry: Cell = entry
        self._exit: Cell = exit
        self._v_walls: list[list[bool]] = [
            [True] * (width + 1) for _ in range(height)
        ]
        self._h_walls: list[list[bool]] = [
            [True] * width for _ in range(height + 1)
        ]
        self._blocked: set[Cell] = set()
        self._solution: list[Cell] = []

    # ------------------------------------------------------------------
    # Geometry / Geometría
    # ------------------------------------------------------------------

    @property
    def width(self) -> int:
        """Number of columns of the grid.

        ES — Número de columnas de la rejilla.
        """
        return self._width

    @property
    def height(self) -> int:
        """Number of rows of the grid.

        ES — Número de filas de la rejilla.
        """
        return self._height

    @property
    def entry(self) -> Cell:
        """Entry cell.

        ES — Celda de entrada.
        """
        return self._entry

    @property
    def exit(self) -> Cell:
        """Exit cell.

        ES — Celda de salida.
        """
        return self._exit

    def in_bounds(self, x: int, y: int) -> bool:
        """Tell whether ``(x, y)`` is inside the grid.

        ES — Indica si ``(x, y)`` está dentro de la rejilla.
        """
        return 0 <= x < self._width and 0 <= y < self._height

    def cells(self) -> list[Cell]:
        """Return every cell in row-major order.

        ES — Devuelve todas las celdas, por filas de norte a sur.
        """
        return [
            (x, y)
            for y in range(self._height)
            for x in range(self._width)
        ]

    def neighbour(self, x: int, y: int, direction: Direction) -> (
        Cell | None
    ):
        """Return the cell next to ``(x, y)``, or ``None`` if outside.

        ES — Devuelve la celda contigua a ``(x, y)``, o ``None`` si
        caería fuera de la rejilla.
        """
        dx, dy = direction.delta
        target = (x + dx, y + dy)
        return target if self.in_bounds(*target) else None

    def neighbours(self, x: int, y: int) -> list[Cell]:
        """Return the in-bounds neighbours, walls ignored.

        ES — Devuelve las vecinas que caen dentro de la rejilla, sin
        mirar los muros.
        """
        result: list[Cell] = []
        for direction in Direction:
            target = self.neighbour(x, y, direction)
            if target is not None:
                result.append(target)
        return result

    def _ensure_inside(self, x: int, y: int) -> None:
        """Raise :class:`MazeError` if ``(x, y)`` is out of bounds.

        ES — Lanza :class:`MazeError` si ``(x, y)`` queda fuera.
        """
        if not self.in_bounds(x, y):
            raise MazeError(f"cell ({x}, {y}) is outside the maze")

    # ------------------------------------------------------------------
    # Walls / Muros
    # ------------------------------------------------------------------

    def has_wall(self, x: int, y: int, direction: Direction) -> bool:
        """Tell whether the wall of ``(x, y)`` on that side is closed.

        ES — Indica si el muro de ``(x, y)`` por ese lado está cerrado.
        """
        self._ensure_inside(x, y)
        if direction is Direction.NORTH:
            return self._h_walls[y][x]
        if direction is Direction.SOUTH:
            return self._h_walls[y + 1][x]
        if direction is Direction.WEST:
            return self._v_walls[y][x]
        return self._v_walls[y][x + 1]

    def _set_wall(
        self, x: int, y: int, direction: Direction, closed: bool
    ) -> None:
        """Write the shared edge on that side of ``(x, y)``.

        ES — Escribe la arista compartida de ese lado de ``(x, y)``.
        """
        if direction is Direction.NORTH:
            self._h_walls[y][x] = closed
        elif direction is Direction.SOUTH:
            self._h_walls[y + 1][x] = closed
        elif direction is Direction.WEST:
            self._v_walls[y][x] = closed
        else:
            self._v_walls[y][x + 1] = closed

    def open_wall(self, x: int, y: int, direction: Direction) -> None:
        """Open the wall shared by ``(x, y)`` and its neighbour.

        One single boolean is written, so both cells see the change.

        Raises:
            MazeError: If the cell is outside the maze, if the wall
                belongs to the outer border, or if one of the two cells
                is blocked by the ``42`` pattern.

        ES — Abre el muro que comparten ``(x, y)`` y su vecina.

        Se escribe un único booleano, así que las dos celdas ven el
        cambio.

        Lanza:
            MazeError: Si la celda cae fuera del laberinto, si el muro
                pertenece al borde exterior, o si alguna de las dos
                celdas está bloqueada por el patrón ``42``.
        """
        self._ensure_inside(x, y)
        target = self.neighbour(x, y, direction)
        if target is None:
            raise MazeError(
                f"cannot open the outer border at ({x}, {y})"
            )
        if (x, y) in self._blocked or target in self._blocked:
            raise MazeError(
                f"cannot open a wall of the blocked cell ({x}, {y})"
            )
        self._set_wall(x, y, direction, False)

    def close_wall(self, x: int, y: int, direction: Direction) -> None:
        """Close the wall shared by ``(x, y)`` and its neighbour.

        ES — Cierra el muro que comparten ``(x, y)`` y su vecina.
        """
        self._ensure_inside(x, y)
        self._set_wall(x, y, direction, True)

    def block(self, x: int, y: int) -> None:
        """Close the four walls of ``(x, y)`` and reserve the cell.

        Blocked cells are the ones drawing the ``42`` pattern: they are
        isolated on purpose and :meth:`open_wall` refuses to touch
        them.

        ES — Cierra los cuatro muros de ``(x, y)`` y reserva la celda.

        Las celdas bloqueadas son las que dibujan el patrón ``42``:
        están aisladas a propósito y :meth:`open_wall` se niega a
        tocarlas.
        """
        self._ensure_inside(x, y)
        for direction in Direction:
            self._set_wall(x, y, direction, True)
        self._blocked.add((x, y))

    @property
    def blocked(self) -> frozenset[Cell]:
        """Cells reserved by the ``42`` pattern.

        ES — Celdas reservadas por el patrón ``42``.
        """
        return frozenset(self._blocked)

    def is_blocked(self, x: int, y: int) -> bool:
        """Tell whether ``(x, y)`` belongs to the ``42`` pattern.

        ES — Indica si ``(x, y)`` pertenece al patrón ``42``.
        """
        self._ensure_inside(x, y)
        return (x, y) in self._blocked

    # ------------------------------------------------------------------
    # Queries / Consultas
    # ------------------------------------------------------------------

    def open_directions(self, x: int, y: int) -> list[Direction]:
        """Return the directions leading to a reachable neighbour.

        ES — Devuelve las direcciones que llevan a una vecina
        alcanzable.
        """
        return [
            direction
            for direction in Direction
            if not self.has_wall(x, y, direction)
            and self.neighbour(x, y, direction) is not None
        ]

    def open_sides(self, x: int, y: int) -> list[str]:
        """Return the open sides as ``N``/``E``/``S``/``W`` letters.

        ES — Devuelve los lados abiertos como letras
        ``N``/``E``/``S``/``W``.
        """
        return [
            direction.letter
            for direction in self.open_directions(x, y)
        ]

    def open_neighbours(self, x: int, y: int) -> list[Cell]:
        """Return the cells reachable from ``(x, y)`` in one step.

        ES — Devuelve las celdas alcanzables desde ``(x, y)`` en un
        paso.
        """
        result: list[Cell] = []
        for direction in self.open_directions(x, y):
            target = self.neighbour(x, y, direction)
            if target is not None:
                result.append(target)
        return result

    def degree(self, x: int, y: int) -> int:
        """Return how many exits ``(x, y)`` has (1 means dead end).

        ES — Devuelve cuántas salidas tiene ``(x, y)``; 1 significa
        callejón sin salida.
        """
        return len(self.open_directions(x, y))

    def nearest_free(self, x: int, y: int) -> Cell:
        """Return the closest cell that is not blocked.

        Distance is the squared euclidean one, ties are broken by row
        then column so the result is always deterministic.

        Raises:
            InvalidGeometryError: If every cell of the maze is blocked.

        ES — Devuelve la celda libre más cercana a ``(x, y)``.

        La distancia es la euclídea al cuadrado, y los empates se
        resuelven por fila y luego por columna, así que el resultado es
        siempre determinista.

        Lanza:
            InvalidGeometryError: Si todas las celdas están bloqueadas.
        """
        best: Cell | None = None
        best_key: tuple[int, int, int] = (0, 0, 0)
        for cx, cy in self.cells():
            if (cx, cy) in self._blocked:
                continue
            key = ((cx - x) ** 2 + (cy - y) ** 2, cy, cx)
            if best is None or key < best_key:
                best, best_key = (cx, cy), key
        if best is None:
            raise InvalidGeometryError("every cell of the maze is blocked")
        return best

    def centre(self) -> Cell:
        """Return the free cell closest to the geometric centre.

        The ``42`` pattern is drawn in the middle of the grid, so the
        geometric centre may well be a blocked cell.  Defining the
        centre as the nearest free cell keeps the Pac-Man start valid
        for any size instead of moving the pattern around.

        ES — Devuelve la celda libre más cercana al centro geométrico.

        El patrón ``42`` se dibuja en mitad de la rejilla, así que el
        centro geométrico puede caer perfectamente sobre una celda
        bloqueada. Definir el centro como la celda libre más cercana
        mantiene válido el arranque del modo Pac-Man para cualquier
        tamaño, en lugar de tener que desplazar el patrón.
        """
        return self.nearest_free((self._width - 1) // 2,
                                 (self._height - 1) // 2)

    def corners(self) -> list[Cell]:
        """Return the four corner cells.

        ES — Devuelve las cuatro celdas de las esquinas.
        """
        last_x, last_y = self._width - 1, self._height - 1
        return [(0, 0), (last_x, 0), (0, last_y), (last_x, last_y)]

    # ------------------------------------------------------------------
    # Solution / Solución
    # ------------------------------------------------------------------

    @property
    def solution(self) -> list[Cell]:
        """The shortest path, entry and exit included.

        ES — El camino más corto, entrada y salida incluidas.
        """
        return list(self._solution)

    def set_solution(self, path: list[Cell]) -> None:
        """Store the shortest path computed by the solver.

        ES — Guarda el camino más corto calculado por el solver.
        """
        self._solution = list(path)

    def solution_string(self) -> str:
        """Return the stored path as ``N``/``E``/``S``/``W`` letters.

        Returns:
            One letter per move, so a path of ``n`` cells gives
            ``n - 1`` letters.

        Raises:
            MazeError: If two consecutive cells are not adjacent.

        ES — Devuelve el camino guardado como letras
        ``N``/``E``/``S``/``W``.

        Devuelve:
            Una letra por movimiento, de modo que un camino de ``n``
            celdas da ``n - 1`` letras.

        Lanza:
            MazeError: Si dos celdas consecutivas no son contiguas.
        """
        letters: list[str] = []
        for (x, y), (nx, ny) in zip(self._solution, self._solution[1:]):
            step = (nx - x, ny - y)
            for direction in Direction:
                if direction.delta == step:
                    letters.append(direction.letter)
                    break
            else:
                raise MazeError(
                    f"({x}, {y}) and ({nx}, {ny}) are not adjacent"
                )
        return "".join(letters)

    # ------------------------------------------------------------------
    # Export / Exportación
    # ------------------------------------------------------------------

    def cell_code(self, x: int, y: int) -> int:
        """Return the 4-bit code of ``(x, y)``, N=1, E=2, S=4, W=8.

        ES — Devuelve el código de 4 bits de ``(x, y)``: N=1, E=2, S=4,
        W=8.
        """
        code = 0
        for direction in Direction:
            if self.has_wall(x, y, direction):
                code |= direction.bit
        return code

    def to_hex_lines(self) -> list[str]:
        """Return the grid as one lowercase hex string per row.

        ES — Devuelve la rejilla como una cadena hexadecimal en
        minúsculas por cada fila.
        """
        return [
            "".join(
                f"{self.cell_code(x, y):x}" for x in range(self._width)
            )
            for y in range(self._height)
        ]

    def __repr__(self) -> str:
        """Return a short debugging representation.

        ES — Devuelve una representación corta para depuración.
        """
        return f"<Maze {self._width}x{self._height}>"
