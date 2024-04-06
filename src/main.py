from hide_and_seek import game_from_file


def playout(game_map_path: str) -> None:
    """Playout a game from a given map."""
    game = game_from_file(game_map_path)

    while True:
        try:
            game.print_rep()
            if game.terminal_score() == 1:
                print(f"Seeker has won! Score: {game.score}!")
                break
            elif game.terminal_score() == -1:
                print(f"Hiders have won! Score: {game.score}!")
                break

            input()
            game.tick()
        except ValueError:
            print("Game over! The seeker has given up.")
            break


def main() -> None:
    while True:
        print("  Hide and Seek")
        map_path = input("Play map: ")
        if map_path == "quit":
            break
        playout(map_path)


if __name__ == "__main__":
    main()
