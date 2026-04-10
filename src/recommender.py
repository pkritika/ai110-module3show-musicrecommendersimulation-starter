import csv
import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score_song(self, user: UserProfile, song: Song) -> float:
        """
        Scores a single Song dataclass against a UserProfile.
        Uses the same Algorithm Recipe as score_song() below.
        Max possible score: 7.0
        """
        total = 0.0

        # Categorical bonuses
        if song.genre.lower() == user.favorite_genre.lower():
            total += 2.0
        if song.mood.lower() == user.favorite_mood.lower():
            total += 1.0

        # Energy — weight 1.5, range 0.0–1.0
        total += 1.5 * (1 - abs(song.energy - user.target_energy) / 1.0)

        # Acousticness — weight 1.0: low target if not acoustic, high if acoustic
        target_acousticness = 0.80 if user.likes_acoustic else 0.08
        total += 1.0 * (1 - abs(song.acousticness - target_acousticness) / 1.0)

        # Valence — weight 0.75, neutral target 0.5
        total += 0.75 * (1 - abs(song.valence - 0.5) / 1.0)

        # Tempo — weight 0.75, neutral target 110 BPM, max range 168
        total += 0.75 * (1 - abs(song.tempo_bpm - 110) / 168)

        return total

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns the top-k songs sorted by score, highest first."""
        scored = [(song, self._score_song(user, song)) for song in self.songs]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [song for song, score in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a human-readable explanation of why a song was recommended."""
        reasons = []

        if song.genre.lower() == user.favorite_genre.lower():
            reasons.append(f"genre matches your preference ({song.genre})")
        if song.mood.lower() == user.favorite_mood.lower():
            reasons.append(f"mood matches your preference ({song.mood})")

        energy_diff = abs(song.energy - user.target_energy)
        if energy_diff <= 0.15:
            reasons.append(
                f"energy level is very close to your target "
                f"({song.energy:.2f} vs {user.target_energy:.2f})"
            )
        elif energy_diff <= 0.30:
            reasons.append(
                f"energy level is somewhat close to your target "
                f"({song.energy:.2f} vs {user.target_energy:.2f})"
            )

        if user.likes_acoustic and song.acousticness >= 0.60:
            reasons.append(
                f"has a strong acoustic feel (acousticness: {song.acousticness:.2f})"
            )
        elif not user.likes_acoustic and song.acousticness <= 0.20:
            reasons.append(
                f"has an electronic/plugged-in sound (acousticness: {song.acousticness:.2f})"
            )

        if not reasons:
            reasons.append("it is a reasonable match based on overall audio features")

        return "Recommended because: " + ", ".join(reasons) + "."


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file using Python's csv module.
    Converts numerical fields to float/int so they can be used in scoring math.

    Args:
        csv_path: Path to the CSV file, relative to project root or absolute.

    Returns:
        A list of dictionaries, one per song, with correctly typed values.
    """
    # Resolve path relative to the project root (one level up from src/)
    if not os.path.isabs(csv_path):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(project_root, csv_path)

    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":           int(row["id"]),
                "title":        row["title"],
                "artist":       row["artist"],
                "genre":        row["genre"],
                "mood":         row["mood"],
                "energy":       float(row["energy"]),
                "tempo_bpm":    float(row["tempo_bpm"]),
                "valence":      float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })

    print(f"Loaded songs: {len(songs)}")
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song dictionary against a user preference dictionary.

    Algorithm Recipe (max score = 7.0):
      +2.0 pts  genre match (categorical)
      +1.0 pts  mood match  (categorical)
      +1.5 pts  energy proximity      (numerical, weight 1.5)
      +1.0 pts  acousticness proximity(numerical, weight 1.0)
      +0.75 pts valence proximity     (numerical, weight 0.75)
      +0.75 pts tempo proximity       (numerical, weight 0.75)

    Args:
        user_prefs: Dict with keys — genre, mood, energy, and optionally
                    acousticness, valence, tempo_bpm
        song: Dict loaded from load_songs()

    Returns:
        (total_score, reasons) where reasons is a list of explanation strings.
    """
    total = 0.0
    reasons = []

    # --- Categorical bonuses ---
    if song["genre"].lower() == user_prefs.get("genre", "").lower():
        total += 2.0
        reasons.append(f"genre match ({song['genre']}): +2.00")

    if song["mood"].lower() == user_prefs.get("mood", "").lower():
        total += 1.0
        reasons.append(f"mood match ({song['mood']}): +1.00")

    # --- Numerical proximity scores ---
    # Energy: weight 1.5, range 0.0–1.0
    target_energy = float(user_prefs.get("energy", 0.5))
    energy_score = 1.5 * (1 - abs(song["energy"] - target_energy) / 1.0)
    total += energy_score
    reasons.append(f"energy proximity: +{energy_score:.2f}")

    # Acousticness: weight 1.0, range 0.0–1.0
    target_acousticness = float(user_prefs.get("acousticness", 0.08))
    acousticness_score = 1.0 * (1 - abs(song["acousticness"] - target_acousticness) / 1.0)
    total += acousticness_score
    reasons.append(f"acousticness proximity: +{acousticness_score:.2f}")

    # Valence: weight 0.75, range 0.0–1.0
    target_valence = float(user_prefs.get("valence", 0.5))
    valence_score = 0.75 * (1 - abs(song["valence"] - target_valence) / 1.0)
    total += valence_score
    reasons.append(f"valence proximity: +{valence_score:.2f}")

    # Tempo: weight 0.75, max range 168 BPM
    target_tempo = float(user_prefs.get("tempo_bpm", 110))
    tempo_score = 0.75 * (1 - abs(song["tempo_bpm"] - target_tempo) / 168)
    total += tempo_score
    reasons.append(f"tempo proximity: +{tempo_score:.2f}")

    return (round(total, 4), reasons)


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5
) -> List[Tuple[Dict, float, str]]:
    """
    Scores every song, sorts by score (highest first), filters below a minimum
    threshold, and returns the top k as (song_dict, score, explanation) tuples.

    Args:
        user_prefs: User preference dictionary (see score_song for keys)
        songs: List of song dicts from load_songs()
        k: Maximum number of songs to return

    Returns:
        List of (song_dict, score, explanation_string) tuples, best first.
    """
    THRESHOLD = 1.5  # Minimum score to be included in recommendations

    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        if score >= THRESHOLD:
            explanation = " | ".join(reasons)
            scored.append((song, score, explanation))

    # Ranking rule: sort descending by score
    scored.sort(key=lambda x: x[1], reverse=True)

    return scored[:k]
