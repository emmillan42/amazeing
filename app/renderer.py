# class Direction:
#     NORTH = 0
#     EAST = 1
#     SOUTH = 2
#     WEST = 3


# class Maze:
#     def __init__(self) -> None:
#         self.width = 4
#         self.height = 4
#         self.entry = (0, 0)
#         self.exit = (2, 2)
#         self.blocked = [(1, 1)]
#         self.solution = [
#             (0, 0),
#             (1, 0),
#             (2, 0),
#             (2, 1),
#             (2, 2)
#         ]

#     def has_wall(self, x: int, y: int, direction: int) -> bool:
#         return True

#     def to_hex_lines(self) -> list[str]:
#         return ["953", "c56", "957"]

#     def solution_string(self) -> str:
#         return "EESS"


# def get_dummy_maze():
#     return Maze()


PALETTES = {
    "default": {
        "reset": "\033[0m",
        "entry": "\033[92m",
        "exit": "\033[91m",
        "path": "\033[93m",
        "wall": "\033[34m",
        "blocked": "\033[90m"
    },
    "neon": {
        "reset": "\033[0m",
        "entry": "\033[90m",
        "exit": "\033[34m",
        "path": "\033[96m",
        "wall": "\033[92m",
        "blocked": "\033[91m"
    }
}


def _render_h_wall(maze: Maze, x: int, y: int, colors: dict) -> str:
    if maze.has_wall(x, y, Direction.NORTH):
        return (f"{colors['wall']}---{colors['reset']}")
    else:
        return ("   ")


def _render_v_wall(maze: Maze, x: int, y: int, colors: dict) -> str:
    if maze.has_wall(x, y, Direction.WEST):
        return (f"{colors['wall']}|{colors['reset']}")
    else:
        return (" ")


def _render_cell_content(
        maze: Maze, x: int, y: int, show_path: bool, colors: dict
) -> str:
    if (x, y) in maze.blocked:
        return (f"{colors['blocked']}███{colors['reset']}")
    elif (x, y) == maze.entry:
        return (f"{colors['entry']} E {colors['reset']}")
    elif (x, y) == maze.exit:
        return (f"{colors['exit']} X {colors['reset']}")
    elif show_path and (x, y) in maze.solution:
        return (f"{colors['path']} ● {colors['reset']}")
    else:
        return ("   ")


def render(
        maze: Maze, show_path: bool = False, palette: str = "default"
) -> str:
    colors = PALETTES.get(palette, PALETTES["default"])

    lines = []
    for y in range(0, maze.height - 1):
        up_string = ""
        for x in range(0, maze.width - 1):
            up_string += f"{colors['wall']}+{colors['reset']}"
            up_string += _render_h_wall(maze, x, y, colors)
        up_string += f"{colors['wall']}+{colors['reset']}"
        lines.append(up_string)

        low_string = ""
        for x in range(0, maze.width - 1):
            low_string += _render_v_wall(maze, x, y, colors)
            low_string += _render_cell_content(maze, x, y, show_path, colors)
        low_string += f"{colors['wall']}|{colors['reset']}"
        lines.append(low_string)

    last_string = ""
    for x in range(0, maze.width - 1):
        last_string += f"{colors['wall']}+---{colors['reset']}"
    last_string += f"{colors['wall']}+{colors['reset']}"
    lines.append(last_string)

    return ("\n".join(lines))


# print(render(get_dummy_maze(), True, "default"))
