from map_state import MapState, CellType
from seeker import Seeker
from hider import Hider
from vector2d import vector


class Game:
    """Represents a game of Hide and Seek.
       Level 1: One hider, one seeker. Infinite time. Hider may not move.
       Level 2: Multiple hiders, one seeker. Infinite time. Hiders may not move.
       Level 3: Multiple hiders, one seeker. Limited time. Hiders may move.
       Level 4: Multiple hiders, one seeker. Limited time. Hiders may move boxes before game starts. Seeker may move boxes."""

    state: MapState
    score: int
    time_elapsed: int
    maximum_time: int
    flares: dict[vector, int]
    turn: bool

    seeker: Seeker
    hiders: list[Hider]

    def __init__(self, start: MapState, max_time: int) -> None:
        self.state = start
        self.time_elapsed = 0
        self.score = 50
        self.maximum_time = max_time
        self.flares = {}
        self.turn = False

    def start_game(self, seeker: Seeker, hiders: list[Hider]) -> None:
        """Starts the game with the seeker and hiders."""
        self.seeker = seeker
        self.hiders = hiders

    def is_there_hider(self, pos: vector) -> bool:
        """Checks if there is a hider at the position pos."""
        for hider in self.hiders:
            if hider.position == pos:
                return True
        return False

    def is_there_seeker(self, pos: vector) -> bool:
        """Checks if there is a seeker at the position pos."""
        return self.seeker.position == pos

    def terminal_score(self) -> int:
        """Returns the score of the game, if the game is over."""
        if self.time_elapsed > self.maximum_time:
            return -1  # Hiders win.
        if len(self.hiders) == 0:
            return 1  # Seeker wins.
        return 0  # Game is not over.

    def tick_seeker(self) -> None:
        """Tells the seeker to move."""
        self.seeker.perceive(self)
        next_dir = self.seeker.accept(self)
        self.seeker.move(next_dir)

    def tick_hiders(self) -> None:
        """Tells the hiders to move."""
        for hider in self.hiders:
            hider.perceive(self)
            next_dir = hider.accept(self)
            hider.move(next_dir)

    def tick_score(self) -> None:
        """Ticks the score."""
        self.score -= 1
        self.time_elapsed += 1

    def shoot_flare(self, where: vector, interval: int) -> None:
        """Shoots a flare at the position where."""
        self.seeker.perceive_flare(where)
        for hider in self.hiders:
            hider.perceive_flare(where)

        self.flares[where] = self.time_elapsed + interval
        print(f"Flare shot at {where} at {self.time_elapsed}s.")

    def check_world(self) -> None:
        """Attempts to check the world if seeker caught anything."""
        hiders_left: list[Hider] = []
        for hider in self.hiders:
            # This hider has been caught!
            if self.seeker.position == hider.position:
                self.score += 20

                # Remove the heated cell.
                self.seeker.heatmap[hider.position.y][hider.position.x] = -1
                continue

            # If not caught, add to the list.
            hiders_left.append(hider)
        self.hiders = hiders_left

        # Also, remove the flare cells if expired.
        self.flares = {k: v for k, v in self.flares.items() if v >
                       self.time_elapsed}

    def tick(self) -> None:
        """Ticks the game 1 state forward."""
        if self.terminal_score() != 0:
            return

        self.tick_score()
        self.tick_seeker()
        self.check_world()
        self.tick_hiders()

    def print_rep(self) -> None:
        """Prints the representation of the game."""
        print("---------------------------------------")
        print(f"{len(self.hiders)} left, {self.time_elapsed}s elapsed\n")

        seeker = self.seeker.position
        hiders = set([hider.position for hider in self.hiders])

        perceived = set(filter(lambda pos: self.seeker.can_see(pos),
                        self.seeker.get_neighbors(self.seeker.position, self.seeker.vision_range)))

        for y in range(len(self.state.current_map)):
            for x in range(len(self.state.current_map[y])):
                if vector(x, y) == seeker:
                    print("S", end="")
                elif vector(x, y) in hiders:
                    print("H", end="")
                elif vector(x, y) in self.flares:
                    print("*", end="")
                elif self.state[x, y] == CellType.WALL:
                    print("X", end="")
                elif self.state[x, y] == CellType.BOX:
                    print("☐", end="")
                elif vector(x, y) in perceived:
                    print("-", end="")
                else:
                    print(".", end="")
            print()


def game_from_file(file_path: str) -> Game:
    """Reads a game from a file and returns a Game object."""
    try:
        file = open(file_path, "r")

        # First line is the time limit.
        time_limit = int(file.readline().strip())

        # Second line is seeker's vision and step count.
        # Third line is hider's vision and step count.
        seeker_vision, seeker_step = tuple(map(int, file.readline().split()))
        hider_vision, hider_step = tuple(map(int, file.readline().split()))

        # All others are the map.
        map_lines = [line.strip() for line in file.read().splitlines()]

        # All lines must have the same length.
        if len(set(map(len, map_lines))) != 1:
            print(f"Invalid line lengths in file {file_path}.")
            raise ValueError("Invalid map file")

        # Extract information.
        cells: list[list[CellType]] = []
        hiders: list[vector] = []
        seeker: vector | None = None

        for y, line in enumerate(map_lines):
            cell_line: list[CellType] = []
            for x, cell in enumerate(line):
                if cell == "X":
                    cell_line.append(CellType.WALL)
                    continue
                elif cell == ".":
                    cell_line.append(CellType.EMPTY)
                    continue
                elif cell == "H":
                    cell_line.append(CellType.EMPTY)
                    hiders.append(vector(x, y))
                    continue
                elif cell == "S":
                    if seeker:  # Multiple seekers.
                        print(f"Multiple seekers in file {file_path}.")
                        raise ValueError("Invalid map file")

                    cell_line.append(CellType.EMPTY)
                    seeker = vector(x, y)
                    continue
                elif cell == "☐":
                    cell_line.append(CellType.BOX)
                    continue

                print(f"Invalid character {
                      cell} at ({x},{y}) in file {file_path}.")
                raise ValueError("Invalid map file")
            cells.append(cell_line)

        # Check if seeker is present.
        if not seeker:
            print(f"Seeker not found in file {file_path}.")
            raise ValueError("Invalid map file")

        # Create the game.
        state = MapState(cells)
        seeker_agent = Seeker(seeker, seeker_vision, state, seeker_step)
        hider_agents = [Hider(hider, hider_vision, state, hider_step)
                        for hider in hiders]
        game = Game(state, time_limit)
        game.start_game(seeker_agent, hider_agents)
        return game
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        exit(1)
    except ValueError:
        print(f"Invalid format in file {file_path}.")
        exit(1)
