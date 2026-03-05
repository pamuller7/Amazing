from source.maze import Maze
from source.vector2 import Vector2
from random import random, shuffle
from typing import Tuple


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


def kruskal(maze: Maze):
    walls = []
    set_map = {}
    for y in range(maze.height):
        for x in range(maze.width):
            set_map[Vector2(x, y)] = set([(x, y)])
            cell_walls = [
                maze.west,
                maze.east,
                maze.north,
                maze.south,
            ]
            walls.extend(map(lambda w: ((x, y), w), cell_walls))
    shuffle(walls)
    for (x, y), wall in walls:
        cells_dividing = [
            Vector2(x, y),
            Vector2(x, y) + get_direction(maze, wall),
        ]
        # print("try ", (x, y), wall)
        if not maze.is_in_bound([cells_dividing[1].y, cells_dividing[1].x]):
            # print(
            #     f"{Vector2(x, y)} + "
            #     f"{get_direction(maze, wall)} = {Vector2(x, y) + get_direction(maze, wall)} out"
            # )
            continue
        if maze.maze[cells_dividing[1].y][cells_dividing[1].x] > 0b1111:
            continue
        if maze.maze[cells_dividing[0].y][cells_dividing[0].x] > 0b1111:
            continue

        if set_map[cells_dividing[0]] is not set_map[cells_dividing[1]]:
            # print("joining ", cells_dividing)
            res = set_map[cells_dividing[0]].union(set_map[cells_dividing[1]])
            for x, y in res:
                set_map[Vector2(x, y)] = res
            maze.put_in_maze((cells_dividing[0].y, cells_dividing[0].x), wall)
            rev = {
                maze.east: maze.west,
                maze.west: maze.east,
                maze.south: maze.north,
                maze.north: maze.south,
            }
            maze.put_in_maze((cells_dividing[1].y, cells_dividing[1].x), rev[wall])
        # print("already joined")
