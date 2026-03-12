from mazegen.maze import Maze
import mazegen.parse as parsing
import random
import sys
from typing import Any


def handle_parse_one(maze: Maze, options: list, user_input: int) -> bool:
    """Apply a single interactive configuration change to the maze.

    Prompts the user for a new value for the selected configuration key,
    validates it, and updates ``maze.config`` in place.

    Args:
        maze: The current ``Maze`` instance whose config will be mutated.
        options: The full list of menu options (strings and
            ``KeyParser`` instances) as displayed to the user.
        user_input: Zero-based index of the chosen option inside *options*.

    Returns:
        ``True`` in all cases (signals the main loop to redraw the maze).

    Raises:
        TypeError: If the selected option is not a ``KeyParser``.
    """
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


def print_header(maze: Maze) -> None:
    """Clear the terminal and print the run summary header.

    Displays the seed, alt flag, perfect flag, and the time taken to
    generate and solve the maze.

    Args:
        maze: The ``Maze`` instance that was generated.
    """
    print("\033c", end="")
    if not maze.can_draw_42():
        print("ERROR: The maze is too small to be printed")
    print(f"Seed used: {maze.config.seed}")
    print(f"Alt: {maze.config.alt}")
    print(f"Perfect: {maze.config.perfect}")


def handle_interaction(maze: Maze) -> bool:
    """Run one iteration of the interactive terminal menu.

    Prints the maze, then enters a loop offering the user choices to
    regenerate, toggle the solution path, tweak config options, or quit.

    Args:
        maze: The ``Maze`` instance to display and interact with.

    Returns:
        ``True`` if the caller should regenerate the maze with the
        (possibly updated) config; ``False`` if the user chose to quit.
    """
    print_header(maze)
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
    """Parse CLI arguments, load config, generate and solve the maze.

    Expects exactly one positional argument: the path to a plain-text
    configuration file.  Writes the hex-encoded maze and its solution to
    the output file specified inside that config.  When ``INTERACTIVE``
    is enabled the function loops, redrawing the maze after each user
    action, until the user quits.
    """
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
        print(f"File not found: {filename}", end="")
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
        try:
            maze = Maze(config)
        except ValueError as e:
            print(f"Maze error: {e}")
            return
        if maze.config.interactive and handle_interaction(maze):
            continue
        return


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting program...")
