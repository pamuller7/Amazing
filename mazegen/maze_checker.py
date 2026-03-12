from mazegen.maze import MazeGenerator
from mazegen.find_way import SolveMaze


def check_is_accessible(
    pos: list, mat_dij: list[list[int]], maze: MazeGenerator
) -> bool:
    """Return whether the cell at *pos* can be reached from the exit.

    A cell is considered inaccessible if it is a normal (non-drawing)
    cell whose Dijkstra distance equals the sentinel value
    ``width * height``.

    Args:
        pos: ``[line, col]`` of the cell to check.
        mat_dij: Dijkstra distance matrix produced by ``SolveMaze``.
        maze: The ``Maze`` being validated.

    Returns:
        ``True`` when the cell is reachable or is a drawing cell;
        ``False`` when it is a normal cell with no path to the exit.
    """
    if (
        maze.maze[pos[0]][pos[1]] >> 4 & 1 == 0
        and mat_dij[pos[0]][pos[1]] == maze.config.width * maze.config.height
    ):
        return False
    return True


def check_is_open_area(
    pos: list, maze: MazeGenerator, solvemaze: SolveMaze
) -> bool:
    """Return whether *pos* is the top-left corner of a fully open 3x3 area.

    An "open area" is a 3x3 block of cells where every internal wall has
    been removed, which is considered invalid in a well-formed maze.

    Args:
        pos: ``[line, col]`` of the candidate top-left corner.
        maze: The ``Maze`` being validated.
        solvemaze: A ``SolveMaze`` instance for ``decomp_cell`` access.

    Returns:
        ``True`` if the cell at *pos* is the top-left corner of a fully
        open 3x3 passage region; ``False`` otherwise.
    """
    if (
        pos[0] > 0
        and pos[0] < maze.config.height - 1
        and pos[1] > 0
        and pos[1] < maze.config.width
    ):
        if maze.maze[pos[0]][pos[1]] == 0:
            cell_open_to = solvemaze.decomp_cell(
                maze.maze[pos[0] - 1][pos[1] - 1]
            )
            if maze.east not in cell_open_to or maze.south not in cell_open_to:
                return False
            cell_open_to = solvemaze.decomp_cell(maze.maze[pos[0] - 1][pos[1]])
            if (
                maze.east not in cell_open_to
                or maze.south not in cell_open_to
                or maze.west not in cell_open_to
            ):
                return False
            cell_open_to = solvemaze.decomp_cell(
                maze.maze[pos[0] - 1][pos[1] + 1]
            )
            if maze.west not in cell_open_to or maze.south not in cell_open_to:
                return False
            cell_open_to = solvemaze.decomp_cell(maze.maze[pos[0]][pos[1] - 1])
            if (
                maze.east not in cell_open_to
                or maze.south not in cell_open_to
                or maze.north not in cell_open_to
            ):
                return False
            cell_open_to = solvemaze.decomp_cell(maze.maze[pos[0]][pos[1] + 1])
            if (
                maze.west not in cell_open_to
                or maze.south not in cell_open_to
                or maze.north not in cell_open_to
            ):
                return False
            cell_open_to = solvemaze.decomp_cell(
                maze.maze[pos[0] + 1][pos[1] - 1]
            )
            if maze.east not in cell_open_to or maze.north not in cell_open_to:
                return False
            cell_open_to = solvemaze.decomp_cell(maze.maze[pos[0] + 1][pos[1]])
            if (
                maze.east not in cell_open_to
                or maze.west not in cell_open_to
                or maze.north not in cell_open_to
            ):
                return False
            cell_open_to = solvemaze.decomp_cell(
                maze.maze[pos[0] + 1][pos[1] + 1]
            )
            if maze.west not in cell_open_to or maze.north not in cell_open_to:
                return False
            return True
        return False
    return False


