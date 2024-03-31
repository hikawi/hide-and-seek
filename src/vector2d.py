from dataclasses import dataclass
from math import sqrt
from typing import Generator


@dataclass
class vectorf:
    """A vector but with floating point components. Please do not use this for cells."""

    x: float
    y: float

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __add__(self, other: 'vectorf') -> 'vectorf':
        """Adds two vectors together, returning a new vector."""
        return vectorf(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'vectorf') -> 'vectorf':
        """Subtracts two vectors, returning a new vector."""
        return vectorf(self.x - other.x, self.y - other.y)

    def __truediv__(self, other: float) -> 'vectorf':
        """Divides the vector by a scalar, returning a new vector. If the scalar is 0, returns a zero vector."""
        return vectorf(self.x / other, self.y / other) if other != 0.0 else vectorf(0.0, 0.0)

    def snap(self) -> 'vector':
        """Snaps the vector to integer values, restricting its freedom."""
        return vector(round(self.x), round(self.y))

    def normal(self) -> 'vectorf':
        """Returns the normalized vector."""
        length = sqrt(self.x ** 2 + self.y ** 2)
        return vectorf(self.x / length, self.y / length)


@dataclass
class vector:
    """A vector with integer components. Use this for cells and agents stuff."""

    x: int
    y: int

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __add__(self, other: 'vector') -> 'vector':
        """Adds two vectors together, returning a new vector."""
        return vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'vector') -> 'vector':
        """Subtracts two vectors, returning a new vector."""
        return vector(self.x - other.x, self.y - other.y)

    def __iter__(self) -> Generator[int, None, None]:
        """Returns an iterator for the vector."""
        yield self.x
        yield self.y

    def __lt__(self, __value: object) -> bool:
        """Returns True if the vector is less than another vector."""
        if not isinstance(__value, vector):
            return False
        return self.x < __value.x and self.y < __value.y

    def __hash__(self) -> int:
        """Returns the hash of the vector."""
        return hash((self.x, self.y))

    def __eq__(self, __value: object) -> bool:
        """Returns True if the vector is equal to another vector."""
        if not isinstance(__value, vector):
            return False
        return self.x == __value.x and self.y == __value.y

    def free(self) -> vectorf:
        """Frees the SHACKLES of INTEGERS, allowing this vector to be used with floats."""
        return vectorf(float(self.x), float(self.y))

    def length_squared(self) -> int:
        """Returns the squared length of the vector."""
        return self.x ** 2 + self.y ** 2

    def taxicab(self, other: 'vector') -> float:
        """Returns the taxicab distance between two vectors."""
        return abs(self.x - other.x) + abs(self.y - other.y)
