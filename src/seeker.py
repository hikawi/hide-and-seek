from agent import Agent
from vector2d import vector
from map_state import MapState, CellType
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from hide_and_seek import Game

import hider
import heapq

DIRECTIONS = [vector(1, 0), vector(-1, 0), vector(0, 1), vector(0, -1),
              vector(1, 1), vector(-1, -1), vector(1, -1), vector(-1, 1)]


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
        for cell in self.get_perceivables():
            # Uh oh, out of bounds.
            if self.view[cell] == CellType.BORDER or not self.can_see(cell):
                continue

            # If there's a hider, increase the heat.
            if game.is_there_hider(cell):
                self.heatmap[cell.y][cell.x] += 1
            else:
                self.heatmap[cell.y][cell.x] -= 1  # Cool down the cell.
        self.log_heatmap()

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

    def multi_astar(self, goals: set[vector]) -> vector:
        """Performs a breadth-first search to find the shortest path to ANY goal."""

        open_set: list[tuple[float, vector]] = [(0, self.position)]
        parents: dict[vector, vector] = {}
        g_score: dict[vector, float] = {self.position: 0}

        while open_set:
            _, current = heapq.heappop(open_set)

            # Found a goal, return the path.
            if current in goals:
                print(f"Found goal at {current}.")
                path: list[vector] = []
                while current != self.position:
                    path.append(current)
                    current = parents[current]
                return path[-1] - self.position

            # Add all neighbors to the queue.
            for direction in DIRECTIONS:
                new_pos = current + direction
                if self.view[new_pos] == CellType.WALL or self.view[new_pos] == CellType.BORDER:
                    continue

                tent = g_score[current] + 1
                if tent >= g_score.get(new_pos, float('inf')):
                    continue

                # Add the new position to the queue.
                g_score[new_pos] = tent
                parents[new_pos] = current
                heapq.heappush(open_set,
                               (tent + self.heuristic(new_pos, goals), new_pos))
                parents[new_pos] = current

        raise ValueError("Come on bro.")

    def accept(self) -> vector:
        """Accepts the current world state. Returns the NEXT direction it takes."""
        # Ravel the heatmap into a list.
        raveled = [cell for row in self.heatmap for cell in row]

        # Pop ALL hottest cells, and calculate the best direction to move to.
        highest_temp: int = max(raveled)
        hottest_cells: set[vector] = set([vector(x, y) for y in range(len(self.heatmap))
                                          for x in range(len(self.heatmap[y])) if self.heatmap[y][x] == highest_temp
                                          and self.view[vector(x, y)] == CellType.EMPTY])

        direction = self.multi_astar(hottest_cells)
        return direction
