"""Interactive loop driving the terminal display."""
from __future__ import annotations

from collections.abc import Callable

from app.config_parser import Config
from app.renderer import PALETTES, render
from app.writer import write_maze
from mazegen.errors import MazeError
from mazegen.generator import MazeGenerator

CLEAR: str = "\033[H\033[J"
"""Move the cursor home and clear the screen."""

QUIT: str = "5"


class Menu:
    """Draw a maze and let the user act on it."""

    def __init__(
        self,
        generator: MazeGenerator,
        config: Config,
        *,
        notice: str = "",
    ) -> None:
        """Store the generator and start on its current maze.

        Args:
            generator: The generator producing the mazes, already used
                once: the menu starts on the maze it holds.
            config: The configuration, needed to save the maze on
                display.
            notice: A line shown on every screen, under the maze.  The
                entry point uses it for the "42 does not fit" warning:
                printed only before the menu, the first screen clear
                would erase it (ADR-030).

        Raises:
            GenerationError: If the generator has not generated yet.
        """
        self._generator = generator
        self._config = config
        self._maze = generator.maze
        self._show_path = False
        self._palette = 0
        self._notice = notice
        self._message = ""
        self._actions: dict[str, Callable[[], None]] = {
            "1": self._regenerate,
            "2": self._toggle_path,
            "3": self._next_palette,
            "4": self._save,
        }

    def run(self) -> None:
        """Draw the maze, then loop until the user quits.

        Invalid choices, ``Ctrl+C`` and the end of the input stream are
        caught, so the program never ends on a traceback.  Bytes that
        are not UTF-8 count as an invalid choice: with a UTF-8 locale
        Python decodes the keyboard strictly, and ``input`` raises.
        """
        while True:
            print(self._frame())
            try:
                choice = input("Choice (1-5): ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                return
            except UnicodeDecodeError:
                self._message = "unreadable input (not UTF-8), pick 1 to 5"
                continue
            if choice == QUIT:
                return
            action = self._actions.get(choice)
            if action is None:
                self._message = f"unknown choice {choice!r}, pick 1 to 5"
            else:
                self._message = ""
                action()

    def _frame(self) -> str:
        """Return the screen: clear, maze, notice, message and options.

        The notice stays on every screen; the message only lasts until
        the next choice.  Without either, the layout is the same as
        before the notice existed: one empty line under the maze.
        """
        palette = PALETTES[self._palette]
        shown = "shown" if self._show_path else "hidden"
        status = [line for line in (self._notice, self._message) if line]
        return (
            CLEAR
            + render(self._maze, self._show_path, palette) + "\n\n"
            + "".join(f"{line}\n" for line in status)
            + "=== A-Maze-ing ===\n"
            + "1. Re-generate a new maze\n"
            + f"2. Show / hide the shortest path (now {shown})\n"
            + f"3. Change the wall colours (now {palette.name})\n"
            + f"4. Save this maze to {self._config.output_file}\n"
            + "5. Quit"
        )

    def _regenerate(self) -> None:
        """Generate a new maze and display it.

        The output file is **not** touched: the evaluation sheet asks
        for the first generated maze to be the one stored there
        (ADR-009).  Writing the maze on display is :meth:`_save`.
        """
        self._maze = self._generator.generate()
        self._message = "new maze generated (not saved, use 4 to save it)"

    def _save(self) -> None:
        """Write the maze currently on display to the output file.

        A failure is shown in the menu instead of ending the program:
        the user can still look at the maze or quit normally.
        """
        try:
            write_maze(self._config.output_file, self._maze)
        except MazeError as error:
            self._message = f"error: {error}"
            return
        self._message = f"maze saved to {self._config.output_file}"

    def _toggle_path(self) -> None:
        """Show or hide the shortest path."""
        self._show_path = not self._show_path

    def _next_palette(self) -> None:
        """Switch to the next colour palette."""
        self._palette = (self._palette + 1) % len(PALETTES)
