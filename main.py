from source.maze import Maze
from source.walker_pa import Walker
from source.find_way import SolveMaze
import time
from mlx import Mlx


def main(args):

    m = Mlx()
    mlx_ptr = m.mlx_init()

    def mymouse(button, x, y, extra: Maze):
        pass

    def mykey(keynum, extra: Maze):
        if keynum == 65307 or keynum == 113:
            m.mlx_loop_exit(mlx_ptr)
            m.mlx_mouse_hook(win_ptr, None, None)

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

    win_ptr = m.mlx_new_window(
        mlx_ptr,
        maze.cell_size * maze.width + 1,
        maze.cell_size * maze.height + 1,
        "a_main_window",
    )

    img_ptr = m.mlx_new_image(
        mlx_ptr,
        maze.cell_size * maze.width + 1,
        maze.cell_size * maze.height + 1,
    )

    m.mlx_mouse_hook(win_ptr, mymouse, maze)
    m.mlx_key_hook(win_ptr, mykey, maze)
    maze.to_image(m, img_ptr)

    m.mlx_put_image_to_window(mlx_ptr, win_ptr, img_ptr, 0, 0)

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

    with open(maze.output_file, "w") as f:
        f.write(content)

    m.mlx_loop(mlx_ptr)

    m.mlx_destroy_window(mlx_ptr, win_ptr)
    data, _, _, _ = m.mlx_get_data_addr(img_ptr)
    m.mlx_release(mlx_ptr)


if __name__ == "__main__":
    maze1 = {
        "height": 6,
        "width": 6,
        "entry": [0, 0],
        "exit": [5, 5],
        "output_file": "test.txt",
        "perfect": True,
    }

    maze2 = {
        "height": 6,
        "width": 6,
        "entry": [0, 0],
        "exit": [5, 5],
        "output_file": "test.txt",
        "perfect": False,
    }

    maze3 = {
        "height": 9,
        "width": 9,
        "entry": [0, 0],
        "exit": [8, 8],
        "output_file": "test.txt",
        "perfect": True,
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
