"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

Functions implemented in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs

# ── ANSI colour helpers (no external dependencies) ───────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
DIM    = "\033[2m"
LINE   = "─" * 56


def print_header(user_prefs: dict) -> None:
    print(f"\n{BOLD}{CYAN}{'═' * 56}{RESET}")
    print(f"{BOLD}{CYAN}  🎵  Music Recommender — Top Picks For You{RESET}")
    print(f"{BOLD}{CYAN}{'═' * 56}{RESET}")
    print(f"{DIM}  User profile → genre: {user_prefs['genre']} | "
          f"mood: {user_prefs['mood']} | energy: {user_prefs['energy']}{RESET}")
    print(f"{DIM}  {LINE}{RESET}\n")


def print_recommendation(rank: int, song: dict, score: float, explanation: str) -> None:
    # Build a simple score bar (max score ~7.0)
    filled = int((score / 7.0) * 20)
    bar = f"{GREEN}{'█' * filled}{'░' * (20 - filled)}{RESET}"

    print(f"  {BOLD}{YELLOW}#{rank}  {song['title']}{RESET}  {DIM}by {song['artist']}{RESET}")
    print(f"      Genre: {song['genre']}  |  Mood: {song['mood']}")
    print(f"      Score: {BOLD}{score:.2f} / 7.00{RESET}  {bar}")
    print(f"      {DIM}Why:{RESET}")
    for reason in explanation.split(" | "):
        print(f"        {DIM}·{RESET} {reason}")
    print(f"  {DIM}{LINE}{RESET}")


def main() -> None:
    songs = load_songs("data/songs.csv")

    # Default example profile — pop / happy / high energy
    user_prefs = {
        "genre":        "pop",
        "mood":         "happy",
        "energy":       0.8,
        "acousticness": 0.08,
        "valence":      0.80,
        "tempo_bpm":    120,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print_header(user_prefs)

    if not recommendations:
        print("  No recommendations found. Try adjusting your profile.\n")
        return

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print_recommendation(rank, song, score, explanation)

    print(f"\n  {DIM}Tip: edit user_prefs in src/main.py to explore other profiles.{RESET}\n")


if __name__ == "__main__":
    main()
