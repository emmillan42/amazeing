from mazegen.errors import MazeError
from mazegen.maze import Maze

def write_maze(path: str, maze: Maze) -> None:
    try:
        with open(path, "w") as f:
            hex_list = maze.to_hex_lines()
            joint_hex = "\n".join(hex_list)
            f.write(f"{joint_hex}\n")

            f.write(f"{maze.entry}\n")
            f.write(f"{maze.exit}\n")
            
            sol = maze.solution_string()
            f.write(f"{sol}")

    except OSError as e:
        raise MazeError(f"No se pudo escribir el archivo de salida '{path}': {e}")
