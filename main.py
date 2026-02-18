from source.maze import Maze
import random

test = Maze(21, 21, [0, 0], [19, 19], "test", False)
test.init_maze()
test.print_maze()
test.print_maze("bin")
test.draw_maze()
test.print_maze()
test.print_maze("bin")
print(bin(0b0110 & 1))