
class MazeError(Exception):
    pass


class Maze:
    def __init__(self, height: int, width: int,
                 entry: list, exit: list,
                 output_file: str, perfect: bool) -> None:
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.output_file = output_file
        self.perfect = perfect
        self.maze: list = []
        self.north = 0b0111
        self.east = 0b1011
        self.south = 0b1101
        self.west = 0b1110
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

    def print_maze(self, convert: str | None = None) -> None:
        if convert and convert != "yes" and convert != "hex":
            if convert == "bin":
                func = bin
            elif convert == "int":
                func = int
            for col in self.maze:
                for cell in col:
                    print(func(cell), end="\t")
                    if (cell) <= 15:
                        print("\t", end="")
                print()
        elif convert == "hex":
            hexa = ['0', '1', '2', '3', '4',
                    '5', '6', '7', '8', '9',
                    'A', 'B', 'C', 'D', 'E', 'F']
            maze = [[] for _ in range(self.height + 1)]
            for line in range(self.height):
                for col in range(self.width):
                    maze[line].append(hexa[self.maze[line][col] % 16])
            for line in maze:
                for cell in line:
                    print(cell, end="")
                print()

        else:
            maze = [[] for _ in range(self.height + 1)]
            # affiche le tableau version joli
            maze[0].append(" ")
            for i in range(self.width):
                maze[0].append("__")
            for line in range(1, self.height):
                maze[line].append("|")
                for col in range(self.width):
                    cell = self.maze[line][col]
                    if cell == 0b11111:
                        maze[line].append("##")
                    elif cell == 98:
                        maze[line].append("++", end="")
                    else:
                        if (cell >> 1) & 1 == 1:
                            maze[line].append("_")
                        else:
                            maze[line].append(" ")
                        if cell >> 2 & 1 == 1:
                            maze[line].append("|")
                        else:
                            if (cell >> 1) & 1 == 1:
                                maze[line].append("_")
                            else:
                                maze[line].append(" ")
            if convert == "yes":
                for line in maze:
                    for cell in line:
                        print(cell, end="")
                    print()

    def is_in_bound(self, pos) -> bool:
        return (pos[0] < self.height and pos[0] >= 0
                and pos[1] < self.width and pos[1] >= 0)

    def put_in_maze(self, pos: list, value: int) -> None:
        line = pos[0]
        col = pos[1]
        if (
            self.is_in_bound(pos)
            and self.maze[line][col] < 0b11111
        ):
            self.maze[line][col] = self.maze[line][col] & value

    def init_maze(self) -> None:
        if self.width > 0 and self.height > 0:
            self.maze = [[0b1111 for _ in range(self.width)]
                         for _ in range(self.height)]
            can_draw = self.can_draw_42()
            for line in range(self.height):
                for col in range(self.width):
                    if (
                        can_draw
                        and line >= int(self.height/2) - 3
                        and line < len(self.drawing) + int(self.height/2) - 3
                        and col >= int(self.width/2) - 3
                        and col < len(self.drawing[0]) + int(self.width/2) - 3
                        and self.drawing[line - int(self.height/2) + 3]
                        [col - int(self.width/2) + 3] == 1
                    ):
                        self.maze[line][col] = 0b11111
                        self.nb_cell_to_fill -= 1
        else:
            raise MazeError("Invalid information:\
 width and height must be > 0")

    def can_draw_42(self) -> bool:
        return (
            len(self.drawing) <= self.height
            and len(self.drawing[0]) <= self.width
        )

    def cross_border(self, value: int, line: int, col: int):
        if (value == self.north and line == 0):
            return (True)
        elif (value == self.south and line == self.height - 1):
            return (True)
        elif (value == self.east and col == self.width - 1):
            return (True)
        elif (value == self.west and col == 0):
            return (True)
        else:
            return (False)

    def open_wall_is(self, pos: list) -> list:
        i = pos[0]
        j = pos[1]
        open_path = []
        if self.maze[i][j] == 98:
            return (open_path)
        if self.maze[i][j] & 1 == 0:
            open_path.append(self.west)
        if self.maze[i][j] >> 1 & 1 == 0:
            open_path.append(self.south)
        if self.maze[i][j] >> 2 & 1 == 0:
            open_path.append(self.east)
        if self.maze[i][j] >> 3 & 1 == 0:
            open_path.append(self.north)
        return (open_path)
