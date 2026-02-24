from .maze import Maze
from random import random, choice
from typing import Tuple, List


class Walker:
    """Walker walks through the maze randomly, breaking walls as long as it
    doesn't break any rules.

    No 3x3 open area
    No breaking 42
    No breaking outer walls
    """

    def walk(self, maze: Maze) -> Tuple[Tuple[int,int], List[int]]:
        """"""
        if maze.height == 0 or maze.width == 0:
            return ((0,0), [])
        # todo reroll if in 42
        start_position: Tuple[int, int] = (
            int(random() * maze.width - 1),
            int(random() * maze.height - 1),
        )
        prev = None
        pos = start_position
        moves = []
        while not maze.is_valid():
            valid_moves: List[int] = self.get_valid_moves(maze, start_position)
            if len(valid_moves) == 0:
                print("dev error")
                exit()
            if len(valid_moves) > 1:
                valid_moves.remove(prev)
            prev = choice(valid_moves)
            moves.append(prev)
            apply_move(prev, maze)

        return (start_position, moves)

    def get_valid_moves(self, maze: Maze, pos: Tuple[int, int]):
        return list(
            filter(
                lambda move: self.maze_valid_after_move(maze, pos, move),
                [0b0111, 0b1011, 0b1101, 0b1110],
            )
        )

    def maze_valid_after_move(self, maze, pos, move):
        """Check if moves is out of bounds or break other rules"""
        direction = 0, 0
        if move == 0b1000:
            direction = 0, -1
        if move == 0b0100:
            direction = 1, 0
        if move == 0b0010:
            direction = 0, 1
        if move == 0b0001:
            direction = -1, 0
        # TODO, this assumes x if first dimension and y second, is that same for graphism side?
        if pos[0] + direction[0] >= len(maze.array) or (
            pos[1] + direction[1] >= len(maze.array[0])
        ):
            return False
        # TODO, check doesnt break 42 chunk
        # TODO, opt perfect: check doesnt introduce a new path
        # if self.
        # TODO,: check doesnt introduce 3x3 open area
        return True
