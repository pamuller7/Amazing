from source.vector2 import Vector2
from source.parse import CheckedConfig
from source.graphics import drawings, themes, Colors, Theme
import time


class MazeError(Exception):
    pass


class Maze:
    def __init__(self, config: CheckedConfig) -> None:
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

    def at(self, pos: Vector2) -> int:
        value_cell: int = self.maze[pos.y][pos.x]
        return value_cell

    def set_cell(self, pos: Vector2, value: int):
        self.maze[pos.y][pos.x] = value

    def is_in_bound(self, pos: Vector2) -> bool:
        cond: bool = (
            pos.y < self.config.height
            and pos.y >= 0
            and pos.x < self.config.width
            and pos.x >= 0
        )
        return cond

    def put_in_maze(self, pos: Vector2, value: int) -> None:
        # casse le mur value a la position pos
        if self.is_in_bound(pos) and self.at(pos) < 0b11111:
            self.set_cell(pos, self.at(pos) & value)

    def init_maze(self) -> list[list[int]]:
        """Init the maze, full of unexplored cells (only walls), and if
        possible draw the given drawing in the middle of the maze
        returns the maze created (a matrix (height, width))"""

        line_draw = len(self.drawing)
        col_draw = len(self.drawing[0])
        if self.config.width > 0 and self.config.height > 0:
            maze = [
                [0b1111 for _ in range(self.config.width)]
                for _ in range(self.config.height)
            ]
            can_draw = self.can_draw_42()
            for line in range(self.config.height):
                for col in range(self.config.width):
                    if (
                        can_draw
                        and line >= int(self.config.height / 2 - line_draw / 2)
                        and line
                        < line_draw
                        + int(self.config.height / 2 - line_draw / 2)
                        and col >= int(self.config.width / 2 - col_draw / 2)
                        and col
                        < col_draw + int(self.config.width / 2 - col_draw / 2)
                        and self.drawing[
                            line
                            - int(
                                self.config.height / 2
                                + line_draw
                                - line_draw / 2
                            )
                        ][
                            col
                            - int(
                                self.config.width / 2 + col_draw - col_draw / 2
                            )
                        ]
                        == 1
                    ):
                        if [line, col] == self.config.entry:
                            raise ValueError(
                                "Entry = [{},{}] is in the drawing".format(
                                    line, col
                                )
                            )
                        elif [line, col] == self.config.exit:
                            raise ValueError(
                                "Exit = [{},{}] is in the drawing".format(
                                    line, col
                                )
                            )
                        maze[line][col] = 0b11111
                        self.nb_cell_to_fill -= 1
        else:
            raise MazeError("Invalid information:\
 width and height must be > 0")
        return maze

    def can_draw_42(self) -> bool:
        """checks if the maze is tall enough to draw the drawing"""

        return (
            len(self.drawing) <= self.config.height - 2
            and len(self.drawing[0]) <= self.config.width - 2
        )

    def print_maze(self, convert: str | None = None) -> str:
        """print the maze
        convert:hex to print the maze in hexa (Mandatory)
                Nothing to print the maze in ascii"""
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
            print(" ", end="")
            for _ in range(self.config.width):
                print(self.theme.wall_color + "__" + Colors.ENDC.value, end="")
            print(self.theme.wall_color + "\n" + Colors.ENDC.value, end="")
            for line in range(self.config.height):
                print(
                    Colors.ENDC.value
                    + self.theme.wall_color
                    + "|"
                    + Colors.ENDC.value,
                    end="",
                )
                for col in range(self.config.width):
                    cell = self.maze[line][col]
                    if cell == 0b11111:
                        print(
                            self.theme.draw_color + "##" + Colors.ENDC.value,
                            end="",
                        )
                    else:
                        if (col, line) == self.config.entry:
                            print(self.theme.entry_color, end="")
                        if not convert:
                            if cell >> 6 & 1 == 1:
                                print(self.theme.tail_solver_color, end="")
                            elif cell >> 5 & 1 == 1:
                                print(self.theme.head_solver_color, end="")
                        if (col, line) == self.config.exit:
                            print(self.theme.exit_color, end="")
                        if (cell >> 2) & 1 == 1:
                            print(self.theme.wall_color + "_", end="")
                        else:
                            print(self.theme.wall_color + " ", end="")
                        if cell >> 1 & 1 == 1:
                            print(
                                Colors.ENDC.value
                                + self.theme.wall_color
                                + "|"
                                + Colors.ENDC.value,
                                end="",
                            )
                        else:
                            if (cell >> 2) & 1 == 1:
                                print(
                                    self.theme.wall_color
                                    + "_"
                                    + Colors.ENDC.value,
                                    end="",
                                )
                            else:
                                print(
                                    self.theme.wall_color
                                    + " "
                                    + Colors.ENDC.value,
                                    end="",
                                )
                print("\n", end="")
            print(" ", end="")
            print("\n", end="")
        return content

    def draw_maze(self) -> None:
        draw_line = len(self.drawing)
        draw_col = len(self.drawing)
        can_draw = self.can_draw_42()
        for line in range(self.config.height):
            for col in range(self.config.width):
                # dessine le 42 pendant le parcours du tableau
                if (
                    can_draw
                    and line
                    >= int(self.config.height / 2) - int(draw_line / 2)
                    and line
                    < len(self.drawing)
                    + int(self.config.height / 2)
                    - int(draw_line / 2)
                    and col >= int(self.config.width / 2) - int(draw_col / 2)
                    and col
                    < len(self.drawing[0])
                    + int(self.config.width / 2)
                    - int(draw_col / 2)
                    and self.drawing[
                        line
                        - int(self.config.height / 2)
                        + draw_line
                        - int(draw_line / 2)
                    ][
                        col
                        - int(self.config.width / 2)
                        + draw_col
                        - int(draw_col / 2)
                    ]
                    == 1
                ):
                    if (col, line) == self.config.entry:
                        raise ValueError("Entry can't be in the 42 pattern")
                    if [line, col] == self.config.exit:
                        raise ValueError("Exit can't be in the 42 pattern")
                    self.maze[line][col] = 0b11111

    def print_maze_on_terminal(self, msg: str):
        print("\033[H")
        print(msg)
        self.print_maze()
        time.sleep(1 / ((max(self.config.height, self.config.width))))
