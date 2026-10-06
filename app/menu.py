
def run_menu(maze: Maze, generator: MazeGenerator | None = None) -> None:
    show_path = False
    current_palette = "default"
    palettes = ["default", "neon"]
    current_maze = maze

    while True:
        try:
            print("\033[H\033[J", end="")
            print(render(current_maze, show_path, current_palette))
            print(
                "========================================\n"
                "              A-MAZE-ING\n"
                "========================================"
            )
            print(
                f" [1] Regenerar laberinto\n"
                f" [2] Mostrar / Ocultar camino solución "
                f"(Estado: {show_path})\n"
                f" [3] Cambiar paleta de colores "
                f"(Actual: '{current_palette}')\n"
                f" [4] Salir"
            )
            print("========================================")

            choice = input("Elige una opción (1-4): ")

            if choice == "1":
                if generator is not None:
                    current_maze = generator.generate()
                continue

            elif choice == "2":
                show_path = not show_path

            elif choice == "3":
                print("\033[H\033[J", end="")

                num_palettes = len(palettes)

                for i in range(0, num_palettes):
                    print(f" [{i}] {palettes[i]}")

                choice_2 = input(f"Elige una paleta (0-{num_palettes-1}): ")

                if choice_2.isdigit() and int(choice_2) in range(num_palettes):
                    current_palette = palettes[int(choice_2)]

            elif choice == "4":
                print("\n¡Gracias por jugar a A-Maze-ing!\n")
                break

        except (KeyboardInterrupt, EOFError):
            print("\n¡Hasta luego!\n")
            break


# run_menu(get_dummy_maze())
