from agent import Agent
from vector2d import vector
from typing import TYPE_CHECKING
from map_state import CellType

import random

if TYPE_CHECKING:
    from hide_and_seek import Game

# The interval at which the hider shoots out an alert flare.
# This is to notify the seeker.
FLARE_INTERVAL = 10

# The range of squares that flares can be shot in.
FLARE_RANGE = 2


class Hider(Agent):
    """An agent that hides."""

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

    def accept(self, game: 'Game') -> vector:
        """Accepts the current world state, and retrieves the next move."""

        # Shoots a flare every FLARE_INTERVAL ticks.
        self.ticks_passed += 1
        if self.ticks_passed % FLARE_INTERVAL == 0:
            game.shoot_flare(self.choose_flare_positions(), FLARE_INTERVAL)

        # Now the hider can't really move.
        return vector(0, 0)

    pass
