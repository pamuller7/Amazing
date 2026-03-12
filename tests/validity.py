from unittest import TestCase
import mazegen.parse as parse
from mazegen.maze import MazeGenerator
from mazegen.maze_checker import check_valid_maze
from mazegen.find_way import SolveMaze


def get_config() -> parse.CheckedConfig:
    with open("config.txt", "r") as f:
        arg = f.read()
    return parse.Parser.parse(arg)


class ValidityTests(TestCase):
    def test_should_work(self) -> None:
        c = get_config()
        left = 4 * 4 * 2 * 2
        for w in range(2, 200, 50):
            for h in range(2, 200, 50):
                for alt in [True, False]:
                    for perfect in [True, False]:
                        left -= 1
                        print(left)
                        c.width = w
                        c.height = h
                        c.entry = (0, 0)
                        c.exit = (1, 1)
                        c.alt = alt
                        c.interactive = False
                        c.animate_generation = False
                        c.animate_shortest_way = False
                        c.perfect = perfect
                        maze = MazeGenerator(c)
                        s = SolveMaze(maze)
                        self.assertTrue(not check_valid_maze(maze, s))
