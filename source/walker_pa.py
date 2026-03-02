from .maze import Maze
import random

class Walker:
    def __init__(self, maze: Maze):
        self.maze = maze
        self.pos_line = 0
        self.pos_col = 0
        self.line_checked = 0
        self.nb_cell_to_fill: int = self.maze.nb_cell_to_fill

    def is_a_possible_way(self, wall_to_open: int, pos: list) -> bool:
        '''Output a bool, telling if the position decribed by pos
        is unexplored and in bound of the maze.

            wall_to_open: int = the wall we are trying to open
            pos: int = the current position in the maze
            --> Usefull to check if a wall can be broken'''

        if wall_to_open == self.maze.north:
            try_pos = [pos[0] - 1, pos[1]]
        elif wall_to_open == self.maze.east:
            try_pos = [pos[0], pos[1] + 1]
        elif wall_to_open == self.maze.south:
            try_pos = [pos[0] + 1, pos[1]]
        elif wall_to_open == self.maze.west:
            try_pos = [pos[0], pos[1] - 1]
        return (self.maze.is_in_bound(try_pos)
                and self.maze.maze[try_pos[0]][try_pos[1]] == 0b1111)

    def loop_the_path(self, wall_to_open: int, pos: list) -> bool:
        '''sensibly like 'is_a_possible_way', except this one
        authorize to break a wall of an already explored cell

            wall_to_open: int = the wall we are trying to open
            pos: int = the current position in the maze
            --> Usefull to create a loop, for inperfect mazes'''

        try_pos = [-1, -1]
        if (
            wall_to_open == self.maze.north
            and self.maze.maze[pos[0]][pos[1]] & 1 == 1
        ):
            try_pos = [pos[0] - 1, pos[1]]
        elif (
            wall_to_open == self.maze.east
            and self.maze.maze[pos[0]][pos[1]] >> 1 & 1 == 1
        ):
            try_pos = [pos[0], pos[1] + 1]
        elif (
            wall_to_open == self.maze.south
            and self.maze.maze[pos[0]][pos[1]] >> 2 & 1 == 1
        ):
            try_pos = [pos[0] + 1, pos[1]]
        elif (
            wall_to_open == self.maze.west
            and self.maze.maze[pos[0]][pos[1]] >> 3 & 1 == 1
        ):
            try_pos = [pos[0], pos[1] - 1]
        # return not try_pos or self.maze.is_in_bound(try_pos) or self.maze.is_in_bound(try_pos)
        if not try_pos:
            return (False)
        return (self.maze.is_in_bound(try_pos)
                and self.maze.maze[try_pos[0]][try_pos[1]] < 0b1111)

    def update_dir(self, way_to_open: int) -> None:
        '''break the wall of the cell's neighboors
        way_to_open: int = the wall we want to break'''

        if way_to_open == self.maze.north:
            self.maze.put_in_maze([self.pos_line - 1, self.pos_col],
                                  self.maze.south)
            self.pos_line -= 1
        elif way_to_open == self.maze.south:
            self.maze.put_in_maze([self.pos_line + 1, self.pos_col],
                                  self.maze.north)
            self.pos_line += 1
        elif way_to_open == self.maze.west:
            self.maze.put_in_maze([self.pos_line, self.pos_col - 1],
                                  self.maze.east)
            self.pos_col -= 1
        elif way_to_open == self.maze.east:
            self.maze.put_in_maze([self.pos_line, self.pos_col + 1],
                                  self.maze.west)
            self.pos_col += 1
        self.nb_cell_to_fill -= 1

    def travel_in_maze(self, dir: int) -> None:
        '''Take an int (north 0b0111, south 0b1101 etc...) and change the pos
        of self
            dir: int = direction (north, south etc...)'''

        if dir == self.maze.north:
            self.pos_line -= 1
        elif dir == self.maze.south:
            self.pos_line += 1
        elif dir == self.maze.west:
            self.pos_col -= 1
        elif dir == self.maze.east:
            self.pos_col += 1

    def draw_path(self) -> int:
        '''draw a random path, starting from the current position,
        breaking random walls of unexplored cells
            return the length of the path we created'''

        path_length = 0
        possible_ways = [x for x in self.maze.dir
                         if self.is_a_possible_way(
                             x, [self.pos_line, self.pos_col])]
        while possible_ways:
            try_way = random.choice(possible_ways)
            self.maze.put_in_maze([self.pos_line, self.pos_col], try_way)
            self.update_dir(try_way)
            possible_ways = [x for x in self.maze.dir
                             if self.is_a_possible_way(
                                 x, [self.pos_line, self.pos_col])]
            path_length += 1
        if not self.maze.perfect:
            possible_ways = [x for x in self.maze.dir
                             if self.loop_the_path(
                                 x, [self.pos_line, self.pos_col])]
            if possible_ways:
                try_way = random.choice(possible_ways)
                self.nb_cell_to_fill += 1
                self.maze.put_in_maze([self.pos_line, self.pos_col], try_way)
                self.update_dir(try_way)
        return (path_length)

    def find_incomplete_cell(self, pos: list) -> list:
        '''checker, as the maze is randomly created, avoid that some parts are
        forgotten.
            return the pos of cell that are still unexplored.
            pos: list = the position from which we start the check'''

        for i in range(pos[0], self.maze.height):
            if pos[0] != self.line_checked:
                start_col = 0
            else:
                start_col = pos[1]
            for j in range(start_col, self.maze.width):
                if (
                    self.maze.maze[i][j] < 0b1111
                    and len([x for x in self.maze.dir
                             if self.is_a_possible_way(x, [i, j])]) >= 1
                ):
                    return ([i, j])
            self.line_checked = i + 1

    def walk_and_fill(self) -> None:
        '''travel in the maze, when an unexplored cell is encountered,
        draw a random path'''

        if self.nb_cell_to_fill == 0:
            return
        self.pos_line = 0
        self.pos_col = 0
        last_check_pos = [0, 0]
        while self.nb_cell_to_fill - 1 != 0:
            if not [x for x in self.maze.dir
                    if self.is_a_possible_way(
                        x, [self.pos_line, self.pos_col])]:
                self.line_checked = last_check_pos[0]
                last_check_pos = self.find_incomplete_cell(last_check_pos)
                if not last_check_pos:
                    return
                self.pos_line = last_check_pos[0]
                self.pos_col = last_check_pos[1]
            else:
                self.draw_path()
                # print(self.maze.print_maze())
