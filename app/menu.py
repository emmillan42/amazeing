"""Interactive loop driving the terminal display."""
from __future__ import annotations

from app.config_parser import Config
from mazegen.generator import MazeGenerator

MENU: str = (
    "=== A-Maze-ing ===\n"
    "1. Re-generate a new maze\n"
    "2. Show / Hide the shortest path\n"
    "3. Rotate the wall colours\n"
    "4. Save the maze on display to the output file\n"
    "5. Quit\n"
)


class Menu:
    """Draw a maze and let the user act on it.

    Attributes:
        generator: The generator producing the mazes.
        config: The configuration, needed to rewrite the output file
            after a new generation.
    """

    def __init__(
        self, generator: MazeGenerator, config: Config
    ) -> None:
        """Store the generator and start on the current maze."""
        self._generator = generator
        self._config = config
        self._show_path = False
        self._palette = 0

    def run(self) -> None:
        """Draw the maze, then loop until the user quits.

        Invalid choices, ``Ctrl+C`` and the end of the input stream are
        caught, so the program never ends on a traceback.
        """
        raise NotImplementedError

    def _regenerate(self) -> None:
        """Generate a new maze and display it.

        The output file is **not** touched: the evaluation sheet asks
        for the first generated maze to be the one stored there.
        Writing the maze on display is an explicit menu entry instead.
        """
        raise NotImplementedError

    def _save(self) -> None:
        """Write the maze currently on display to the output file."""
        raise NotImplementedError

    def _toggle_path(self) -> None:
        """Show or hide the shortest path."""
        raise NotImplementedError

    def _next_palette(self) -> None:
        """Switch to the next colour palette."""
        raise NotImplementedError
