from dataclasses import dataclass
from enum import Enum
from typing import Any
from vector2d import vector


class CellType(Enum):
    EMPTY = 0      # An empty cell
    WALL = 1       # A wall cell, this wall CAN NOT be moved.
    BOX = 2        # A box cell, a box can be moved by the player.
    BORDER = 3     # A border cell, this cell is out of bounds.


@dataclass
class MapState:
    """Represents a state of the map. This should be hashable and fast."""

    current_map: list[list[CellType]]
    height: int
    width: int

    def __init__(self, cur_map: list[list[CellType]]) -> None:
        self.current_map = cur_map
        self.height = len(cur_map)
        self.width = len(cur_map[0])

    def validate_coords(self, x: int, y: int) -> bool:
        """Checks if the coordinates are valid."""
        return 0 <= x < self.width and 0 <= y < self.height

    def __getitem__(self, key: Any) -> CellType:
        """Retrieves the cell from the map using key. Key must be of
           type tuple, list or vector. Tuple and list must have 2 keys.
           Returns a BORDER cell if the cell is out of bounds by any chance."""
        try:
            x: int
            y: int

            if (isinstance(key, tuple) or isinstance(key, list)) and len(key) == 2:
                x, y = int(key[0]), int(key[1])
            elif isinstance(key, vector):
                x, y = key.x, key.y
            else:
                raise ValueError("Invalid key type")

            return self.current_map[y][x] if self.validate_coords(x, y) else CellType.BORDER
        except IndexError:
            return CellType.BORDER  # If out of bounds, just return a border cell

        raise ValueError("Invalid key type")

    def __setitem__(self, key: Any, value: CellType) -> None:
        """Sets the cell at the key to the value. Key must be of
           type tuple, list or vector. Tuple and list must have 2 keys."""
        try:
            x: int
            y: int

            if (isinstance(key, tuple) or isinstance(key, list)) and len(key) == 2:
                x, y = int(key[0]), int(key[1])
            elif isinstance(key, vector):
                x, y = key.x, key.y
            else:
                raise ValueError("Invalid key type")

            if self.validate_coords(x, y):
                self.current_map[y][x] = value
        except IndexError:
            raise ValueError("Invalid key")

        raise ValueError("Invalid key type")


def state_from_file(file_path: str) -> MapState:
    """Reads a map from a file and returns a MapState object."""
    cells: list[list[CellType]] = []
    with open(file_path, "r") as file:
        # The first line is the dimensions of the map
        width, height = tuple(map(int, file.readline().split()))
        for _ in range(height):
            line = list(map(lambda x: CellType(int(x)),
                        file.readline().strip().split()))
            if len(line) != width:
                raise ValueError("Invalid map file")
            cells.append(line)
    return MapState(cells)
