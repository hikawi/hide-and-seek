from agent import Agent
from map_state import MapState, CellType
from vector2d import vector
from hide_and_seek import Game, game_from_file

INT_INF = 1_000_000_000


def playout(game_map_path: str) -> None:
    """Playout a game from a given map."""
    game = game_from_file(game_map_path)

    while True:
        game.print_rep()
        if game.terminal_score() == 1:
            print(f"Seeker has won! Score: {game.score}!")
            break
        elif game.terminal_score() == -1:
            print(f"Hiders have won! Score: {game.score}!")
            break

        input()
        game.tick()


def main() -> None:
    # playout("./maps/l1_m1.txt") # LEVEL 1, MAP 1
    playout("./maps/l2_m2.txt")


if __name__ == "__main__":
    main()
