from source.maze import Maze
from source.find_way import SolveMaze
from source.walker_pa import Walker


def check_is_accessible(walker: Walker, pos: list, mat_dij: list[list[int]], maze: Maze) -> bool:
    if (
        maze.maze[pos[0]][pos[1]] >> 4 & 1 == 0 
        and mat_dij[pos[0]][pos[1]] == maze.width * maze.height
    ):
        return (False)
    return (True)


def check_is_open_area(pos: list, maze: Maze, solvemaze: SolveMaze) -> bool:
    if pos[0] > 0 and pos[0] < maze.height - 1 and pos[1] > 0 and pos[1] < maze.width:
        if maze.maze[pos[0]][pos[1]] == 0:
            cell_open_to = solvemaze.decomp_cell(maze.maze[pos[0] - 1][pos[1] - 1])
            if (maze.east not in cell_open_to or maze.south not in cell_open_to):
                return (False)
            cell_open_to = solvemaze.decomp_cell(maze.maze[pos[0] - 1][pos[1]])
            if (
                maze.east not in cell_open_to
                or maze.south not in cell_open_to
                or maze.west not in cell_open_to
            ):
                return (False)
            cell_open_to = solvemaze.decomp_cell(maze.maze[pos[0] - 1]
                                                 [pos[1] + 1])
            if (maze.west not in cell_open_to or maze.south not in cell_open_to):
                return (False)
            cell_open_to = solvemaze.decomp_cell(maze.maze[pos[0]][pos[1] - 1])
            if (
                maze.east not in cell_open_to
                or maze.south not in cell_open_to
                or maze.north not in cell_open_to
            ):
                return (False)
            cell_open_to = solvemaze.decomp_cell(maze.maze[pos[0]][pos[1] + 1])
            if (
                maze.west not in cell_open_to
                or maze.south not in cell_open_to
                or maze.north not in cell_open_to
            ):
                return (False)
            cell_open_to = solvemaze.decomp_cell(maze.maze[pos[0] + 1]
                                                 [pos[1] - 1])
            if (
                maze.east not in cell_open_to
                or maze.north not in cell_open_to
            ):
                return (False)
            cell_open_to = solvemaze.decomp_cell(maze.maze[pos[0] + 1][pos[1]])
            if (
                maze.east not in cell_open_to or maze.west not in cell_open_to
                or maze.north not in cell_open_to
            ):
                return (False)
            cell_open_to = solvemaze.decomp_cell(maze.maze[pos[0] + 1]
                                                 [pos[1] + 1])
            if (
                maze.west not in cell_open_to
                or maze.north not in cell_open_to
            ):
                return (False)
            return (True)
        return (False)
    return (False)


def check_have_the_same_open_wall(pos: list, maze: Maze, solvemaze: SolveMaze) -> str:
    walls_of_cell = solvemaze.decomp_cell(maze.maze[pos[0]][pos[1]])
    if maze.maze[pos[0]][pos[1]] == 0b11111 and len(walls_of_cell) != 0:
        return (f"maze[{pos[0]}][{pos[1]}] in drawing have broken walls")
    if maze.north in walls_of_cell:
        if pos[0] - 1 < 0:
            return (f"maze[{pos[0]}][{pos[1]}] is open outside the maze")
        if maze.south not in solvemaze.decomp_cell(maze.maze[pos[0] - 1][pos[1]]):
            return (f"maze[{pos[0]}][{pos[1]}] is open to maze[{pos[0] - 1}][{pos[1]}]\
but maze[{pos[0] - 1}][{pos[1]}] is closed to maze[{pos[0]}][{pos[1]}]")
    if maze.east in walls_of_cell:
        if pos[1] + 1 >= maze.width:
            return (f"maze[{pos[0]}][{pos[1]}] is open outside the maze")
        if maze.west not in solvemaze.decomp_cell(maze.maze[pos[0]][pos[1] + 1]):
            return (f"maze[{pos[0]}][{pos[1]}] is open to maze[{pos[0]}][{pos[1] + 1}]\
but maze[{pos[0]}][{pos[1] + 1}] is closed to maze[{pos[0]}][{pos[1]}]")
    if maze.south in walls_of_cell:
        if pos[0] + 1 >= maze.height:
            return (f"maze[{pos[0]}][{pos[1]}] is open outside the maze")
        if maze.north not in solvemaze.decomp_cell(maze.maze[pos[0] + 1][pos[1]]):
            return (f"maze[{pos[0]}][{pos[1]}] is open to maze[{pos[0] + 1}][{pos[1]}]\
but maze[{pos[0] + 1}][{pos[1]}] is closed to maze[{pos[0]}][{pos[1]}]")
    if maze.west in walls_of_cell:
        if pos[1] - 1 < 0:
            return (f"maze[{pos[0]}][{pos[1]}] is open outside the maze")
        if maze.east not in solvemaze.decomp_cell(maze.maze[pos[0]][pos[1] - 1]):
            return (f"maze[{pos[0]}][{pos[1]}] is open to maze[{pos[0]}][{pos[1] - 1}]\
but maze[{pos[0]}][{pos[1] - 1}] is closed to maze[{pos[0]}][{pos[1]}]")
    return ("")


def check_valid_maze(maze: Maze, solvemaze: SolveMaze, walker: Walker) -> list[str]:
    errors = []
    mat_dij = solvemaze.djikstra_matrix()
    for i in range(maze.height):
        for j in range(maze.width):
            if not (check_is_accessible(walker, [i, j], mat_dij, maze)):
                errors.append(f"maze[{i}][{j}] is not accessed")
            if (check_is_open_area([i, j], maze, solvemaze)):
                errors.append(f"maze[{i}][{j}] is an open area")
            res_check_walls = check_have_the_same_open_wall([i, j], maze, solvemaze)
            if len(res_check_walls) > 0:
                errors.append(res_check_walls)
    return (errors)
