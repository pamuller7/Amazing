from source.maze import Maze
from source.walker_pa import Walker
import random

test = Maze(10, 10, [80, 80], [90, 90], "test", False)
test.init_maze()
test.print_maze("yes")
# test.print_maze("bin")
walk = Walker(test, [0,0])

print("here")
walk.walk_and_fill()
test.print_maze("hex")

for i in range( test.height):
	for j in range(test.width):
		if test.maze[i][j] == 0b1111:
			print(f"ERROR MAZE[{i}][{j}]")


# def travel_in():
# 	walk.pos_col = 0
# 	walk.pos_line = 0
# 	open_wall = walk.maze.open_wall_is([walk.pos_line, walk.pos_col])
# 	x = random.choice([x for x in open_wall])
# 	print([bin(x) for x in open_wall])
# 	while open_wall:
# 		old_x = x
# 		x = random.choice([x for x in open_wall if x != old_x])
# 		walk.maze.maze[walk.pos_line][walk.pos_col] = 98
# 		walk.travel_in_maze(x)
# 		print(walk.pos_line, walk.pos_col)
# 		open_wall = walk.maze.open_wall_is([walk.pos_line, walk.pos_col])
# 		print([bin(x) for x in open_wall])

# travel_in()
# test.print_maze()