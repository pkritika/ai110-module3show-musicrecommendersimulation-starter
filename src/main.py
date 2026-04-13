"""
Command line runner for the Music Recommender Simulation.
Runs multiple user profiles to stress-test the recommender system.

Functions implemented in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs

# ── ANSI colour helpers (no external dependencies) ────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
RED    = "\033[91m"
DIM    = "\033[2m"
MAGENTA= "\033[95m"
LINE   = "─" * 58

# ── User Profiles ─────────────────────────────────────────────────────────────
# Normal profiles
PROFILE_POP_HAPPY = {
    "_label":       "🎉  High-Energy Pop",
    "genre":        "pop",
    "mood":         "happy",
    "energy":       0.80,
    "acousticness": 0.08,
    "valence":      0.80,
    "tempo_bpm":    120,
}

PROFILE_CHILL_LOFI = {
    "_label":       "☕  Chill Lofi",
    "genre":        "lofi",
    "mood":         "chill",
    "energy":       0.35,
    "acousticness": 0.80,
    "valence":      0.58,
    "tempo_bpm":    76,
}

PROFILE_INTENSE_ROCK = {
    "_label":       "🤘  Deep Intense Rock",
    "genre":        "rock",
    "mood":         "intense",
    "energy":       0.90,
    "acousticness": 0.08,
    "valence":      0.45,
    "tempo_bpm":    152,
}

# Adversarial / edge-case profiles
PROFILE_SAD_HIGH_ENERGY = {
    "_label":       "⚡  Adversarial: High Energy + Sad Mood",
    "_note":        "energy=0.9 wants intensity, mood='sad' wants sadness — very few songs live here",
    "genre":        "blues",
    "mood":         "sad",
    "energy":       0.90,
    "acousticness": 0.50,
    "valence":      0.25,
    "tempo_bpm":    130,
}

PROFILE_CHILL_GENRE_MISMATCH = {
    "_label":       "🎻  Adversarial: Classical + High Energy",
    "_note":        "classical has only one song (energy=0.22) — max energy request will be ignored by genre",
    "genre":        "classical",
    "mood":         "focused",
    "energy":       0.95,
    "acousticness": 0.90,
    "valence":      0.50,
    "tempo_bpm":    160,
}

PROFILE_GENRE_ORPHAN = {
    "_label":       "🎷  Adversarial: Obscure Genre (jazz) + Opposite Numerics",
    "_note":        "jazz has 1 song with low energy/tempo — but asking for high energy: genre bonus wins anyway",
    "genre":        "jazz",
    "mood":         "intense",
    "energy":       0.99,
    "acousticness": 0.02,
    "valence":      0.90,
    "tempo_bpm":    168,
}

PROFILE_ALL_MAXED = {
    "_label":       "🔥  Adversarial: All Features Maxed to 1.0",
    "_note":        "no real song matches — tests if system degrades gracefully or clumps results",
    "genre":        "EDM",
    "mood":         "energetic",
    "energy":       1.00,
    "acousticness": 0.00,
    "valence":      1.00,
    "tempo_bpm":    168,
}

ALL_PROFILES = [
    PROFILE_POP_HAPPY,
    PROFILE_CHILL_LOFI,
    PROFILE_INTENSE_ROCK,
    PROFILE_SAD_HIGH_ENERGY,
    PROFILE_CHILL_GENRE_MISMATCH,
    PROFILE_GENRE_ORPHAN,
    PROFILE_ALL_MAXED,
]


def is_adversarial(profile: dict) -> bool:
    return "_note" in profile


def print_profile_header(profile: dict) -> None:
    colour = RED if is_adversarial(profile) else CYAN
    print(f"\n{BOLD}{colour}{'═' * 58}{RESET}")
    print(f"{BOLD}{colour}  {profile['_label']}{RESET}")
    if "_note" in profile:
        print(f"  {DIM}⚠  {profile['_note']}{RESET}")
    print(f"{colour}{'═' * 58}{RESET}")
    print(
        f"{DIM}  genre: {profile['genre']} | mood: {profile['mood']} | "
        f"energy: {profile['energy']} | tempo: {profile.get('tempo_bpm', '–')} BPM{RESET}"
    )
    print(f"{DIM}  {LINE}{RESET}\n")


def print_recommendation(rank: int, song: dict, score: float, explanation: str) -> None:
    filled = int((score / 7.0) * 20)
    bar = f"{GREEN}{'█' * filled}{'░' * (20 - filled)}{RESET}"

    print(f"  {BOLD}{YELLOW}#{rank}  {song['title']}{RESET}  {DIM}by {song['artist']}{RESET}")
    print(f"      Genre: {song['genre']}  |  Mood: {song['mood']}")
    print(f"      Score: {BOLD}{score:.2f} / 7.00{RESET}  {bar}")
    print(f"      {DIM}Why:{RESET}")
    for reason in explanation.split(" | "):
        print(f"        {DIM}·{RESET} {reason}")
    print(f"  {DIM}{LINE}{RESET}")


def run_profile(songs: list, profile: dict, k: int = 3) -> None:
    user_prefs = {k: v for k, v in profile.items() if not k.startswith("_")}
    recommendations = recommend_songs(user_prefs, songs, k=k)

    print_profile_header(profile)

    if not recommendations:
        print(f"  {RED}No songs met the scoring threshold!{RESET}")
        print(f"  {DIM}This means every song scored below 1.5/7.0 — the profile is too restrictive.{RESET}\n")
        return

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print_recommendation(rank, song, score, explanation)


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"\n{BOLD}{MAGENTA}  🧪  Stress Testing — {len(ALL_PROFILES)} Profiles{RESET}")

    for profile in ALL_PROFILES:
        run_profile(songs, profile, k=3)

    print(f"\n  {DIM}Tip: add or edit profiles in src/main.py to explore more.{RESET}\n")


if __name__ == "__main__":
    main()
