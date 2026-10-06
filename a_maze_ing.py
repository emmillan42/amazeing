import sys


def amazeing() -> None:
    if len(sys.argv) != 2:
        sys.stderr.write("Uso: python3 a_maze_ing.py config.txt\n")
        sys.exit(1)

    try:
        config = parse_config(sys.argv[1])

        generator = MazeGenerator(
            width=config.width,
            height=config.height,
            entry=config.entry,
            exit=config.exit,
            perfect=config.perfect,
            seed=config.seed,
            algorithm=config.algorithm,
            pattern=config.pattern,
        )
        maze = generator.generate()

        if generator.pattern_skipped:
            sys.stderr.write(
                "Aviso: El laberinto es demasiado pequeño, se omitirá "
                "el patrón '42'.\n"
            )

        write_maze(config.outout_file, maze)

        run_menu(maze, generator)

    except MazeError as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    amazeing()
