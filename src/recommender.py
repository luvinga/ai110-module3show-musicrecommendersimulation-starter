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

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k Song objects ranked by compatibility with user's profile."""
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable string explaining why song was recommended to user."""
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Read a CSV of songs and return a list of dicts with typed numeric fields."""
    import csv
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    print(f"Loaded songs: {len(songs)}")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against a user's preferences.

    Scoring algorithm (EXPERIMENT — Weight Shift):
      +1.0  genre match        (was +2.0, halved to reduce genre dominance)
      +1.5  mood match         (unchanged)
      +0.0–2.0  energy proximity  (2.0 * (1.0 - |song_energy - user_energy|), doubled)

    Max score unchanged at 4.5 — weights redistributed, not inflated.

    Returns:
        (score, reasons)  where reasons is a list of human-readable strings.
    """
    score = 0.0
    reasons: List[str] = []

    if song["genre"].lower() == user_prefs.get("genre", "").lower():
        score += 1.0
        reasons.append(f"genre match (+1.0)")

    if song["mood"].lower() == user_prefs.get("mood", "").lower():
        score += 1.5
        reasons.append(f"mood match (+1.5)")

    target_energy = float(user_prefs.get("energy", 0.5))
    energy_score = round(2.0 * (1.0 - abs(song["energy"] - target_energy)), 3)
    score += energy_score
    reasons.append(f"energy proximity {song['energy']:.2f} vs {target_energy:.2f} (+{energy_score:.2f})")

    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py

    Uses sorted() (not .sort()) so the original songs list is never mutated —
    sorted() returns a brand-new list while .sort() modifies in place.
    """
    scored = [
        (song, score, ", ".join(reasons))
        for song in songs
        for score, reasons in [score_song(user_prefs, song)]
    ]
    return sorted(scored, key=lambda x: x[1], reverse=True)[:k]
