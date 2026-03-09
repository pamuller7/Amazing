from source.maze import Maze
from source.walker_pa import Walker
from source.walker import kruskal
from source.find_way import SolveMaze
from source.parse import Parser
from pydantic import ValidationError
import sys


def main():
    if len(sys.argv) > 2:
        print(
            "ERROR: Too many args,"
            " Please run python3 a_maze_ing <filename>.txt"
        )
        return
    try:
        with open(sys.argv[1], "r") as f:
            args = f.read()
        config = Parser.parse(args)
        maze = Maze(config)
        if maze.config.perfect and maze.config.alt:
            kruskal(maze)
        else:
            walk = Walker(maze)
            walk.walk_and_fill()
        content = maze.print_maze("hex")
        solvmaze = SolveMaze(maze)
        content += f"Entry: {config.entry}\nExit: {config.exit}\n"
        content += solvmaze.output_shortest_way()

        if maze.config.interactive:
            output_to_print = "e"
            maze.print_maze("1")
            count_path = 0
            while output_to_print != "3":
                print(
                    """==== A-Maze-ing ====
1- Re-generate a new maze
2- Show/hide the path
3- Quit
choice(1-3): """,
                    end="",
                )
                output_to_print = input()
                print("\033c", end="")
                if output_to_print == "1":
                    main()
                    return
                if output_to_print == "2" and count_path % 2 == 1:
                    count_path += 1
                    print("Generated maze:")
                    maze.print_maze("1")
                elif output_to_print == "2" and count_path % 2 == 0:
                    count_path += 1
                    print("The shortest solution")
                    maze.print_maze()
                elif output_to_print != "3":
                    print("Input not recognised")
        with open(maze.config.output_file, "w") as f:
            f.write(content)
    except ValidationError as e:
        print(e)
    except ValueError as e:
        print("ERROR:", e)
    except IndexError:
        print("ERROR: No configuration txt given as argument. \
Please run python3 a_maze_ing <filename>.txt")
    except FileNotFoundError:
        print("File not found, ", end="")
        print("please create a config.txt with the arguments:")
        print("""    WIDTH=<int>
    HEIGHT=<int>
    ENTRY=<int>,<int>
    EXIT=<int>,<int>
    OUTPUT_FILE=<filename>
    PERFECT=True|False
    [SEED=<str>]""")


if __name__ == "__main__":
    main()
