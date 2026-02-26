from .maze import Maze
from .walker_pa import Walker
import random
import functools


class SolveMaze:
    def __init__(self, maze: Maze, walker: Walker):
        self.maze = maze
        self.entry = self.maze.entry
        self.exit = self.maze.exit
        self.pos_line = self.entry[0]
        self.pos_col = self.entry[1]
        self.way = []
        self.explored = [self.entry]
        self.prev_dir = 1111111
        self.reverse = {
                            self.maze.north: self.maze.south,
                            self.maze.south: self.maze.north,
                            self.maze.west: self.maze.east,
                            self.maze.east: self.maze.west
        }
        self.is_in_bound = self.maze.is_in_bound

    def travel_in_maze(self, dir: int):
        if dir == self.maze.north:
            self.pos_line -= 1
        elif dir == self.maze.south:
            self.pos_line += 1
        elif dir == self.maze.west:
            self.pos_col -= 1
        elif dir == self.maze.east:
            self.pos_col += 1

    def decomp_cell(self, cell: int):
        cell_open = []
        if cell & 1 == 0:
            cell_open.append(self.maze.west)
        if cell >> 1 & 1 == 0:
            cell_open.append(self.maze.south)
        if cell >> 2 & 1 == 0:
            cell_open.append(self.maze.east)
        if cell >> 3 & 1 == 0:
            cell_open.append(self.maze.north)
        return (cell_open)

    def opti_way(self):
        opti_way = []
        if self.pos_col > self.exit[1]:
            opti_way.append(self.maze.west)
        if self.pos_col < self.exit[1]:
            opti_way.append(self.maze.east)
        if self.pos_line < self.exit[0]:
            opti_way.append(self.maze.south)
        if self.pos_line > self.exit[0]:
            opti_way.append(self.maze.north)
        return (opti_way)

    def find_a_way(self, way) -> int:
        self.explored.append([self.pos_line, self.pos_col])
        if [self.pos_line, self.pos_col] == self.exit:
            print(len(way))
            self.way = way
            return (0)
        else:
            cell_open_to = self.decomp_cell(
                self.maze.maze[self.pos_line][self.pos_col])
            opti = [x for x in self.opti_way() if x in cell_open_to]
            random.shuffle(cell_open_to)
            other_path = [x for x in cell_open_to if x not in opti]
            prioritize_opti = opti + other_path
            for dir in prioritize_opti:
                old_way = way.copy()
                self.prev_dir = dir
                old_line = self.pos_line
                old_col = self.pos_col
                self.travel_in_maze(dir)
                if not [self.pos_line, self.pos_col] in self.explored:
                    way += [dir]
                    # self.find_a_way(way)
                    if self.find_a_way(way) == 0:
                        return (0)
                way = old_way
                self.pos_line = old_line
                self.pos_col = old_col

    def get_path(self) -> str:
        way = ""
        count = 0
        self.find_a_way([])
        print(self.way)
        for path in self.way:
            if path == self.maze.north:
                way += 'N'
            if path == self.maze.south:
                way += 'S'
            if path == self.maze.east:
                way += 'E'
            if path == self.maze.west:
                way += 'W'
        print(count)
        return (way)
