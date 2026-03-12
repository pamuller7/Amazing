from typing import Any, Tuple, List


class Vector2:
    """An immutable-style 2-D integer vector with basic arithmetic support.

    Attributes:
        x: Horizontal component (column index in most contexts).
        y: Vertical component (row index in most contexts).
    """

    def __init__(self, x: int, y: int) -> None:
        """Initialise the vector with the given components.

        Args:
            x: Horizontal component.
            y: Vertical component.
        """
        self.x = x
        self.y = y

    def __add__(self, rhs: Any) -> "Vector2":
        """Return the element-wise sum of two vectors.

        Args:
            rhs: Another ``Vector2`` to add.

        Returns:
            A new ``Vector2`` whose components are the sums.

        Raises:
            ValueError: If *rhs* is not a ``Vector2``.
        """
        if not isinstance(rhs, Vector2):
            raise ValueError(
                "+ operator not supported between Vector2 and {}".format(
                    type(rhs)
                )
            )
        return Vector2(self.x + rhs.x, self.y + rhs.y)

    def __sub__(self, rhs: Any) -> "Vector2":
        """Return the element-wise difference of two vectors.

        Args:
            rhs: Another ``Vector2`` to subtract.

        Returns:
            A new ``Vector2`` whose components are the differences.

        Raises:
            ValueError: If *rhs* is not a ``Vector2``.
        """
        if not isinstance(rhs, Vector2):
            raise ValueError(
                "- operator not supported between Vector2 and {}".format(
                    type(rhs)
                )
            )
        return Vector2(self.x - rhs.x, self.y - rhs.y)

    def __eq__(self, rhs: object) -> bool:
        """Check component-wise equality with another vector.

        Args:
            rhs: Object to compare against.

        Returns:
            ``True`` when both components are equal.

        Raises:
            ValueError: If *rhs* is not a ``Vector2``.
        """
        if not isinstance(rhs, Vector2):
            raise ValueError(
                "== operator not supported between Vector2 and {}".format(
                    type(rhs)
                )
            )
        return rhs.x == self.x and rhs.y == self.y

    def __str__(self) -> str:
        """Return a human-readable representation of the vector."""
        return f"Vector2({self.x}, {self.y})"

    def __repr__(self) -> str:
        """Return the same string as ``__str__``."""
        return str(self)

    def __hash__(self) -> int:
        """Return a hash based on the ``(x, y)`` tuple."""
        return hash((self.x, self.y))

    def as_tuple(self) -> Tuple[int, int]:
        """Return the vector as a plain ``(x, y)`` tuple."""
        return self.x, self.y

    @classmethod
    def from_iter(cls, tup: Tuple[int, int] | List[int]) -> "Vector2":
        """Construct a ``Vector2`` from a two-element sequence.

        Args:
            tup: Any two-element sequence whose first element becomes *x*
                and second becomes *y*.

        Returns:
            A new ``Vector2`` instance.
        """
        return cls(tup[0], tup[1])

    def inverted(self) -> "Vector2":
        """Return a new vector with *x* and *y* swapped.

        Returns:
            ``Vector2(self.y, self.x)``.
        """
        return Vector2(self.y, self.x)
