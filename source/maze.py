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
            if not can_draw:
                print("ERROR: The maze is too small to be printed")
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
            print()
            for _ in range(self.config.width * 4 + 1):
                print(self.theme.wall_color + " "
                      + Colors.ENDC.value, end="")
            print()
            for line in range(self.config.height):
                for middle in range(2):
                    print(self.theme.wall_color + " "
                          + Colors.ENDC.value, end="")
                    for col in range(self.config.width):
                        cell = self.maze[line][col]
                        if middle == 0:
                            if (col, line) == self.config.entry:
                                print(self.theme.entry_color + "En"
                                      + Colors.ENDC.value, end="")
                            elif (col, line) == self.config.exit:
                                print(self.theme.exit_color + "Ex"
                                      + Colors.ENDC.value, end="")
                            elif convert:
                                if cell >> 6 & 1 == 1:
                                    print(self.theme.tail_solver_color
                                          + "  " + Colors.ENDC.value, end="")
                                elif cell >> 5 & 1 == 1:
                                    print(self.theme.head_solver_color
                                          + "  " + Colors.ENDC.value, end="")
                                elif cell == 0b11111:
                                    print(self.theme.draw_color
                                          + "  " + Colors.ENDC.value, end="")
                                else:
                                    print("  ", end="")
                            elif cell == 0b11111:
                                print(self.theme.tail_solver_color
                                      + "  " + Colors.ENDC.value, end="")
                            else:
                                print("  ", end="")
                            if cell >> 1 & 1 == 1:
                                print(self.theme.wall_color
                                      + "  " + Colors.ENDC.value, end="")
                            else:
                                if convert:
                                    if (
                                        (col, line) == self.config.entry
                                        and col + 1 < self.config.width
                                        and self.maze[line]
                                        [col + 1] >> 6 & 1 == 1
                                    ):
                                        print(self.theme.tail_solver_color
                                              + "  " + Colors.ENDC.value,
                                              end="")
                                    elif (
                                        cell >> 6 & 1 == 1
                                        and col + 1 < self.config.width
                                        and self.maze[line]
                                        [col + 1] >> 6 & 1 == 1
                                    ):
                                        print(self.theme.tail_solver_color
                                              + "  " + Colors.ENDC.value,
                                              end="")
                                    elif (
                                        cell >> 5 & 1 == 1
                                        and col + 1 < self.config.width
                                        and self.maze[line]
                                        [col + 1] >> 5 & 1 == 1
                                    ):
                                        print(self.theme.head_solver_color
                                              + "  " + Colors.ENDC.value,
                                              end="")
                                    else:
                                        print("  ", end="")
                                else:
                                    print("  ", end="")

                        if middle == 1:
                            if cell >> 2 & 1 == 1:
                                print(self.theme.wall_color
                                      + "    " + Colors.ENDC.value, end="")
                                continue
                            elif convert:
                                if (
                                    (col, line) == self.config.entry
                                    and line + 1 < self.config.height
                                    and self.maze[line + 1][col] >> 6 & 1 == 1
                                ):
                                    print(self.theme.tail_solver_color
                                          + "  " + Colors.ENDC.value, end="")
                                elif (
                                    cell >> 6 & 1 == 1
                                    and line + 1 < self.config.height
                                    and self.maze[line + 1]
                                    [col] >> 6 & 1 == 1
                                ):
                                    print(self.theme.tail_solver_color
                                          + "  " + Colors.ENDC.value, end="")
                                elif (
                                    cell >> 5 & 1 == 1
                                    and line + 1 < self.config.height
                                    and self.maze[line + 1]
                                    [col] >> 5 & 1 == 1
                                ):
                                    print(self.theme.head_solver_color
                                          + "  " + Colors.ENDC.value, end="")
                                else:
                                    print("  ", end="")
                            else:
                                print("  ", end="")
                            if cell >> 1 & 1 == 1:
                                print(self.theme.wall_color
                                      + "  " + Colors.ENDC.value, end="")
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
                                            print(self.theme.wall_color
                                                  + "  " + Colors.ENDC.value,
                                                  end="")
                                        elif cell_bot >> 1 & 1 == 1:
                                            print(self.theme.wall_color
                                                  + "  " + Colors.ENDC.value,
                                                  end="")
                                        elif cell_col >> 2 & 1 == 1:
                                            print(self.theme.wall_color
                                                  + "  " + Colors.ENDC.value,
                                                  end="")
                                        else:
                                            print(" ", end="")
                                    else:
                                        print("  ", end="")
                                else:
                                    print("  ", end="")
                    print()
            print()
        return content

    def print_maze_on_terminal(self, msg: str, sleep=True):
        print("\033[H")
        if not self.can_draw_42():
            print("ERROR: The maze is too small to be printed")
        print(msg)
        self.print_maze()
        if sleep:
            time.sleep(1 / ((max(self.config.height, self.config.width))))
