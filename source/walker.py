from maze import Maze, Vector2  # todo disallowed import
from random import random, choice
from typing import Tuple, List, Generator
from math import sqrt


def is_north_set(bit: int) -> bool:
    return bit & 1 != 0


def is_east_set(bit: int) -> bool:
    return bit >> 1 & 1 != 0


def is_south_set(bit: int) -> bool:
    return bit >> 2 & 1 != 0


def is_west_set(bit: int) -> bool:
    return bit >> 3 & 1 != 0


def chunk_visited(maze: Maze, min_pos: Vector2, max_pos: Vector2):
    for y in range(
        min_pos.y,
        max_pos.y,
    ):
        for x in range(
            min_pos.x,
            max_pos.x,
        ):
            pos = Vector2(x, y)
            if not maze.is_in_bound(pos):
                continue
            if maze.at(pos) == 0b1111:
                return False
    return True


class Walker:
    """Walker walks through the maze randomly, breaking walls as long as it
    doesn't break any rules.

    No 3x3 open area
    No breaking 42
    No breaking outer walls
    """

    def __init__(self, maze: Maze) -> None:
        self.maze = maze

    # opti: fill it out chunk by chunk, Astar to next chunk when is done, stay in chunk till done
    def walk(self, yielding: bool) -> None | Generator[Vector2]:
        """"""
        if self.maze.height == 0 or self.maze.width == 0:
            return ((0, 0), [])
        start_position = self.maze.entry
        prev = None
        pos = Vector2(start_position.x, start_position.y)
        if yielding:
            yield pos

        # # invariant: when cache is visited, it is always valid
        # cache: List[List[Tuple[bool, bool]]] = []  # is_cache_valid, is_visited
        # for y in range(int(sqrt(self.maze.height)) + 1):
        #     line = []
        #     for x in range(int(sqrt(self.maze.width)) + 1):
        #         line.append((True, False))
        #     cache.append(line)

        # def all_visited() -> bool:
        #     for chunk_line in range(int(sqrt(self.maze.height)) + 1):
        #         for chunk_col in range(int(sqrt(self.maze.width)) + 1):
        #             is_cache_valid, is_visited = cache[chunk_line][chunk_col]
        #             if is_cache_valid and is_visited:
        #                 continue
        #             elif is_cache_valid:
        #                 return False
        # min_pos = Vector2(
        #     chunk_col * (int(sqrt(self.maze.width)) + 1),
        #     chunk_line * (int(sqrt(self.maze.height)) + 1),
        # )
        # max_pos = Vector2(
        #     (chunk_col + 1) * (int(sqrt(self.maze.width)) + 1),
        #     (chunk_line + 1) * (int(sqrt(self.maze.height)) + 1),
        # )
        # if chunk_visited(maze, min_pos, max_pos)
        # cache[chunk_line][chunk_col] = True, True
        # else:
        # cache[chunk_line][chunk_col] = True, False
        # return False
        #     return True

        for chunk_line in range(int(sqrt(self.maze.height)) + 1):
            for chunk_col in range(int(sqrt(self.maze.width)) + 1):
                min_pos = Vector2(
                    chunk_col * (int(sqrt(self.maze.width)) + 1),
                    chunk_line * (int(sqrt(self.maze.height)) + 1),
                )
                max_pos = Vector2(
                    (chunk_col + 1) * (int(sqrt(self.maze.width)) + 1),
                    (chunk_line + 1) * (int(sqrt(self.maze.height)) + 1),
                )
                while not chunk_visited(self.maze, min_pos, max_pos):
                    valid_moves: List[int] = self.get_valid_moves(
                        pos, min_pos, max_pos
                    )
                    if len(valid_moves) == 0:
                        print("dev error")
                        exit()
                    if len(valid_moves) > 1:
                        if prev:
                            valid_moves.remove(prev)
                    prev = choice(valid_moves)
                    direction = self.get_direction(prev)
                    next_pos = pos + direction
                    if yielding:
                        yield next_pos
                    self.apply_move(pos, next_pos, direction)
                    pos = next_pos

    def broken_with_dir(
        self,
        pos: Vector2,
        next_pos: Vector2,
        direction: Vector2,
    ) -> Tuple[int, int]:
        """Returns new value for pos and next pos after breaking the wall"""
        if direction == Vector2(-1, 0):
            return (
                self.maze.at(pos) & 0b1110,
                self.maze.at(next_pos) & 0b1011,
            )
        elif direction == Vector2(1, 0):
            return (
                self.maze.at(pos) & 0b1011,
                self.maze.at(next_pos) & 0b1110,
            )
        elif direction == Vector2(0, -1):
            return (
                self.maze.at(pos) & 0b1101,
                self.maze.at(next_pos) & 0b0111,
            )
        elif direction == Vector2(0, 1):
            return (
                self.maze.at(pos) & 0b0111,
                self.maze.at(next_pos) & 0b1101,
            )
        else:
            raise ValueError()

    def apply_move(
        self,
        pos: Vector2,
        next_pos: Vector2,
        direction: Vector2,
    ):
        (
            self.maze.maze[pos.y][pos.x],
            self.maze.maze[next_pos.y][next_pos.x],
        ) = self.broken_with_dir(pos, next_pos, direction)
        # cache_visited = cache[int(pos[0] / (sqrt(self.maze.height) + 1))][
        #     int(pos[1] / (sqrt(self.maze.width) + 1))
        # ][1]
        # cache_next_visited = cache[
        #     int(next_pos[0] / (sqrt(self.maze.height) + 1))
        # ][int(next_pos[1] / (sqrt(self.maze.width) + 1))][1]
        # if not cache_visited:
        #     cache[int(pos[0] / (sqrt(self.maze.height) + 1))][
        #         int(pos[1] / (sqrt(self.maze.width) + 1))
        #     ] = (False, False)
        # if not cache_next_visited:
        #     cache[int(next_pos[0] / (sqrt(self.maze.height) + 1))][
        #         int(next_pos[1] / (sqrt(self.maze.width) + 1))
        #     ] = (False, False)

    def get_valid_moves(
        self,
        pos: Vector2,
        min_pos: Vector2,
        max_pos: Vector2,
    ):
        return list(
            filter(
                lambda move: self.maze_valid_after_move(
                    move, pos, min_pos, max_pos
                ),
                [0b1, 0b10, 0b100, 0b1000],
            )
        )

    def get_direction(self, move: int) -> Vector2:
        direction = 0, 0
        if move == 0b0001:
            direction = -1, 0
        if move == 0b0010:
            direction = 0, 1
        if move == 0b0100:
            direction = 1, 0
        if move == 0b1000:
            direction = 0, -1
        return Vector2(*direction)

    def is_wall_broken_in_dir(
        self,
        pos: Vector2,
        next_pos: Vector2,
        direction: Vector2,
    ):
        return (
            (
                direction == Vector2(-1, 0)
                and not is_north_set(self.maze.at(pos))
                and not is_south_set(self.maze.at(next_pos))
            )
            or (
                direction == Vector2(1, 0)
                and not is_south_set(self.maze.at(pos))
                and not is_north_set(self.maze.at(next_pos))
            )
            or (
                direction == Vector2(0, -1)
                and not is_east_set(self.maze.at(pos))
                and not is_west_set(self.maze.at(next_pos))
            )
            or (
                direction == Vector2(0, 1)
                and not is_west_set(self.maze.at(pos))
                and not is_east_set(self.maze.at(next_pos))
            )
        )

    def maze_valid_after_move(
        self, move: int, pos: Vector2, min_pos: Vector2, max_pos: Vector2
    ):
        """Check if moves is out of bounds or break other rules

        if it's already maze has seen move already then the check is cheap
        Potential optimisation: return valid but not prio
        """
        direction = self.get_direction(move)
        next_pos = pos + direction

        if not self.maze.is_in_bound(next_pos):
            return False

        return self.is_wall_broken_in_dir(pos, next_pos, direction) or (
            not self.maze.at(next_pos) > 0b1111
            and not self.introduces_33_corridor(pos, next_pos, direction)
            and not (
                self.maze.perfect
                and self.introduces_loop(pos, next_pos, direction)
            )
        )

    def introduces_33_corridor(
        self, pos: Vector2, next_pos: Vector2, direction: Vector2
    ) -> bool:
        def tile_is_corridor(y, x, value) -> bool:
            if y == 0:
                if x == 0:  # top left
                    return not is_east_set(value) and not is_south_set(value)
                elif x == 2:  # top right
                    return not is_west_set(value) and not is_south_set(value)
                else:  # first line can only have north set
                    return value == 1 or value == 0
            elif y == 2:
                if x == 0:  # top
                    return not is_east_set(value) and not is_north_set(value)
                elif x == 2:  # bottom right
                    return not is_west_set(value) and not is_north_set(value)
                else:  # last line can only have south set
                    return value == 0b0100 or value == 0
            elif x == 0:
                return value == 0b1000 or value == 0
            elif x == 2:
                return value == 0b0010 or value == 0
            else:
                return value == 0

        def is_corridor(
            base: Vector2,
            e_pos: Vector2,
            e_override: int,
            e_next_pos: Vector2,
            e_next_override: int,
        ) -> bool:
            for y in range(0, 3):
                for x in range(0, 3):
                    relative = Vector2(x, y)
                    absolute = relative + base
                    if not self.maze.is_in_bound(absolute):
                        return False
                    value = self.maze.at(absolute)
                    if not absolute == base:
                        value = e_override
                    elif absolute == e_next_pos:
                        value = e_next_override
                    if not tile_is_corridor(y, x, value):
                        return False
            return True

        pos_value, next_pos_value = self.broken_with_dir(
            pos, next_pos, direction
        )
        for y in range(-3, 4):
            for x in range(-3, 4):
                relative = Vector2(x, y)
                if is_corridor(
                    pos + relative, pos, pos_value, next_pos, next_pos_value
                ):
                    return True
        return False

    def introduces_loop(self, pos, next_pos, direction) -> bool:
        return (
            not self.is_wall_broken_in_dir(pos, next_pos, direction)
            and self.maze.at(next_pos) != 0b1111
        )
