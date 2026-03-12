from mazegen.vector2 import Vector2
from random import shuffle, choice


class DisjointSet:
    """A single node in a union-find (disjoint-set) data structure.

    Used by the Kruskal algorithm to track which cells belong to the
    same connected component so that only walls between *different*
    components are removed.

    Attributes:
        pos: Grid position this node represents.
        rank: Rank used for union-by-rank optimisation.
        parent: Parent pointer; a root node points to itself.
    """

    def __init__(self, pos: Vector2) -> None:
        """Initialise a new disjoint-set node at *pos*.

        The node starts as its own root (``parent = self``) with rank 0.

        Args:
            pos: Grid position represented by this node.
        """
        self.pos: Vector2 = pos
        self.rank: int = 0
        self.parent: "DisjointSet" = self

    @classmethod
    def at(
        cls, sets: list[list["DisjointSet"]], pos: Vector2
    ) -> "DisjointSet":
        """Return the ``DisjointSet`` node at *pos* without path compression.

        Args:
            sets: 2-D grid of ``DisjointSet`` nodes indexed ``[y][x]``.
            pos: Grid position to look up.

        Returns:
            The node at ``sets[pos.y][pos.x]``.
        """
        return sets[pos.y][pos.x]

    @classmethod
    def find(
        cls, sets: list[list["DisjointSet"]], pos: Vector2
    ) -> "DisjointSet":
        """Find the root of the set containing *pos*, with path compression.

        Uses the two-step path-halving strategy: each node's parent is
        updated to its grandparent while traversing to the root.

        Args:
            sets: 2-D grid of ``DisjointSet`` nodes indexed ``[y][x]``.
            pos: Grid position whose root to find.

        Returns:
            The root ``DisjointSet`` node of the component.
        """
        x = sets[pos.y][pos.x]
        while x != x.parent:
            x.parent = x.parent.parent
            x = x.parent
        return x

    @classmethod
    def merge(
        cls, sets: list[list["DisjointSet"]], pos1: Vector2, pos2: Vector2
    ) -> bool:
        """Merge the sets containing *pos1* and *pos2* if they are disjoint.

        Args:
            sets: 2-D grid of ``DisjointSet`` nodes indexed ``[y][x]``.
            pos1: Grid position of the first cell.
            pos2: Grid position of the second cell.

        Returns:
            ``True`` if the two cells were in different components and the
            merge was performed; ``False`` if they were already connected.
        """
        x = cls.find(sets, pos1)
        y = cls.find(sets, pos2)
        if x is y:
            return False
        x.parent = y
        return True


class Kruskal:
    """Randomised Kruskal maze-generation algorithm.

    Shuffles all interior walls, then removes each wall whose two
    neighbouring cells belong to different connected components.
    Optionally opens extra walls to create loops for imperfect mazes.
    """

    from mazegen.maze import Maze

    @staticmethod
    def get_direction(maze: Maze, move: int) -> Vector2:
        """Convert a direction bitmask to a unit ``Vector2`` offset.

        Args:
            maze: The maze (provides direction constants).
            move: One of ``maze.north``, ``maze.south``, ``maze.east``,
                ``maze.west``.

        Returns:
            The corresponding unit vector (e.g. ``Vector2(0, -1)`` for north).

        """
        if move == maze.north:
            return Vector2(0, -1)
        if move == maze.south:
            return Vector2(0, 1)
        if move == maze.east:
            return Vector2(1, 0)
        if move == maze.west:
            return Vector2(-1, 0)
        return Vector2(0, 0)

    @staticmethod
    def decomp_cell(maze: Maze, cell: int) -> list:
        """Return the open-passage directions for a raw cell value.

        A direction is open when its wall bit is cleared (0).

        Args:
            maze: The maze (provides direction constants).
            cell: Raw integer value from ``maze.maze[line][col]``.

        Returns:
            List of direction bitmasks for every open passage.
        """
        cell_open = []
        if cell & 1 == 0:
            cell_open.append(maze.north)
        if cell >> 1 & 1 == 0:
            cell_open.append(maze.east)
        if cell >> 2 & 1 == 0:
            cell_open.append(maze.south)
        if cell >> 3 & 1 == 0:
            cell_open.append(maze.west)
        return cell_open

    @staticmethod
    def kruskal(maze: Maze) -> None:
        """Generate passages in *maze* using randomised Kruskal's algorithm.

        Builds a disjoint-set forest over all cells, shuffles every
        (cell, direction) wall pair, then removes each wall that separates
        two distinct components.  When ``maze.config.perfect`` is
        ``False``, up to ``max(height, width)`` additional loop walls are
        opened in a second pass to create an imperfect maze.  Animation
        frames are printed to the terminal at each step when
        ``maze.config.animate_generation`` is ``True``.

        Args:
            maze: The ``Maze`` instance to generate paths in
            (mutated in place).
        """
        walls = []
        sets: list[list[DisjointSet]] = [
            [DisjointSet(Vector2(x, y)) for x in range(maze.config.width)]
            for y in range(maze.config.height)
        ]
        for y in range(maze.config.height):
            for x in range(maze.config.width):
                cell_walls = [
                    maze.east,
                    maze.north,
                ]
                walls.extend([(Vector2(x, y), w) for w in cell_walls])
        shuffle(walls)
        for i, (pos, wall) in enumerate(walls):
            cells_dividing: list[Vector2] = [
                pos,
                pos + Kruskal.get_direction(maze, wall),
            ]
            if not maze.is_in_bound(cells_dividing[1]):
                continue
            if maze.maze[cells_dividing[1].y][cells_dividing[1].x] > 0b1111:
                continue
            if maze.maze[cells_dividing[0].y][cells_dividing[0].x] > 0b1111:
                continue
            if DisjointSet.merge(sets, cells_dividing[0], cells_dividing[1]):
                maze.put_in_maze(cells_dividing[0], wall)
                rev = {
                    maze.east: maze.west,
                    maze.west: maze.east,
                    maze.south: maze.north,
                    maze.north: maze.south,
                }
                maze.put_in_maze(cells_dividing[1], rev[wall])
                if maze.config.animate_generation:
                    maze.print_maze_on_terminal("Kruskal generation...", False)
        if not maze.config.perfect:
            count = 0
            shuffle(walls)
            for pos, wall in walls:
                if count < max(maze.config.height, maze.config.width):
                    cell_open_to = Kruskal.decomp_cell(maze, wall)
                    if (
                        len(cell_open_to) < 2
                        and maze.maze[pos.y][pos.x] < 0b1111
                    ):
                        open_wall = [
                            x for x in maze.dir if x not in cell_open_to
                        ]
                        shuffle(open_wall)
                        wall = choice(open_wall)
                        next_cell = pos + Kruskal.get_direction(maze, wall)
                        if (
                            maze.is_in_bound(next_cell)
                            and maze.maze[next_cell.y][next_cell.x] < 0b1111
                        ):
                            maze.put_in_maze(pos, wall)
                            rev = {
                                maze.east: maze.west,
                                maze.west: maze.east,
                                maze.south: maze.north,
                                maze.north: maze.south,
                            }
                            maze.put_in_maze(next_cell, rev[wall])
                            count += 1
                        if maze.config.animate_generation:
                            maze.print_maze_on_terminal(
                                "Kruskal generation...", False
                            )
                else:
                    break
