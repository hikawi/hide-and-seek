from agent import Agent
from vector2d import vector
from typing import TYPE_CHECKING
from map_state import CellType

import random
import heapq

if TYPE_CHECKING:
    from hide_and_seek import Game

# The interval at which the hider shoots out an alert flare.
# This is to notify the seeker.
FLARE_INTERVAL = 10

# The range of squares that flares can be shot in.
FLARE_RANGE = 2


class Hider(Agent):
    """An agent that hides. While the seeker uses a heatmap to move to the hotspots in the FEWEST steps
       possible, the hider uses a heatmap to move to coldspots with the COLDEST path."""

    ticks_passed: int = 0

    def choose_flare_positions(self) -> vector:
        """Yields a flare position."""
        positions: list[vector] = []
        for dx in range(-FLARE_RANGE, FLARE_RANGE + 1):
            for dy in range(-FLARE_RANGE, FLARE_RANGE + 1):
                pos = self.position + vector(dx, dy)
                if pos == self.position or self.view[pos] != CellType.EMPTY:
                    continue
                positions.append(self.position + vector(dx, dy))
        return random.choice(positions)

    def perceive(self, game: 'Game') -> None:
        """Perceives the world."""
        for cell in self.get_neighbors(self.position, self.vision_range):
            # Uh oh, out of bounds.
            if self.view[cell] == CellType.BORDER or not self.can_see(cell):
                continue

            if not game.is_there_seeker(cell):
                self.heatmap[cell.y][cell.x] += 1  # Heat up slightly.
                continue

            # Oh no. A seeker.
            # Heat up ALL cells around it.
            for pos in self.get_neighbors(cell, game.seeker.max_step):
                if self.view[pos] != CellType.EMPTY:
                    continue
                self.heatmap[pos.y][pos.x] += 2  # Heat up more.

            # There's no concept of cooling down for the hider.

    def perceive_flare(self, flare: vector) -> None:
        """Perceives a flare."""
        for pos in self.get_neighbors(flare, FLARE_RANGE):
            if self.view[pos] != CellType.EMPTY:
                continue
            self.heatmap[pos.y][pos.x] += 2  # Heat up more.

    def heuristic(self, cur: vector, goals: set[vector]) -> float:
        """Returns the heuristic value of the current position to the goal."""
        return max([cur.taxicab(goal) for goal in goals])

    def multi_astar(self, goals: set[vector]) -> vector:
        """Launches a multi A* search, that finds the COLDEST path to ONE of the goals."""
        open_set: list[tuple[float, vector]] = [(0, self.position)]
        parents: dict[vector, vector] = {}
        g_score: dict[vector, float] = {self.position: 0}

        while open_set:
            # Pop the current position.
            cur = heapq.heappop(open_set)[1]

            # Found a goal, return the path.
            if cur in goals:
                print(f"Found goal at {cur} in {len(goals)} goals.")
                path: list[vector] = []
                while cur != self.position:
                    path.append(cur)
                    cur = parents[cur]
                return path[-1] - self.position

            for neighbor in self.get_moveset(cur):
                # If the neighbor is out of bounds, or is a wall, skip it.
                if self.view[neighbor] == CellType.BORDER or self.view[neighbor] == CellType.WALL:
                    continue

                # Calculate the new g score.
                new_g = g_score[cur] + self.heatmap[neighbor.y][neighbor.x]

                # If the new g score is better than the old one, update it.
                if new_g < g_score.get(neighbor, float('inf')):
                    g_score[neighbor] = new_g
                    f_score = new_g + self.heuristic(neighbor, goals)
                    heapq.heappush(open_set, (f_score, neighbor))
                    parents[neighbor] = cur

        return vector(0, 0)

    def accept(self, game: 'Game') -> vector:
        """Accepts the current world state, and retrieves the next move."""

        # Shoots a flare every FLARE_INTERVAL ticks.
        self.ticks_passed += 1
        if self.ticks_passed % FLARE_INTERVAL == 0:
            game.shoot_flare(self.choose_flare_positions(), FLARE_INTERVAL)

        # Ravel the heatmap into a list.
        raveled = [cell for row in self.heatmap for cell in row]

        # Pop ALL hottest cells, and calculate the best direction to move to.
        lowest_temp: int = min(raveled)
        coldest_cells: set[vector] = set([vector(x, y) for y in range(len(self.heatmap))
                                          for x in range(len(self.heatmap[y])) if self.heatmap[y][x] == lowest_temp
                                          and self.view[vector(x, y)] == CellType.EMPTY])

        # Now the hider can't really move.
        return self.multi_astar(coldest_cells)

    pass
