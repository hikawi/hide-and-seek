from vector2d import vector
from map_state import MapState, CellType

DIRECTIONS = [vector(x, y) for x in range(-1, 2)
              for y in range(-1, 2) if (x, y) != (0, 0)]


class Agent:
    """Represents an abstract agent that may move, and can see a certain distance."""

    position: vector
    vision_range: int
    heatmap: list[list[int]]
    view: MapState
    max_step: int

    def __init__(self, pos: vector, vision_range: int, view: MapState, max_step: int) -> None:
        """Initializes a general agent, with starting point pos,
           limited vision range vision_range, and the dimensions of the map."""
        self.position = pos
        self.vision_range = vision_range
        self.view = view
        self.heatmap = [[0 for _ in range(view.width)]
                        for _ in range(view.height)]
        self.max_step = max_step

    def get_neighbors(self, at: vector, radius: int) -> list[vector]:
        """Returns the positions in the NxN grid around the agent."""
        return [vector(x, y) for x in range(at.x - radius, at.x + radius + 1)
                for y in range(at.y - radius, at.y + radius + 1)]

    def get_moveset(self, at: vector) -> list[vector]:
        """Retrieves the moveset at a certain position, with the agent's max step."""
        current: list[vector] = [at]
        for _ in range(self.max_step):
            new = []
            for pos in current:
                for move in DIRECTIONS:
                    new_pos = pos + move
                    if self.view[new_pos] == CellType.WALL or self.view[new_pos] == CellType.BORDER:
                        continue
                    new.append(new_pos)
            current = list(set(new))
        return current

    def move(self, direction: vector) -> bool:
        """Attempts to move the current agent in the direction dir. 
           Returns True if successful, False otherwise."""
        new_pos = self.position + direction
        if self.view[new_pos] == CellType.WALL or self.view[new_pos] == CellType.BORDER:
            print("Can't move here.")
            return False  # Can not move here.

        # Moved successfully.
        self.position = new_pos
        return True

    def can_see(self, pos: vector) -> bool:
        """Checks if this agent is able to see the position pos."""

        # An agent can view an NxN grid around itself, if the x or y distance is
        # OUTSIDE the vision range, the agent can NOT see the position.
        # .........
        # ..-----..
        # ..-----..
        # ..--A--..
        # ..-----..
        # ..-----..
        # .........
        # For example, the agent A can see the positions marked with -, with vision = 2.

        # That means, once we take a distance vector from the agent to the position (end - start),
        # If any components > vision_range, the agent can NOT see the position.
        dist_vec = pos - self.position
        if abs(dist_vec.x) > self.vision_range or abs(dist_vec.y) > self.vision_range:
            return False

        # If on the same tile, obviously the agent can see the position.
        if self.position == pos:
            return True

        # The number of steps to check (no reason to choose this algo).
        steps = max(abs(dist_vec.x), abs(dist_vec.y))
        # The direction to move in.
        direction = dist_vec.free() / steps
        cur = self.position.free()                    # The starting position.

        for i in range(steps):
            cur += direction
            cell = self.view[cur.snap()]
            if cell == CellType.WALL and i != steps - 1:
                return False  # If we hit a wall, we can't see the position.
            if cell == CellType.BORDER:
                return True  # Out of bounds cell, we hit the edge.
        return True  # We can see the position.
