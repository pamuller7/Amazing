# from mlx import Mlx
from typing import Optional
from enum import Enum
import time


class MazeError(Exception):
    pass


class Colors(Enum):
    BG_GREY = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_ORANGE = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_PURPULE = '\033[45m'
    BG_LIGHT_BLUE = '\033[46m'
    BG_WHITE = '\033[47m'
    WHITE = '\033[97m'
    LIGHT_BLUE = '\033[96m'
    PURPULE = '\033[95m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    GREY = '\033[90m'
    LIGHT_GREY = '\033[89m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class Maze:
    def __init__(
        self,
        height: int,
        width: int,
        entry: list,
        exit: list,
        output_file: str,
        perfect: bool,
        seed: Optional[int],
        animate_generation: Optional[bool] = False,
        animate_shortest_way: Optional[bool] = False,
        interactive: Optional[bool] = False,
        drawing: Optional[str] = "42",
        theme: Optional[str] = "squeleton"
    ) -> None:
        self.interactive = interactive
        self.anim_gen: bool = animate_generation
        self.anim_res: bool = animate_shortest_way
        self.seed: int = seed
        self.width: int = width
        self.height: int = height
        self.entry: list[int] = [entry[1], entry[0]]
        self.exit: list[int] = [exit[1], exit[0]]
        self.output_file: str = output_file
        self.perfect: bool = perfect
        self.north: int = 0b1110
        self.east: int = 0b1101
        self.south: int = 0b1011
        self.west: int = 0b0111
        self.nb_cell_to_fill: int = width * height
        self.dir: list = [self.north, self.west, self.south, self.east]
        self.draws: dict[list[list]] = {"42": [[1, 0, 0, 0, 1, 1, 1],
                                               [1, 0, 0, 0, 0, 0, 1],
                                               [1, 1, 1, 0, 1, 1, 1],
                                               [0, 0, 1, 0, 1, 0, 0],
                                               [0, 0, 1, 0, 1, 1, 1],
                                               ],
                                        "smiley": [[1, 1, 0, 0, 0, 1, 1],
                                                   [1, 1, 0, 0, 0, 1, 1],
                                                   [0, 0, 0, 0, 0, 0, 0],
                                                   [1, 0, 0, 0, 0, 0, 1],
                                                   [1, 1, 0, 0, 0, 1, 1],
                                                   [0, 1, 1, 1, 1, 1, 0]
                                                   ],
                                        "pac-man": [[0, 0, 1, 1, 1, 1, 1, 0],
                                                    [0, 1, 1, 1, 1, 1, 1, 1],
                                                    [1, 1, 1, 1, 1, 1, 1, 0],
                                                    [1, 1, 1, 1, 1, 0, 0, 0],
                                                    [1, 1, 1, 1, 0, 0, 0, 0],
                                                    [1, 1, 1, 1, 1, 0, 0, 0],
                                                    [1, 1, 1, 1, 1, 1, 1, 0],
                                                    [0, 1, 1, 1, 1, 1, 1, 1],
                                                    [0, 0, 1, 1, 1, 1, 1, 0]
                                                    ],
                                        "no_drawing": [[]]
                                        }
        self.drawing: list[list[int]] = self.draws[drawing]
        self.theme: dict = self.choose_theme(theme)
        self.maze: list = self.init_maze()

    def choose_theme(self, theme: str) -> dict:
        if theme == "red":
            return {
                "wall_color": Colors.RED.value + Colors.BOLD.value,
                "draw_color": Colors.YELLOW.value + Colors.BOLD.value,
                "entry_color": Colors.BG_GREEN.value,
                "head_solver_color": Colors.BG_RED.value,
                "tail_colver_color": Colors.BG_PURPULE.value,
                "exit_color": Colors.BG_RED.value
                }
        elif theme == "green":
            return {
                "wall_color": Colors.GREEN.value + Colors.BOLD.value,
                "draw_color": Colors.PURPULE.value + Colors.BOLD.value,
                "entry_color": Colors.BG_GREEN.value,
                "head_solver_color": Colors.BG_BLUE.value,
                "tail_colver_color": Colors.BG_LIGHT_BLUE.value,
                "exit_color": Colors.BG_RED.value
            }
        elif theme == "squeleton":
            return {
                "wall_color": Colors.WHITE.value + Colors.BOLD.value,
                "draw_color": Colors.LIGHT_GREY.value + Colors.BOLD.value,
                "entry_color": Colors.BG_GREEN.value,
                "head_solver_color": Colors.BG_GREY.value,
                "tail_colver_color": Colors.BG_LIGHT_BLUE.value,
                "exit_color": Colors.BG_RED.value
            }
        elif theme == "rgb":
            return {
                "wall_color": Colors.BLUE.value + Colors.BOLD.value,
                "draw_color": Colors.GREEN.value + Colors.BOLD.value,
                "entry_color": Colors.BG_GREEN.value,
                "head_solver_color": Colors.BG_GREEN.value,
                "tail_colver_color": Colors.BG_RED.value,
                "exit_color": Colors.BG_RED.value
            }

    def at(self, pos: list) -> int:
        value_cell: int = self.maze[pos[0]][pos[1]]
        return value_cell

    def is_in_bound(self, pos: list) -> bool:
        cond: bool = (pos[0] < self.height
                      and pos[0] >= 0
                      and pos[1] < self.width
                      and pos[1] >= 0)
        return (cond)

    def put_in_maze(self, pos: list, value: int) -> None:
        # casse le mur value a la position pos
        if self.is_in_bound(pos) and self.at(pos) < 0b11111:
            self.maze[pos[0]][pos[1]] = self.at(pos) & value

    def init_maze(self) -> list[list[int]]:
        """Init the maze, full of unexplored cells (only walls), and if
        possible draw the given drawing in the middle of the maze
        returns the maze created (a matrix (height, width))"""

        line_draw = len(self.drawing)
        col_draw = len(self.drawing[0])
        if self.width > 0 and self.height > 0:
            maze = [
                [0b1111 for _ in range(self.width)] for _ in range(self.height)
            ]
            can_draw = self.can_draw_42()
            if not can_draw:
                print("ERROR: The maze is too small to be printed")
            for line in range(self.height):
                for col in range(self.width):
                    if (
                        can_draw
                        and line >= int(self.height / 2 - line_draw / 2)
                        and line
                        < line_draw + int(self.height / 2 - line_draw / 2)
                        and col >= int(self.width / 2 - col_draw / 2)
                        and col < col_draw + int(self.width / 2 - col_draw / 2)
                        and self.drawing[
                            line
                            - int(self.height / 2 + line_draw - line_draw / 2)
                        ][col - int(self.width / 2 + col_draw - col_draw / 2)]
                        == 1
                    ):
                        if [line, col] == self.entry:
                            raise ValueError(f"Entry = [{line},{col}] \
is in the drawing")
                        elif [line, col] == self.exit:
                            raise ValueError(f"Exit = [{line},{col}] \
is in the drawing")
                        maze[line][col] = 0b11111
                        self.nb_cell_to_fill -= 1
        else:
            raise MazeError(
                "Invalid information:\
 width and height must be > 0"
            )
        return maze

    def can_draw_42(self) -> bool:
        """checks if the maze is tall enough to draw the drawing"""

        return (
            len(self.drawing) <= self.height - 2
            and len(self.drawing[0]) <= self.width - 2
        )

    def print_maze(self, convert: str | None = None) -> str:
        """print the maze
        convert:hex to print the maze in hexa (Mandatory)
                Nothing to print the maze in ascii"""
        content = ""
        wall_color = self.theme['wall_color']
        draw_color = self.theme['draw_color']
        entry_color = self.theme['entry_color']
        head_solver_color = self.theme['head_solver_color']
        tail_colver_color = self.theme['tail_colver_color']
        exit_color = self.theme['exit_color']
        if convert == "hex":
            hexa = [
                "0",
                "1",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
                "A",
                "B",
                "C",
                "D",
                "E",
                "F",
            ]
            maze: list[list] = [[] for _ in range(self.height + 1)]
            for line in range(self.height):
                for col in range(self.width):
                    maze[line].append(hexa[self.maze[line][col] % 16])
            for tab in maze:
                for cell in tab:
                    content += (cell)
                content += ("\n")
        else:
            print(" ", end="")
            for _ in range(self.width):
                print(wall_color + "__" + Colors.ENDC.value, end="")
            print(wall_color + "\n" + Colors.ENDC.value, end="")
            for line in range(self.height):
                print(Colors.ENDC.value + wall_color + "|"
                      + Colors.ENDC.value, end="")
                for col in range(self.width):
                    cell = self.maze[line][col]
                    if cell == 0b11111:
                        print(draw_color + "##" +
                              Colors.ENDC.value, end="")
                    else:
                        if [line, col] == self.entry:
                            print(entry_color, end="")
                        if not convert:
                            if cell >> 6 & 1 == 1:
                                print(tail_colver_color, end="")
                            elif cell >> 5 & 1 == 1:
                                print(head_solver_color, end="")
                        if [line, col] == self.exit:
                            print(exit_color, end="")
                        if (cell >> 2) & 1 == 1:
                            print(wall_color + "_", end="")
                        else:
                            print(wall_color + " ", end="")
                        if cell >> 1 & 1 == 1:
                            print(Colors.ENDC.value + wall_color
                                  + "|" + Colors.ENDC.value, end="")
                        else:
                            if (cell >> 2) & 1 == 1:
                                print(wall_color
                                      + "_" + Colors.ENDC.value, end="")
                            else:
                                print(wall_color
                                      + " " + Colors.ENDC.value, end="")
                print("\n", end="")
            print(" ", end="")
            print("\n", end="")
        return content

    def draw_maze(self) -> None:
        draw_line = len(self.drawing)
        draw_col = len(self.drawing)
        can_draw = self.can_draw_42()
        for line in range(self.height):
            for col in range(self.width):
                # dessine le 42 pendant le parcours du tableau
                if (
                    can_draw
                    and line >= int(self.height / 2) - int(draw_line/2)
                    and line < len(self.drawing) +
                    int(self.height / 2) - int(draw_line/2)
                    and col >= int(self.width / 2) - int(draw_col/2)
                    and col < len(self.drawing[0]) +
                    int(self.width / 2) - int(draw_col/2)
                    and self.drawing[line - int(self.height / 2) +
                                     draw_line - int(draw_line/2)][
                        col - int(self.width / 2) + draw_col - int(draw_col/2)
                    ]
                    == 1
                ):
                    if [line, col] == self.entry:
                        raise ValueError("Entry can't be in the 42 pattern")
                    if [line, col] == self.exit:
                        raise ValueError("Exit can't be in the 42 pattern")
                    self.maze[line][col] = 0b11111

    def print_maze_on_terminal(self, msg: str):
        print("\033[H")
        if not self.can_draw_42():
            print("ERROR: The maze is too small to be printed")
        print(msg)
        self.print_maze()
        time.sleep(1 / ((max(self.height, self.width))))
