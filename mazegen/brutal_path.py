from mazegen.vector2 import Vector2
from typing import Literal
import random


class Walker:
    """Carves passages through a ``Maze`` using a randomised
    walk algorithm.

    Starting from a random cell, the walker repeatedly moves to an
    unexplored neighbour, opening the shared wall as it goes.  When the
    walker reaches a dead end, ``find_incomplete_cell`` locates the next
    unexplored cell and teleports the walker there.  The process repeats
    until every non-drawing cell has been visited.

    For imperfect mazes (``config.perfect == False``) an additional loop
    wall is optionally opened at each dead end.

    Attributes:
        maze: The ``Maze`` instance being generated.
        pos_line: Current row index of the walker.
        pos_col: Current column index of the walker.
        line_checked: Tracks how many rows have been scanned during
            incomplete-cell searches (unused externally).
        nb_cell_to_fill: Number of cells that still need to be carved.
    """

    from mazegen.maze import MazeGenerator

    def __init__(self, maze: MazeGenerator) -> None:
        """Initialise the walker for a given maze.

        Args:
            maze: The ``Maze`` instance to generate paths in.
        """
        self.maze = maze
        self.pos_line = 0
        self.pos_col = 0
        self.line_checked = 0
        self.nb_cell_to_fill: int = self.maze.nb_cell_to_fill

    def is_a_possible_way(self, wall_to_open: int, pos: list) -> bool:
        """Return whether the neighbour in direction *wall_to_open*
        is unexplored.

        An unexplored cell has value ``0b1111`` (all walls intact) and lies
        within the maze boundaries.

        Args:
            wall_to_open: One of the four direction bitmasks
                (``maze.north``, ``maze.east``, ``maze.south``,
                ``maze.west``).
            pos: ``[line, col]`` of the current cell.

        Returns:
            ``True`` if the neighbouring cell in the given direction is
            in bounds and has not yet been carved.
        """
        try_pos = [0, 0]
        if wall_to_open == self.maze.north:
            try_pos = [pos[0] - 1, pos[1]]
        elif wall_to_open == self.maze.east:
            try_pos = [pos[0], pos[1] + 1]
        elif wall_to_open == self.maze.south:
            try_pos = [pos[0] + 1, pos[1]]
        elif wall_to_open == self.maze.west:
            try_pos = [pos[0], pos[1] - 1]
        return (
            self.maze.is_in_bound(Vector2.from_iter(try_pos).inverted())
            and self.maze.maze[try_pos[0]][try_pos[1]] == 0b1111
        )

    def loop_the_path(self, wall_to_open: int, pos: list) -> bool:
        """Return whether a loop wall can be opened at the current dead end.

        Unlike ``is_a_possible_way``, this method allows breaking a wall
        into an already-explored (carved) cell, which creates a loop and
        produces an imperfect maze.  It also checks that the wall in the
        given direction is still intact before attempting the opening.

        Args:
            wall_to_open: Direction bitmask to test.
            pos: ``[line, col]`` of the current cell.

        Returns:
            ``True`` if the wall is still present and the neighbour is an
            already-explored, in-bounds cell.
        """
        try_pos = [-1, -1]
        if (
            wall_to_open == self.maze.north
            and self.maze.maze[pos[0]][pos[1]] & 1 == 1
        ):
            try_pos = [pos[0] - 1, pos[1]]
        elif (
            wall_to_open == self.maze.east
            and self.maze.maze[pos[0]][pos[1]] >> 1 & 1 == 1
        ):
            try_pos = [pos[0], pos[1] + 1]
        elif (
            wall_to_open == self.maze.south
            and self.maze.maze[pos[0]][pos[1]] >> 2 & 1 == 1
        ):
            try_pos = [pos[0] + 1, pos[1]]
        elif (
            wall_to_open == self.maze.west
            and self.maze.maze[pos[0]][pos[1]] >> 3 & 1 == 1
        ):
            try_pos = [pos[0], pos[1] - 1]
        if not try_pos:
            return False
        return (
            self.maze.is_in_bound(Vector2.from_iter(try_pos).inverted())
            and self.maze.maze[try_pos[0]][try_pos[1]] < 0b1111
        )

    def update_dir(self, way_to_open: int) -> None:
        """Open *way_to_open* wall of the current cell and advance the walker.

        Breaks the reciprocal wall of the neighbouring cell, moves
        ``pos_line`` / ``pos_col`` to that neighbour, and decrements
        ``nb_cell_to_fill``.

        Args:
            way_to_open: Direction bitmask indicating which wall to open.
        """
        if way_to_open == self.maze.north:
            self.maze.put_in_maze(
                Vector2(self.pos_col, self.pos_line - 1), self.maze.south
            )
            self.pos_line -= 1
        elif way_to_open == self.maze.south:
            self.maze.put_in_maze(
                Vector2(self.pos_col, self.pos_line + 1), self.maze.north
            )
            self.pos_line += 1
        elif way_to_open == self.maze.west:
            self.maze.put_in_maze(
                Vector2(
                    self.pos_col - 1,
                    self.pos_line,
                ),
                self.maze.east,
            )
            self.pos_col -= 1
        elif way_to_open == self.maze.east:
            self.maze.put_in_maze(
                Vector2(self.pos_col + 1, self.pos_line), self.maze.west
            )
            self.pos_col += 1
        self.nb_cell_to_fill -= 1

    def travel_in_maze(self, dir: int) -> None:
        """Move the walker one step in direction *dir* without carving a wall.

        Updates ``pos_line`` and ``pos_col`` to reflect the new position.

        Args:
            dir: Direction bitmask (``maze.north``, ``maze.south``,
                ``maze.east``, or ``maze.west``).
        """
        if dir == self.maze.north:
            self.pos_line -= 1
        elif dir == self.maze.south:
            self.pos_line += 1
        elif dir == self.maze.west:
            self.pos_col -= 1
        elif dir == self.maze.east:
            self.pos_col += 1

    def draw_path(self) -> int:
        """Carve a random path from the current position until a dead end.

        Repeatedly chooses a random unexplored neighbour, opens the shared
        wall, and advances the walker.  For imperfect mazes, also tries to
        open one loop wall when the dead end is reached.

        Returns:
            The number of cells carved during this path segment.
        """
        path_length = 0
        possible_ways = [
            x
            for x in self.maze.dir
            if self.is_a_possible_way(x, [self.pos_line, self.pos_col])
        ]
        while possible_ways:
            try_way = random.choice(possible_ways)
            self.maze.put_in_maze(
                Vector2(self.pos_col, self.pos_line), try_way
            )
            self.update_dir(try_way)
            possible_ways = [
                x
                for x in self.maze.dir
                if self.is_a_possible_way(x, [self.pos_line, self.pos_col])
            ]
            path_length += 1
        if not self.maze.config.perfect:
            possible_ways = [
                x
                for x in self.maze.dir
                if self.loop_the_path(x, [self.pos_line, self.pos_col])
            ]
            if possible_ways:
                try_way = random.choice(possible_ways)
                self.nb_cell_to_fill += 1
                self.maze.put_in_maze(
                    Vector2(
                        self.pos_col,
                        self.pos_line,
                    ),
                    try_way,
                )
                self.update_dir(try_way)
        return path_length

    def find_incomplete_cell(
        self, tab_line: list[int], tab_col: list[int], index: list[int]
    ) -> list:
        """Scan the maze for the next cell that can still be carved.

        Iterates through the rows in *tab_line* and columns in *tab_col*,
        returning the ``[line, col]`` of the first cell that is already
        partially carved (``< 0b1111``) *and* has at least one unexplored
        neighbour.  Updates ``index[0]`` with the number of rows scanned.

        Args:
            tab_line: Row indices to search, in priority order.
            tab_col: Column indices to search within each row.
            index: Single-element list used to pass the scan progress back
                to the caller.

        Returns:
            ``[line, col]`` of the first suitable cell, or an empty list
            when no such cell exists.
        """
        for count_line, i in enumerate(tab_line):
            for j in tab_col:
                if (
                    self.maze.maze[i][j] < 0b1111
                    and len(
                        [
                            x
                            for x in self.maze.dir
                            if self.is_a_possible_way(x, [i, j])
                        ]
                    )
                    >= 1
                ):
                    return [i, j]
            index[0] = count_line
        return []

    def is_around_drawing(
        self, pos: int, check: Literal["line", "col"]
    ) -> bool:
        """Return whether *pos* falls in the rows or columns occupied
        by the drawing.

        Used to avoid starting the walker inside the decorative centrepiece.

        Args:
            pos: Row index (when *check* is ``"line"``) or column index
                (when *check* is ``"col"``).
            check: Dimension to test — ``"line"`` or ``"col"``.

        Returns:
            ``False`` if the maze is too small for the drawing.
            Otherwise ``True`` when *pos* overlaps the drawing region.
        """
        if not self.maze.can_draw_42():
            return False
        line_draw = len(self.maze.drawing)
        col_draw = len(self.maze.drawing[0])
        if check == "line":
            return pos >= int(
                self.maze.config.height / 2 - line_draw / 2
            ) and pos < line_draw + int(
                self.maze.config.height / 2 - line_draw / 2
            )
        if check == "col":
            return pos >= int(
                self.maze.config.width / 2 - col_draw / 2
            ) and pos < col_draw + int(
                self.maze.config.width / 2 - col_draw / 2
            )
        return False

    def walk_and_fill(self) -> None:
        """Drive the full random-walk generation until every cell is carved.

        Picks a random starting cell outside the drawing region, then
        loops: when the walker has no unexplored neighbours it calls
        ``find_incomplete_cell`` to teleport to the next workable position.
        Continues until ``nb_cell_to_fill`` reaches 1 (last cell is handled
        implicitly).  Prints the maze to the terminal at each step when
        ``config.animate_generation`` is ``True``.
        """
        if self.maze.config.animate_generation:
            print("\033c", end="")
        if self.nb_cell_to_fill == 0:
            return
        self.pos_line = random.choice(
            [
                x
                for x in range(self.maze.config.height)
                if not self.is_around_drawing(x, "line")
            ]
        )
        self.pos_col = random.choice(
            [
                x
                for x in range(self.maze.config.width)
                if not self.is_around_drawing(x, "col")
            ]
        )
        index = [0, 0]
        old_index = 0
        tab_line = [
            x for x in range(self.pos_line, self.maze.config.height)
        ] + [x for x in range(self.pos_line - 1, -1, -1)]
        tab_col = [x for x in range(self.pos_col, self.maze.config.width)] + [
            x for x in range(self.pos_col - 1, -1, -1)
        ]
        while self.nb_cell_to_fill - 1 != 0:
            if not [
                x
                for x in self.maze.dir
                if self.is_a_possible_way(x, [self.pos_line, self.pos_col])
            ]:
                old_index = index[0]
                last_check_pos = self.find_incomplete_cell(
                    tab_line, tab_col, index
                )
                if old_index != index[0]:
                    tab_line = tab_line[index[0]:]
                if not last_check_pos:
                    return
                self.pos_line = last_check_pos[0]
                self.pos_col = last_check_pos[1]
            else:
                self.draw_path()
                if self.maze.config.animate_generation:
                    self.maze.print_maze_on_terminal("Generating the maze...")
