from mazegen.maze import Maze


class SolveMaze:
    """Solve a ``Maze`` and expose the shortest entry-to-exit path.

    On construction a Dijkstra distance matrix (``mat_star``) is built
    from the exit cell outward.  ``output_shortest_way`` then greedily
    walks from the entry towards decreasing distance values to reconstruct
    the path.

    Attributes:
        maze: The ``Maze`` instance being solved.
        entry: ``[line, col]`` of the entry cell.
        exit: ``[line, col]`` of the exit cell.
        pos_line: Current row index used during traversal.
        pos_col: Current column index used during traversal.
        explored: List of ``[line, col]`` positions visited so far.
        is_in_bound: Convenience alias for ``maze.is_in_bound``.
        mat_star: The Dijkstra distance matrix (distances from the exit).
    """

    def __init__(self, maze: Maze) -> None:
        """Initialise the solver and build the Dijkstra distance matrix.

        Args:
            maze: The fully generated ``Maze`` to solve.
        """
        self.maze = maze
        self.entry = [self.maze.config.entry[1], self.maze.config.entry[0]]
        self.exit = [self.maze.config.exit[1], self.maze.config.exit[0]]
        self.pos_line = self.entry[0]
        self.pos_col = self.entry[1]
        self.explored = [self.entry]
        self.is_in_bound = self.maze.is_in_bound
        self.mat_star = self.djikstra_matrix()

    def travel_in_maze(self, dir: int) -> None:
        """Advance ``pos_line`` / ``pos_col`` one step in direction *dir*.

        Args:
            dir: Direction bitmask (``maze.north``, ``maze.south``,
                ``maze.east``, or ``maze.west``).
        """
        if dir == self.maze.north:
            self.pos_line -= 1
        elif dir == self.maze.south:
            self.pos_line += 1
        elif dir == self.maze.west:
            self.pos_col -= 1
        elif dir == self.maze.east:
            self.pos_col += 1

    def decomp_cell(self, cell: int) -> list[int]:
        """Return the list of open-passage directions for a raw cell value.

        A direction is considered open when its corresponding wall bit is 0.

        Args:
            cell: Raw integer value from ``maze.maze[line][col]``.

        Returns:
            List of direction bitmasks for every passage that is open.
        """
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
        """Build and return the Dijkstra distance matrix from the exit.

        Initialises every cell with the sentinel value
        ``width * height`` (unreachable), sets the exit to 0, and performs
        a BFS that propagates shortest distances through open passages.

        Returns:
            A ``height × width`` matrix where each entry is the minimum
            number of steps needed to reach the exit from that cell.
        """
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
        """Trace the shortest path and return it as a cardinal-direction
        string.

        Starting from the entry, greedily moves to the neighbour whose
        distance in ``mat_star`` is exactly one less than the current
        cell, marking each visited cell in the maze for rendering (bits 5
        and 6).  Optionally streams each step to the terminal when
        ``config.animate_shortest_way`` is ``True``.

        Returns:
            A string of `'N'`, `'S'`, `'E'`, `'W'` characters
            describing each step of the solution, followed by a newline.
        """
        if self.maze.config.animate_shortest_way:
            print("\033c", end="")
        way = ""
        self.pos_line = self.entry[0]
        self.pos_col = self.entry[1]
        self.maze.maze[self.pos_line][self.pos_col] += 32
        if self.maze.config.animate_shortest_way:
            self.maze.print_maze_on_terminal(
                "Finding the shortest solution...", True, "1"
            )
        self.maze.maze[self.pos_line][self.pos_col] += 64
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
                            "Finding the shortest solution...", True, "1"
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
