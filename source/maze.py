
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
        if (
            self.is_in_bound(pos)
            and self.maze[line][col] < 0b11111
        ):
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
