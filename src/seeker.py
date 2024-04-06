from agent import Agent
from vector2d import vector
from map_state import MapState, CellType
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from hide_and_seek import Game

import hider
import heapq


class Seeker(Agent):
    """An agent that has a goal to FIND ALL hiders."""

    pathfinders: dict[tuple[vector, vector], vector] = {}

    def log_heatmap(self) -> None:
        """Logs down the heatmap to a file."""
        with open("test/heatmap.txt", "w") as f:
            for row in self.heatmap:
                for cell in row:
                    f.write(f"{cell:>5}")
                f.write("\n")

    def perceive(self, game: 'Game') -> None:
        """Perceives the world then updates the heatmap accordingly."""
        for cell in self.get_neighbors(self.position, self.vision_range):
            # Uh oh, out of bounds.
            if self.view[cell] == CellType.BORDER or not self.can_see(cell):
                continue

            # If there's a hider, increase the heat.
            if game.is_there_hider(cell):
                self.heatmap[cell.y][cell.x] = 10
            else:
                self.heatmap[cell.y][cell.x] -= 1  # Cool down the cell.

    def perceive_flare(self, flare: vector) -> None:
        """A flare has been shot, update the heatmap accordingly."""

        # A flare has been shot which means there's a hider nearby.
        # Increases heat for a certain radius around the flare.
        for dx in range(-hider.FLARE_RANGE, hider.FLARE_RANGE + 1):
            for dy in range(-hider.FLARE_RANGE, hider.FLARE_RANGE + 1):
                pos = flare + vector(dx, dy)
                if self.view[pos] != CellType.EMPTY:
                    continue
                self.heatmap[pos.y][pos.x] = 1

    def heuristic(self, cur: vector, goals: set[vector]) -> float:
        """Returns the heuristic value of the current position to the goal."""
        return min([cur.taxicab(goal) for goal in goals])

    def multi_astar(self, game: 'Game', goals: set[vector]) -> vector:
        """Performs a breadth-first search to find the shortest path to ANY goal."""

        open_set: list[tuple[float, vector]] = [(0, self.position)]
        parents: dict[vector, vector] = {}
        g_score: dict[vector, float] = {self.position: 0}

        while open_set:
            _, current = heapq.heappop(open_set)

            # Found a goal, return the path.
            if current in goals:
                print(f"Found goal at {current} in {len(goals)} goals.")
                path: list[vector] = []
                while current != self.position:
                    path.append(current)
                    current = parents[current]
                return path[-1] - self.position if path else vector(0, 0)

            # Add all neighbors to the queue.
            for neighbor in self.get_moveset(current):
                if self.view[neighbor] == CellType.WALL or self.view[neighbor] == CellType.BORDER:
                    continue

                tent = g_score[current] + 1
                if tent >= g_score.get(neighbor, float('inf')):
                    continue

                # Add the new position to the queue.
                g_score[neighbor] = tent
                parents[neighbor] = current
                heapq.heappush(open_set,
                               (tent + self.heuristic(neighbor, goals), neighbor))
                parents[neighbor] = current

        # No path to go to where it wants to. Which means the map is enclosed
        # in a way that the seeker can't look for all spots.
        # May also handle this in a way that it looks for a different hotspot
        # to go to instead. But I'm lazy.
        raise ValueError("Come on bro.")

    def accept(self, game: 'Game') -> vector:
        """Accepts the current world state. Returns the NEXT direction it takes."""
        # Ravel the heatmap into a list.
        raveled = [cell for row in self.heatmap for cell in row]

        # Pop ALL hottest cells, and calculate the best direction to move to.
        highest_temp: int = max(raveled)
        hottest_cells: set[vector] = set([vector(x, y) for y in range(len(self.heatmap))
                                          for x in range(len(self.heatmap[y])) if self.heatmap[y][x] == highest_temp
                                          and self.view[vector(x, y)] == CellType.EMPTY])

        direction = self.multi_astar(game, hottest_cells)
        return direction