def check_have_the_same_open_wall(
    pos: list, maze: MazeGenerator, solvemaze: SolveMaze
) -> str:
    """Check that every open wall of the cell at *pos* is reciprocated.

    For each open passage direction, verifies that the neighbouring cell
    also has the corresponding wall open.  Also checks that drawing cells
    have no broken walls.

    Args:
        pos: ``[line, col]`` of the cell to validate.
        maze: The ``Maze`` being validated.
        solvemaze: A ``SolveMaze`` instance for ``decomp_cell`` access.

    Returns:
        An empty string when all open walls are symmetric; a human-readable
        error message describing the first asymmetry or boundary violation
        found.
    """
    walls_of_cell = solvemaze.decomp_cell(maze.maze[pos[0]][pos[1]])
    if maze.maze[pos[0]][pos[1]] == 0b11111 and len(walls_of_cell) != 0:
        return f"maze[{pos[0]}][{pos[1]}] in drawing have broken walls"
    if maze.north in walls_of_cell:
        if pos[0] - 1 < 0:
            return f"maze[{pos[0]}][{pos[1]}] is open outside the maze"
        if maze.south not in solvemaze.decomp_cell(
            maze.maze[pos[0] - 1][pos[1]]
        ):
            return (
                f"maze[{pos[0]}][{pos[1]}] is open "
                f"to maze[{pos[0] - 1}][{pos[1]}] "
                f"but maze[{pos[0] - 1}][{pos[1]}] "
                f"is closed to maze[{pos[0]}][{pos[1]}]"
            )
    if maze.east in walls_of_cell:
        if pos[1] + 1 >= maze.config.width:
            return f"maze[{pos[0]}][{pos[1]}] is open outside the maze"
        if maze.west not in solvemaze.decomp_cell(
            maze.maze[pos[0]][pos[1] + 1]
        ):
            return (
                f"maze[{pos[0]}][{pos[1]}] is open "
                f"to maze[{pos[0]}][{pos[1] + 1}]"
                f"but maze[{pos[0]}][{pos[1] + 1}] "
                f"is closed to maze[{pos[0]}][{pos[1]}]"
            )
    if maze.south in walls_of_cell:
        if pos[0] + 1 >= maze.config.height:
            return f"maze[{pos[0]}][{pos[1]}] is open outside the maze"
        if maze.north not in solvemaze.decomp_cell(
            maze.maze[pos[0] + 1][pos[1]]
        ):
            return (
                f"maze[{pos[0]}][{pos[1]}] "
                f"is open to maze[{pos[0] + 1}][{pos[1]}] "
                f"but maze[{pos[0] + 1}][{pos[1]}] "
                f"is closed to maze[{pos[0]}][{pos[1]}]"
            )
    if maze.west in walls_of_cell:
        if pos[1] - 1 < 0:
            return f"maze[{pos[0]}][{pos[1]}] is open outside the maze"
        if maze.east not in solvemaze.decomp_cell(
            maze.maze[pos[0]][pos[1] - 1]
        ):
            return (
                f"maze[{pos[0]}][{pos[1]}] is open "
                f"to maze[{pos[0]}][{pos[1] - 1}] "
                f"but maze[{pos[0]}][{pos[1] - 1}] is "
                f"closed to maze[{pos[0]}][{pos[1]}]"
            )
    return ""


def check_valid_maze(maze: MazeGenerator, solvemaze: SolveMaze) -> list[str]:
    """Run all three validity checks on every cell of the maze.

    Combines ``check_is_accessible``, ``check_is_open_area``, and
    ``check_have_the_same_open_wall`` into a single pass over the grid.

    Args:
        maze: The ``Maze`` to validate.
        solvemaze: A ``SolveMaze`` instance built from the same maze,
            providing the Dijkstra matrix and ``decomp_cell``.

    Returns:
        A list of human-readable error strings.  An empty list means the
        maze is valid.
    """
    errors = []
    mat_dij = solvemaze.mat_star
    for i in range(maze.config.height):
        for j in range(maze.config.width):
            if not (check_is_accessible([i, j], mat_dij, maze)):
                errors.append(f"maze[{i}][{j}] is not accessed")
            if check_is_open_area([i, j], maze, solvemaze):
                errors.append(f"maze[{i}][{j}] is an open area")
            res_check_walls = check_have_the_same_open_wall(
                [i, j], maze, solvemaze
            )
            if len(res_check_walls) > 0:
                errors.append(res_check_walls)
    return errors
