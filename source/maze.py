from mlx import Mlx
from typing import Any


class MazeError(Exception):
    pass


class Maze:
    def __init__(
        self,
        height: int,
        width: int,
        entry: list,
        exit: list,
        output_file: str,
        perfect: bool,
        cell_size: int = 50,
    ) -> None:
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.output_file = output_file
        self.perfect = perfect
        self.north = 0b1110
        self.east = 0b1101
        self.south = 0b1011
        self.west = 0b0111
        self.nb_cell_to_fill = width * height
        self.dir: list = [self.north,
                          self.west,
                          self.south,
                          self.east]
        self.drawing: list = [[1, 0, 0, 0, 1, 1, 1],
                              [1, 0, 0, 0, 0, 0, 1],
                              [1, 1, 1, 0, 1, 1, 1],
                              [0, 0, 1, 0, 1, 0, 0],
                              [0, 0, 1, 0, 1, 1, 1]]
        self.maze: list = self.init_maze()

        def check_open_area(self, pos: list):
            i = pos[0]
            j = pos[0]
            if (
                i > 0 and j > 0
                and i < self.height - 1 and j < self.width - 1
            ):
                weigth_square = 0
                for x in range(-1, 2):
                    for y in range(-1, 2):
                        weigth_square += self.maze[i+x][j+y]

    def is_in_bound(self, pos: list) -> bool:
        '''checks if the current position pos is not outside the maze
            pos: list of coords we want to check'''

        return (pos[0] < self.height and pos[0] >= 0
                and pos[1] < self.width and pos[1] >= 0)

    def put_in_maze(self, pos: list, value: int) -> None:
        '''put the wanted wall (value) at the position pos in maze'''

        line = pos[0]
        col = pos[1]
        if self.is_in_bound(pos) and self.maze[line][col] < 0b11111:
            self.maze[line][col] = self.maze[line][col] & value

    def init_maze(self) -> list[list[int]]:
        '''Init the maze, full of unexplored cells (only walls), and if
        possible draw the given drawing in the middle of the maze
        returns the maze created (a matrix (height, width))'''

        line_draw = len(self.drawing)
        col_draw = len(self.drawing[0])
        if self.width > 0 and self.height > 0:
            maze = [[0b1111 for _ in range(self.width)]
                    for _ in range(self.height)]
            can_draw = self.can_draw_42()
            for line in range(self.height):
                for col in range(self.width):
                    if (
                        can_draw
                        and line >= int(self.height/2 - line_draw/2)
                        and line < line_draw + int(self.height/2 - line_draw/2)
                        and col >= int(self.width/2 - col_draw/2)
                        and col < col_draw + int(self.width/2 - col_draw/2)
                        and self.drawing[line - int(self.height/2 + line_draw - line_draw/2)]
                        [col - int(self.width/2 + col_draw - col_draw/2)] == 1
                    ):
                        maze[line][col] = 0b11111
                        self.nb_cell_to_fill -= 1
        else:
            raise MazeError("Invalid information:\
 width and height must be > 0")
        return (maze)

    def can_draw_42(self) -> bool:
        '''checks if the maze is tall enough to draw the drawing'''

        return (
            len(self.drawing) <= self.height - 2
            and len(self.drawing[0]) <= self.width - 2
        )
 
    def print_maze(self, convert: str | None = None) -> str:
        '''print the maze
            convert:hex to print the maze in hexa (Mandatory)
                    Nothing to print the maze in ascii'''
        content = ""
        if convert == "hex":
            hexa = ['0', '1', '2', '3', '4',
                    '5', '6', '7', '8', '9',
                    'A', 'B', 'C', 'D', 'E', 'F']
            maze = [[] for _ in range(self.height + 1)]
            for line in range(self.height):
                for col in range(self.width):
                    maze[line].append(hexa[self.maze[line][col] % 16])
            for line in maze:
                for cell in line:
                    content += (cell)
                content += ("\n")
        else:
            content += (" ")
            for _ in range(self.width):
                content += ("__")
            content += ("\n")
            for line in range(self.height):
                content += ("|")
                for col in range(self.width):
                    cell = self.maze[line][col]
                    if cell == 0b11111:
                        content += ("##")
                    elif cell == 98:
                        content += ("++")
                    else:
                        if (cell >> 2) & 1 == 1:
                            content += ("_")
                        else:
                            content += (" ")
                        if cell >> 1 & 1 == 1:
                            content += ("|")
                        else:
                            if (cell >> 2) & 1 == 1:
                                content += ("_")
                            else:
                                content += (" ")
                content += ("\n")
            content += (" ")
            content += ("\n")
        return (content)

    def draw_maze(self) -> None:
        can_draw = self.can_draw_42()
        for line in range(self.height):
            for col in range(self.width):
                # dessine le 42 pendant le parcours du tableau
                if (
                    can_draw
                    and line >= int(self.height / 2) - 3
                    and line < len(self.drawing) + int(self.height / 2) - 3
                    and col >= int(self.width / 2) - 3
                    and col < len(self.drawing[0]) + int(self.width / 2) - 3
                    and self.drawing[line - int(self.height / 2) + 3][
                        col - int(self.width / 2) + 3
                    ]
                    == 1
                ):
                    self.maze[line][col] = 0b11111
                # choisist un nombre dedirection au hasard, casse les murs
        # walker = Walker()
        # walker.walk()

    def to_background_image(self, m: Mlx, img_ptr: Any):
        data, _, line_size, format = m.mlx_get_data_addr(img_ptr)
        for line in range(self.height * self.cell_size):
            for col in range(self.width * self.cell_size):
                r, g, b, a = 100, 100, 200, 254
                if 2 * 100 <= col <= 4 * 100 and 2 * 100 <= line <= 4 * 100:
                    r, g, b, a = 255, 0, 0, 254
                if format == 0:
                    data[4 * col + line * line_size] = b
                    data[4 * col + line * line_size + 1] = g
                    data[4 * col + line * line_size + 2] = r
                    data[4 * col + line * line_size + 3] = a
                else:
                    data[4 * col + line * line_size] = a
                    data[4 * col + line * line_size + 1] = r
                    data[4 * col + line * line_size + 2] = g
                    data[4 * col + line * line_size + 3] = b

    def to_image(self, m: Mlx, img_ptr: Any):
        data, _, line_size, format = m.mlx_get_data_addr(img_ptr)
        self.to_background_image(m, img_ptr)

        def write_line(start, incr, color=(0, 0, 0, 255)):
            for _ in range(self.cell_size):
                r, g, b, a = color
                print(start)
                if format == 0:
                    data[start] = b
                    data[start + 1] = g
                    data[start + 2] = r
                    data[start + 3] = a
                else:
                    data[start] = a
                    data[start + 1] = r
                    data[start + 2] = g
                    data[start + 3] = b
                start += incr

        for line in range(self.height):
            for col in range(self.width):
                if self.maze[line][col] & 0b1000:
                    write_line(
                        self.cell_size * 4 * col
                        + self.cell_size * line_size * line,
                        4,
                    )
                if self.maze[line][col] & 0b0100:
                    write_line(
                        self.cell_size * 4 * (col + 1)
                        + self.cell_size * line_size * line,
                        line_size,
                    )
                if self.maze[line][col] & 0b0010:
                    write_line(
                        self.cell_size * 4 * col
                        + self.cell_size * line_size * (line + 1)
                        - line_size,
                        4,
                    )
                if self.maze[line][col] & 0b0001:
                    write_line(
                        self.cell_size * 4 * (col)
                        + self.cell_size * line_size * line,
                        line_size,
                    )
