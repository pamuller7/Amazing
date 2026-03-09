from source.maze import Maze
from source.walker_pa import Walker
from source.walker import kruskal
from source.find_way import SolveMaze
from source.parse import Parser
from source.maze_checker import check_valid_maze
import random
from pydantic import ValidationError
import sys
from time import time
from source.graphics import themes

def main():
    new_theme = None
    if len(sys.argv) > 2:
        print(
            "ERROR: Too many args,"
            " Please run python3 a_maze_ing <filename>.txt"
        )
        return
    while True:
        try:
            with open(sys.argv[1], 'r') as f:
                args = f.read()
            args = Parser.parse(args)
            if new_theme:
                args.theme = new_theme
            x = time()
            maze = Maze(args)
            if (maze.config.animate_generation):
                print("\033c", end="")
            if maze.config.perfect and maze.config.alt:
                kruskal(maze)
            else:
                walk = Walker(maze)
                walk.walk_and_fill()
            generation = time() - x
            content = maze.print_maze("hex")
            x = time()
            solvmaze = SolveMaze(maze)
            content += f"Entry: {args.entry}\nExit: {args.exit}\n"
            content += solvmaze.output_shortest_way()
            solving = time() - x
            with open(maze.config.output_file, "w") as f:
                f.write(content)

            if maze.config.interactive:
                print("\033c", end="")
                if not maze.can_draw_42():
                    print("ERROR: The maze is too small to be printed")
                output_to_print = "e"
                count_path = 0
                if (
                    maze.config.animate_generation
                    or maze.config.animate_shortest_way
                ):
                    animation = "with animation "
                else:
                    animation = ""
                print(f"Program {animation}took:\n\
                {generation} secondes to generate the maze\n\
                {solving} secondes to solve it")
                print("checker =", check_valid_maze(maze, solvmaze))
                if maze.config.animate_shortest_way:
                    count_path += 1
                    maze.print_maze()
                else:
                    maze.print_maze("1")
                while output_to_print != "4":
                    print("""==== A-Maze-ing ====
    1- Re-generate a new maze
    2- Show/hide the path
    3- Change the theme
    4- Quit
    choice(1-4): """, end="")
                    output_to_print = input()
                    print("\033c", end="")
                    if not maze.can_draw_42():
                        print("ERROR: The maze is too small to be printed")
                    if output_to_print == "1":
                        break
                    if output_to_print == "2" and count_path % 2 == 1:
                        count_path += 1
                        print("Generated maze:")
                        maze.print_maze("1")
                    elif output_to_print == "2" and count_path % 2 == 0:
                        count_path += 1
                        print("The shortest solution:")
                        maze.print_maze()
                    elif output_to_print == "3":
                        print("Actual maze:")
                        maze.print_maze()
                        count_path = 1
                        print("==== A-Maze-ing ====")
                        theme = input("Enter the new theme among rgb, red, squeleton, green: ")
                        if theme in themes.keys():
                            maze.theme = themes[theme]
                            new_theme = theme
                            print("\033c", end="")
                            print(f"The maze with the {theme} theme:")
                            maze.print_maze()
                        else:
                            print(f"theme {theme} not recognised, back to default theme")
                    elif output_to_print == "4":
                        return
                    elif output_to_print != "4":
                        print("Input not recognised")
            else:
                return
        except ValidationError as e:
            print(e)
            return
        except (ValueError) as e:
            print("ERROR:", e)
            return
        except IndexError:
            print("ERROR: No configuration txt given as argument. \
    Please run python3 a_maze_ing <filename>.txt")
            return
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
            return


if __name__ == "__main__":
    main()
