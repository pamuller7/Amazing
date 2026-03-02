from source.maze import Maze
from source.walker_pa import Walker
from source.find_way import SolveMaze
import time

def main(args):

    # create a maze object
    maze = Maze(**args)

    # print it (initiall)
    # print(maze.print_maze())

    # init a walker (a valid and initiated maze as argument)
    walk = Walker(maze)

    # walk through the empty maze and generate it
    x = time.time()
    walk.walk_and_fill()
    print(maze.print_maze())
    print("Creation time", time.time() - x)

    # store the new maze
    # content = maze.print_maze()

    # store the hexa maze(MANDATORY)
    content = maze.print_maze("hex")

    # init the solver
    x = time.time()
    solvmaze = SolveMaze(maze)
    print("Resolution time", time.time() - x)

    # store the shortest way(MANDATORY)
    content += solvmaze.output_shortest_way()

    with open(maze.output_file, 'w') as f:
        f.write(content)


if __name__ == "__main__":
    maze1 = {
            "height": 6,
            "width": 6,
            "entry": [0, 0],
            "exit": [5, 5],
            "output_file": "test.txt",
            "perfect": True
            }
    
    maze2 = {
            "height": 6,
            "width": 6,
            "entry": [0, 0],
            "exit": [5, 5],
            "output_file": "test.txt",
            "perfect": False
            }
    
    maze3 = {
            "height": 9,
            "width": 9,
            "entry": [0, 0],
            "exit": [8, 8],
            "output_file": "test.txt",
            "perfect": True
            }

    # maze4 = {
    #         "height": 50,
    #         "width": 50,
    #         "entry": [0, 0],
    #         "exit": [49, 49],
    #         "output_file": "test.txt",
    #         "perfect": True
    #         }
    # maze5 = {
    #         "height": 50,
    #         "width": 50,
    #         "entry": [0, 0],
    #         "exit": [49, 49],
    #         "output_file": "test.txt",
    #         "perfect": False
    #         }
    mazes = [maze1, maze2, maze3]
    for maze in mazes:
        main(maze)
