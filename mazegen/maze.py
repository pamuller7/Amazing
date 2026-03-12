"""Core ``Maze`` class: initialisation, cell manipulation, and rendering."""

from mazegen.vector2 import Vector2
from mazegen.parse import CheckedConfig
from mazegen.graphics import drawings, themes, Colors, Theme
import time


class MazeGenerator:
    """A rectangular grid maze stored as a bit-encoded integer matrix.

    Each cell is an integer whose lower four bits represent the four walls
    (bit 0 = north, bit 1 = east, bit 2 = south, bit 3 = west).  A set
    bit means the wall is *present*; a cleared bit means the wall has been
    removed (i.e. there is a passage).  The special value ``0b11111``
    marks a decorative drawing cell that is excluded from path generation.
    Bits 5 and 6 are used by the solver to mark the solution path.

    Direction constants (used as bitmasks to open walls):

    * ``north`` = ``0b1110`` — clears bit 0
    * ``east``  = ``0b1101`` — clears bit 1
    * ``south`` = ``0b1011`` — clears bit 2
    * ``west``  = ``0b0111`` — clears bit 3

    Attributes:
        config: The validated configuration for this maze.
        north: Bitmask that opens the northern wall of a cell.
        east: Bitmask that opens the eastern wall of a cell.
        south: Bitmask that opens the southern wall of a cell.
        west: Bitmask that opens the western wall of a cell.
        nb_cell_to_fill: Number of cells still awaiting path generation.
        dir: Ordered list of the four direction constants.
        drawing: Pixel-art bitmap for the decorative centrepiece.
        theme: Active ``Theme`` used during terminal rendering.
        maze: The ``height x width`` integer matrix representing the maze.
    """

    def __init__(self, config: CheckedConfig) -> None:
        """Build and generate a new maze from *config*.

        Initialises the cell matrix (including the decorative drawing),
        then generates paths using either the Kruskal algorithm (when
        ``config.alt`` is ``True``) or the default random-walk ``Walker``.

        Args:
            config: Validated maze configuration.
        """
        from mazegen.brutal_path import Walker
        from mazegen.kruskal import Kruskal
        from mazegen.find_way import SolveMaze

        self.config = config
        self.north: int = 0b1110
        self.east: int = 0b1101
        self.south: int = 0b1011
        self.west: int = 0b0111
        self.nb_cell_to_fill: int = config.width * config.height
        self.dir: list = [self.north, self.west, self.south, self.east]
        self.drawing: list[list[int]] = drawings[config.drawing]
        self.theme: Theme = themes[config.theme]
        self.maze: list = self.init_maze()
        if self.config.alt:
            Kruskal.kruskal(self)
        else:
            walk = Walker(self)
            walk.walk_and_fill()
        content: str = self.print_maze("hex")
        content += f"Entry: {config.entry}\nExit: {config.exit}\n"
        solver = SolveMaze(self)
        content += solver.output_shortest_way()
        with open(self.config.output_file, "w") as f:
            f.write(content)

    def at(self, pos: Vector2) -> int:
        """Return the raw cell value at *pos*.

        Args:
            pos: Grid position (``pos.x`` = column, ``pos.y`` = row).

        Returns:
            The integer stored in ``self.maze[pos.y][pos.x]``.
        """
        value_cell: int = self.maze[pos.y][pos.x]
        return value_cell

    def set_cell(self, pos: Vector2, value: int) -> None:
        """Unconditionally overwrite the cell at *pos* with *value*.

        Args:
            pos: Grid position to update.
            value: New integer value for the cell.
        """
        self.maze[pos.y][pos.x] = value

    def is_in_bound(self, pos: Vector2) -> bool:
        """Return whether *pos* lies within the maze boundaries.

        Args:
            pos: Position to test (``pos.x`` = column, ``pos.y`` = row).

        Returns:
            ``True`` if ``0 <= pos.y < height`` and ``0 <= pos.x < width``.
        """
        cond: bool = (
            pos.y < self.config.height
            and pos.y >= 0
            and pos.x < self.config.width
            and pos.x >= 0
        )
        return cond

    def put_in_maze(self, pos: Vector2, value: int) -> None:
        """Open a wall of the cell at *pos* by ANDing its value with *value*.

        The operation is a no-op when *pos* is out of bounds or the cell is
        a drawing cell (``>= 0b11111``).

        Args:
            pos: Grid position whose wall will be opened.
            value: Direction bitmask (e.g. ``self.north``) to apply.
        """
        # casse le mur value a la position pos
        if self.is_in_bound(pos) and self.at(pos) < 0b11111:
            self.set_cell(pos, self.at(pos) & value)

    def init_maze(self) -> list[list[int]]:
        """Initialise the maze matrix with all walls intact and embed
        the drawing.

        Creates a ``height x width`` matrix filled with ``0b1111`` (all walls
        present).  If the maze is large enough, the configured decorative
        drawing is stamped into the centre by setting matching cells to
        ``0b11111`` (drawing sentinel) and decrementing ``nb_cell_to_fill``.

        Returns:
            The initialised ``height x width`` integer matrix.

        Raises:
            ValueError: If the entry or exit coordinate overlaps a
            drawing cell.
            MazeError: If ``width`` or ``height`` is not positive.
        """
        line_draw = len(self.drawing)
        col_draw = len(self.drawing[0])
        maze = [
            [0b1111 for _ in range(self.config.width)]
            for _ in range(self.config.height)
        ]
        can_draw = self.can_draw_42()
        if not can_draw:
            print(
                "ERROR:",
                "The maze is too small for the drawing to be printed",
            )
        for line in range(self.config.height):
            for col in range(self.config.width):
                if (
                    can_draw
                    and line >= int(self.config.height / 2 - line_draw / 2)
                    and line
                    < line_draw + int(self.config.height / 2 - line_draw / 2)
                    and col >= int(self.config.width / 2 - col_draw / 2)
                    and col
                    < col_draw + int(self.config.width / 2 - col_draw / 2)
                    and self.drawing[
                        line
                        - int(
                            self.config.height / 2 + line_draw - line_draw / 2
                        )
                    ][
                        col
                        - int(self.config.width / 2 + col_draw - col_draw / 2)
                    ]
                    == 1
                ):
                    if Vector2(col, line) == Vector2.from_iter(
                        self.config.entry
                    ):
                        raise ValueError(
                            "Entry = [{},{}] is in the drawing".format(
                                line, col
                            )
                        )
                    elif Vector2(col, line) == Vector2.from_iter(
                        self.config.exit
                    ):
                        raise ValueError(
                            "Exit = [{},{}] is in the drawing".format(
                                line, col
                            )
                        )
                    maze[line][col] = 0b11111
                    self.nb_cell_to_fill -= 1
        return maze

    def can_draw_42(self) -> bool:
        """Return whether the maze is large enough to display the drawing.

        Returns:
            ``True`` if the drawing fits with at least one cell of margin on
            every side.
        """
        return (
            len(self.drawing) <= self.config.height - 2
            and len(self.drawing[0]) <= self.config.width - 2
        )

    def print_maze(self, convert: str | None = None) -> str:
        """Render the maze and return any generated text content.

        When *convert* is ``"hex"``, the maze is serialised to a
        hexadecimal string (one character per cell) that is returned
        *without* printing to stdout.  For any other value the maze is
        rendered with ANSI colours directly to the terminal and an empty
        string is returned.

        Args:
            convert: Pass ``"hex"`` to produce hex output; otherwise
                any str to render the solver path in colour;
                omit (or pass ``None``) for a plain colour render.

        Returns:
            The hex-encoded maze string when *convert* is ``"hex"``; an
            empty string otherwise.
        """
        content = ""
        if convert == "hex":
            hexa = "0123456789ABCDEF"
            maze: list[list] = [[] for _ in range(self.config.height + 1)]
            for line in range(self.config.height):
                for col in range(self.config.width):
                    maze[line].append(hexa[self.maze[line][col] % 16])
            for tab in maze:
                for cell in tab:
                    content += cell
                content += "\n"
        else:
            print()
            for _ in range(self.config.width * 4 + 1):
                print(self.theme.wall_color + " " + Colors.ENDC.value, end="")
            print()
            for line in range(self.config.height):
                for middle in range(2):
                    print(
                        self.theme.wall_color + " " + Colors.ENDC.value, end=""
                    )
                    for col in range(self.config.width):
                        cell = self.maze[line][col]
                        if middle == 0:
                            if (col, line) == self.config.entry:
                                print(
                                    self.theme.entry_color
                                    + "En"
                                    + Colors.ENDC.value,
                                    end="",
                                )
                            elif (col, line) == self.config.exit:
                                print(
                                    self.theme.exit_color
                                    + "Ex"
                                    + Colors.ENDC.value,
                                    end="",
                                )
                            elif convert:
                                if cell >> 6 & 1 == 1:
                                    print(
                                        self.theme.tail_solver_color
                                        + "  "
                                        + Colors.ENDC.value,
                                        end="",
                                    )
                                elif cell >> 5 & 1 == 1:
                                    print(
                                        self.theme.head_solver_color
                                        + "  "
                                        + Colors.ENDC.value,
                                        end="",
                                    )
                                elif cell == 0b11111:
                                    print(
                                        self.theme.draw_color
                                        + "  "
                                        + Colors.ENDC.value,
                                        end="",
                                    )
                                else:
                                    print("  ", end="")
                            elif cell == 0b11111:
                                print(
                                    self.theme.tail_solver_color
                                    + "  "
                                    + Colors.ENDC.value,
                                    end="",
                                )
                            else:
                                print("  ", end="")
                            if cell >> 1 & 1 == 1:
                                print(
                                    self.theme.wall_color
                                    + "  "
                                    + Colors.ENDC.value,
                                    end="",
                                )
                            else:
                                if convert:
                                    if (
                                        (col, line) == self.config.entry
                                        and col + 1 < self.config.width
                                        and self.maze[line][col + 1] >> 6 & 1
                                        == 1
                                    ):
                                        print(
                                            self.theme.tail_solver_color
                                            + "  "
                                            + Colors.ENDC.value,
                                            end="",
                                        )
                                    elif (
                                        cell >> 6 & 1 == 1
                                        and col + 1 < self.config.width
                                        and self.maze[line][col + 1] >> 6 & 1
                                        == 1
                                    ):
                                        print(
                                            self.theme.tail_solver_color
                                            + "  "
                                            + Colors.ENDC.value,
                                            end="",
                                        )
                                    elif (
                                        cell >> 5 & 1 == 1
                                        and col + 1 < self.config.width
                                        and self.maze[line][col + 1] >> 5 & 1
                                        == 1
                                    ):
                                        print(
                                            self.theme.head_solver_color
                                            + "  "
                                            + Colors.ENDC.value,
                                            end="",
                                        )
                                    else:
                                        print("  ", end="")
                                else:
                                    print("  ", end="")

                        if middle == 1:
                            if cell >> 2 & 1 == 1:
                                print(
                                    self.theme.wall_color
                                    + "    "
                                    + Colors.ENDC.value,
                                    end="",
                                )
                                continue
                            elif convert:
                                if (
                                    (col, line) == self.config.entry
                                    and line + 1 < self.config.height
                                    and self.maze[line + 1][col] >> 6 & 1 == 1
                                ):
                                    print(
                                        self.theme.tail_solver_color
                                        + "  "
                                        + Colors.ENDC.value,
                                        end="",
                                    )
                                elif (
                                    cell >> 6 & 1 == 1
                                    and line + 1 < self.config.height
                                    and self.maze[line + 1][col] >> 6 & 1 == 1
                                ):
                                    print(
                                        self.theme.tail_solver_color
                                        + "  "
                                        + Colors.ENDC.value,
                                        end="",
                                    )
                                elif (
                                    cell >> 5 & 1 == 1
                                    and line + 1 < self.config.height
                                    and self.maze[line + 1][col] >> 5 & 1 == 1
                                ):
                                    print(
                                        self.theme.head_solver_color
                                        + "  "
                                        + Colors.ENDC.value,
                                        end="",
                                    )
                                else:
                                    print("  ", end="")
                            else:
                                print("  ", end="")
                            if cell >> 1 & 1 == 1:
                                print(
                                    self.theme.wall_color
                                    + "  "
                                    + Colors.ENDC.value,
                                    end="",
                                )
                            else:
                                if (
                                    line + 1 < self.config.height
                                    or col + 1 < self.config.width
                                ):
                                    if (
                                        line + 1 < self.config.height
                                        and col + 1 < self.config.width
                                    ):
                                        cell_bot = self.maze[line + 1][col]
                                        cell_col = self.maze[line][col + 1]
                                        if (
                                            cell_col >> 1 & 1 == 1
                                            and cell_bot >> 2 & 1 == 1
                                        ):
                                            print(
                                                self.theme.wall_color
                                                + "  "
                                                + Colors.ENDC.value,
                                                end="",
                                            )
                                        elif cell_bot >> 1 & 1 == 1:
                                            print(
                                                self.theme.wall_color
                                                + "  "
                                                + Colors.ENDC.value,
                                                end="",
                                            )
                                        elif cell_col >> 2 & 1 == 1:
                                            print(
                                                self.theme.wall_color
                                                + "  "
                                                + Colors.ENDC.value,
                                                end="",
                                            )
                                        else:
                                            print("  ", end="")
                                    else:
                                        print("  ", end="")
                                else:
                                    print("  ", end="")
                    print()
            print()
        return content

    def print_maze_on_terminal(
        self, msg: str, sleep: bool = True, convert: str | None = None
    ) -> None:
        """Move the cursor to the top of the terminal, print *msg*, then
        render the maze.

        Used during animation to redraw the maze in place without scrolling.
        An optional sleep proportional to the inverse of the largest
        dimension is inserted to pace the animation.

        Args:
            msg: Status message printed above the maze
            (e.g. ``"Generating..."``).
            sleep: When ``True``, pause briefly after rendering to create a
                smooth animation effect.
            convert: Forwarded to ``print_maze``; controls solver-path
                highlighting.
        """
        print("\033[H")
        if not self.can_draw_42():
            print("ERROR: The maze is too small to be printed")
        print(msg)
        self.print_maze(convert)
        if sleep:
            time.sleep(1 / ((max(self.config.height, self.config.width))))
