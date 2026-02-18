import random

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
        self.west = 0b1011
        self.south = 0b1101
        self.east = 0b1110
        self.dir: list = [self.north,
                          self.west,
                          self.south,
                          self.east]
        self.drawing: list = [[1, 0, 0, 0, 1, 1, 1],
                              [1, 0, 0, 0, 0, 0, 1],
                              [1, 1, 1, 0, 1, 1, 1],
                              [0, 0, 1, 0, 1, 0, 0],
                              [0, 0, 1, 0, 1, 1, 1]]

    def print_maze(self, convert: str | None = None) -> None:
        if convert:
            if convert == "hex":
                func = hex
            elif convert == "bin":
                func = bin
            elif convert == "int":
                func = int
            for col in self.maze:
                for cell in col:
                    print(func(cell), end="\t")
                    if (cell) <= 15:
                        print("\t", end="")
                print()
        else:
            print(" ")
            for _ in range(self.width):
                print("__", end="")
            print()
            for line in range(self.height):
                print("|", end="")
                for col in range(self.width):
                    cell = self.maze[line][col]
                    if line == self.entry[0] and col == self.entry[1]:
                        print("S ", end="")
                    elif cell == 0b11111:
                        print("##", end="")
                    elif line == self.exit[0] and col == self.exit[1]:
                        print(" E", end="")
                    else:
                        if (cell >> 1) & 1 == 1:
                            print("_", end="")
                        else:
                            print(" ", end="")
                        if cell & 1 == 1:
                            print("|", end="")
                        else:
                            if (cell >> 1) & 1 == 1:
                                print("_", end="")
                            else:
                                print(" ", end="")
                print()
            print(" ", end="")
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
            self.put_in_maze(self.entry, 0b0000)
            self.put_in_maze(self.exit, 0b0000)
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

    def draw_maze(self) -> None:
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
                    self.print_maze()
                else:
                    nb_dir = random.randrange(1, 3)
                    rand_dir_tab = self.dir.copy()
                    random.shuffle(rand_dir_tab)
                    for i in range(nb_dir):
                        if not (self.cross_border(rand_dir_tab[i], line, col)):
                            self.put_in_maze([line, col], rand_dir_tab[i])
                        if rand_dir_tab[i] == self.north:
                            if self.is_in_bound([line - 1, col]):
                                self.put_in_maze([line - 1, col], self.south)
                        if rand_dir_tab[i] == self.south:
                            if self.is_in_bound([line + 1, col]):
                                self.put_in_maze([line + 1, col], self.north)
                        if rand_dir_tab[i] == self.west:
                            if self.is_in_bound([line, col - 1]):
                                self.put_in_maze([line, col - 1], self.east)
                        if rand_dir_tab[i] == self.east:
                            if self.is_in_bound([line, col + 1]):
                                self.put_in_maze([line, col + 1], self.west)
