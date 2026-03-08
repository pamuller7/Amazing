from source.maze import Maze
from source.vector2 import Vector2
from random import shuffle
from typing import Self, List


def get_direction(maze: Maze, move: int) -> Vector2:
    if move == maze.north:
        return Vector2(0, -1)
    if move == maze.south:
        return Vector2(0, 1)
    if move == maze.east:
        return Vector2(1, 0)
    if move == maze.west:
        return Vector2(-1, 0)
    raise ValueError("direction")


class DisjointSet:
    def __init__(self, pos: Vector2) -> None:
        self.pos: Vector2 = pos
        self.rank: int = 0
        self.parent: Self = self

    @classmethod
    def at(cls, sets: List[List[Self]], pos: Vector2) -> Self:
        return sets[pos.y][pos.x]

    @classmethod
    def find(cls, sets: List[List[Self]], pos: Vector2) -> Self:
        x = sets[pos.y][pos.x]
        while x != x.parent:
            x.parent = x.parent.parent
            x = x.parent
        return x

    @classmethod
    def merge(
        cls, sets: List[List[Self]], pos1: Vector2, pos2: Vector2
    ) -> bool:
        x = cls.find(sets, pos1)
        y = cls.find(sets, pos2)
        if x is y:
            return False
        x.parent = y
        return True


def kruskal(maze: Maze):
    walls = []
    sets: List[List[DisjointSet]] = [
        [DisjointSet(Vector2(x, y)) for x in range(maze.width)]
        for y in range(maze.height)
    ]
    for y in range(maze.height):
        for x in range(maze.width):
            cell_walls = [
                maze.west,
                maze.east,
                maze.north,
                maze.south,
            ]
            walls.extend([(Vector2(x, y), w) for w in cell_walls])
    shuffle(walls)
    for pos, wall in walls:
        cells_dividing: List[Vector2] = [
            pos,
            pos + get_direction(maze, wall),
        ]
        if not maze.is_in_bound([cells_dividing[1].y, cells_dividing[1].x]):
            continue
        if maze.maze[cells_dividing[1].y][cells_dividing[1].x] > 0b1111:
            continue
        if maze.maze[cells_dividing[0].y][cells_dividing[0].x] > 0b1111:
            continue
        if DisjointSet.merge(sets, cells_dividing[0], cells_dividing[1]):
            maze.put_in_maze((cells_dividing[0].y, cells_dividing[0].x), wall)
            rev = {
                maze.east: maze.west,
                maze.west: maze.east,
                maze.south: maze.north,
                maze.north: maze.south,
            }
            maze.put_in_maze(
                (cells_dividing[1].y, cells_dividing[1].x), rev[wall]
            )
            if maze.anim_gen:
                maze.print_maze_on_terminal("")
