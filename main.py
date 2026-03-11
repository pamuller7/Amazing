from source.maze import Maze
from source.find_way import SolveMaze
import source.parse as parsing
import random
import sys
from time import time
from typing import Any


def handle_parse_one(maze: Maze, options: list, user_input: int) -> bool:
    parser: parsing.KeyParser = options[user_input]
    if not isinstance(parser, parsing.KeyParser):
        raise TypeError(f"expected `KeyParser` got {type(parser)}")
    res: Any = None

    if isinstance(parser.arg, parsing.DictKeysParser):
        print(f"Enter the new value for {parser.key_name}:")
        for i, opt in enumerate(parser.arg.allowed):
            if isinstance(opt, str):
                print(f"{i+1}- {opt}")
        arg = input()
        res = parser.arg.parse(arg, 0)
        if isinstance(res, parsing.ParseError):
            is_int = False
            try:
                int_arg = int(arg)
                is_int = True
                if int_arg - 1 < 0:
                    raise IndexError
                res = parser.arg.allowed[int_arg - 1]
            except (ValueError, IndexError):
                if is_int:
                    print(f"ERROR: {arg} is out of bounds")
    if isinstance(parser.arg, parsing.IdentParser):
        arg = input(f"Enter valid identity string for {parser.key_name}: ")
        res = parser.arg.parse(arg, 0)
    if isinstance(parser.arg, parsing.BoolParser):
        res = not getattr(maze.config, parser.key_name.lower())
    if res is not None:
        if isinstance(res, parsing.ParseError):
            print(f"ERROR: {res.msg} - press enter")
            input()
        else:
            setattr(maze.config, parser.key_name.lower(), res)
            print("\033c", end="")
            print("The maze with updated config:")
            return True
    return True


def print_header(
    maze: Maze, generation_time: float, solving_time: float
) -> None:
    print("\033c", end="")
    if not maze.can_draw_42():
        print("ERROR: The maze is too small to be printed")
    animation = (
        "with animation "
        if maze.config.animate_generation or maze.config.animate_shortest_way
        else ""
    )
    print(f"Seed used: {maze.config.seed}")
    print(f"Alt: {maze.config.alt}")
    print(f"Perfect: {maze.config.perfect}")
    print(f"Program {animation}took:")
    print(f"{generation_time} secondes to generate the maze")
    print(f"{solving_time} secondes to solve it")


def handle_interaction(
    maze: Maze, generation_time: float, solving_time: float
) -> bool:
    """Returns False if you need to exit"""
    print_header(maze, generation_time, solving_time)
    count_path = 0
    if maze.config.animate_shortest_way:
        count_path += 1
        maze.print_maze("1")
    else:
        maze.print_maze()
    options = [
        "Re-generate a new maze",
        "Show/hide the path",
        *parsing.Parser.interactable_extractors(),
        "Quit",
    ]
    user_input = None
    while True:
        print("==== A-Maze-ing ====")
        for i, opt in enumerate(options):
            if isinstance(opt, str):
                print(f"{i+1}- {opt}")
            elif isinstance(opt, parsing.KeyParser):
                if isinstance(opt.arg, parsing.BoolParser):
                    print(f"{i+1}- toggle {opt.key_name}")
                else:
                    print(f"{i+1}- set {opt.key_name}")
            else:
                raise TypeError

        print(f"choice(1-{len(options)}):", end="")

        try:
            user_input = int(input()) - 1
        except ValueError:
            print("\033c", end="")
            input("Input not recognised - press enter")
            continue

        # Quitting
        if user_input == len(options) - 1:
            return False

        if user_input >= len(options):
            print("\033c", end="")
            print("Input not recognised")
            continue
        print("\033c", end="")
        # Regenerating
        if user_input == 0:
            maze.config.seed = hex(random.randint(16**16, 16**17))
            return True
        elif user_input == 1:
            if count_path % 2 == 1:
                count_path += 1
                print("Generated maze:")
                maze.print_maze()
            else:
                count_path += 1
                print("The shortest solution:")
                maze.print_maze("1")
        else:
            if handle_parse_one(maze, options, user_input):
                return True


def main() -> None:
    if len(sys.argv) > 2:
        print(
            "ERROR: Too many args,"
            " Please run python3 a_maze_ing <filename>.txt"
        )
        return
    try:
        filename = sys.argv[1]
    except IndexError:
        print("ERROR: No configuration txt given as argument.")
        print("Please run python3 a_maze_ing <filename>.txt")
        return
    try:
        with open(filename, "r") as f:
            arg = f.read()
    except FileNotFoundError:
        print("File not found, ", end="")
        return
    try:
        config: parsing.CheckedConfig = parsing.Parser.parse(arg)
    except ValueError as e:
        print(e)
        print("please create a config file with the arguments:")
        print(parsing.Parser.config_format())
        return
    if config.seed is None:
        config.seed = hex(random.randint(16**16, 16**17))
    while True:
        random.seed(config.seed)
        x = time()
        maze = Maze(config)
        generation_time = time() - x
        content = maze.print_maze("hex")
        x = time()
        solver = SolveMaze(maze)
        content += f"Entry: {config.entry}\nExit: {config.exit}\n"
        content += solver.output_shortest_way()
        solving_time = time() - x
        with open(maze.config.output_file, "w") as f:
            f.write(content)
        if maze.config.interactive and handle_interaction(
            maze, generation_time, solving_time
        ):
            continue
        return


if __name__ == "__main__":
    main()
