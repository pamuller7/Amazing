from .maze import Maze


class SolveMaze:
    def __init__(self, maze: Maze):
        self.maze = maze
        self.entry = [self.maze.config.entry[1], self.maze.config.entry[0]]
        self.exit = [self.maze.config.exit[1], self.maze.config.exit[0]]
        self.pos_line = self.entry[0]
        self.pos_col = self.entry[1]
        self.explored = [self.entry]
        self.perfect_error = []
        self.is_in_bound = self.maze.is_in_bound
        self.mat_star = None

    def travel_in_maze(self, dir: int) -> None:
        """Take an int (north 0b0111, south 0b1101 etc...) and change the pos
        of self
            dir: int = direction (north, south etc...)"""

        if dir == self.maze.north:
            self.pos_line -= 1
        elif dir == self.maze.south:
            self.pos_line += 1
        elif dir == self.maze.west:
            self.pos_col -= 1
        elif dir == self.maze.east:
            self.pos_col += 1

    def decomp_cell(self, cell: int) -> list:
        """tells which walls of the current cell is open
        cell: int = an argument of the maze (ex: maze[line][col])
        --> Usefull to know wich way is open and ok to moove"""

        cell_open = []
        if cell & 1 == 0:
            cell_open.append(self.maze.north)
        if cell >> 1 & 1 == 0:
            cell_open.append(self.maze.east)
        if cell >> 2 & 1 == 0:
            cell_open.append(self.maze.south)
        if cell >> 3 & 1 == 0:
            cell_open.append(self.maze.west)
        return cell_open

    def djikstra_matrix(self) -> list[list[int]]:
        """Create a new matrix, describing the distance of maze's cell
        from the exit."""

        mat_star = [
            [
                self.maze.config.width * self.maze.config.height
                for _ in range(self.maze.config.width)
            ]
            for _ in range(self.maze.config.height)
        ]
        self.pos_line = self.exit[0]
        self.pos_col = self.exit[1]
        count = 0
        mat_star[self.pos_line][self.pos_col] = 0
        cell_to_explore = [self.exit]
        for cell in cell_to_explore:
            [self.pos_line, self.pos_col] = cell
            count = mat_star[self.pos_line][self.pos_col] + 1
            avb_pos = self.decomp_cell(
                self.maze.maze[self.pos_line][self.pos_col]
            )
            for try_dir in avb_pos:
                old_dir = [self.pos_line, self.pos_col]
                self.travel_in_maze(try_dir)
                if count < mat_star[self.pos_line][self.pos_col]:
                    mat_star[self.pos_line][self.pos_col] = count
                    cell_to_explore.append([self.pos_line, self.pos_col])
                [self.pos_line, self.pos_col] = old_dir
        return mat_star

    def output_shortest_way(self) -> str:
        """Travel in the matrix created by the djikstra algo, and output the
        direction taken by the solver to link the entry to the exit."""

        if self.maze.config.animate_shortest_way:
            print("\033c", end="")
        self.mat_star = self.djikstra_matrix()
        way = ""
        self.pos_line = self.entry[0]
        self.pos_col = self.entry[1]
        init = self.mat_star[self.pos_line][self.pos_col]
        while init != 0:
            avb_pos = self.decomp_cell(
                self.maze.maze[self.pos_line][self.pos_col]
            )
            for try_dir in avb_pos:
                old_dir = [self.pos_line, self.pos_col]
                self.travel_in_maze(try_dir)
                if self.mat_star[self.pos_line][self.pos_col] == init - 1:
                    self.maze.maze[self.pos_line][self.pos_col] += 32
                    if self.maze.config.animate_shortest_way:
                        self.maze.print_maze_on_terminal(
                            "Finding the shortest solution..."
                        )
                    self.maze.maze[self.pos_line][self.pos_col] += 64
                    if try_dir == self.maze.north:
                        way += "N"
                    if try_dir == self.maze.south:
                        way += "S"
                    if try_dir == self.maze.east:
                        way += "E"
                    if try_dir == self.maze.west:
                        way += "W"
                    init = self.mat_star[self.pos_line][self.pos_col]
                    break
                else:
                    [self.pos_line, self.pos_col] = old_dir
        way += "\n"
        return way
