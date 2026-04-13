"""
Command line runner for the Music Recommender Simulation.

Runs the recommender against multiple user profiles:
  - Three "normal" profiles: High-Energy Pop, Chill Lofi, Deep Intense Rock
  - Four adversarial/edge-case profiles designed to stress-test scoring logic
"""

import os
from recommender import load_songs, recommend_songs

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# Named user preference dictionaries
# ---------------------------------------------------------------------------

# Standard profiles
HIGH_ENERGY_POP = {"genre": "pop", "mood": "happy", "energy": 0.9}
CHILL_LOFI      = {"genre": "lofi", "mood": "chill", "energy": 0.35}
DEEP_INTENSE_ROCK = {"genre": "rock", "mood": "intense", "energy": 0.95}

# Adversarial / edge-case profiles
# 1. Conflicting energy vs. mood — max energy but melancholic mood
CONFLICTING_ENERGY_MOOD = {"genre": "pop", "mood": "melancholic", "energy": 0.9}

# 2. Ghost genre — genre that exists in no song, so genre match never fires
UNKNOWN_GENRE = {"genre": "vaporwave", "mood": "happy", "energy": 0.7}

# 3. Zero energy — minimum possible energy preference
ZERO_ENERGY = {"genre": "lofi", "mood": "chill", "energy": 0.0}

# 4. All-wildcards — empty strings + mid energy; tests graceful degradation
EMPTY_PREFS = {"genre": "", "mood": "", "energy": 0.5}

PROFILES = [
    ("High-Energy Pop",       HIGH_ENERGY_POP),
    ("Chill Lofi",            CHILL_LOFI),
    ("Deep Intense Rock",     DEEP_INTENSE_ROCK),
    ("[ADVERSARIAL] Conflicting Energy+Mood",  CONFLICTING_ENERGY_MOOD),
    ("[ADVERSARIAL] Unknown Genre (vaporwave)", UNKNOWN_GENRE),
    ("[ADVERSARIAL] Zero Energy",              ZERO_ENERGY),
    ("[ADVERSARIAL] Empty Preferences",        EMPTY_PREFS),
]


def print_results(label: str, user_prefs: dict, recommendations: list) -> None:
    width = 60
    print()
    print("=" * width)
    print(f"  Profile : {label}")
    print(f"  Prefs   : genre={user_prefs.get('genre')!r}  "
          f"mood={user_prefs.get('mood')!r}  "
          f"energy={user_prefs.get('energy')}")
    print("=" * width)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n  #{rank}  {song['title']}  —  {song['artist']}")
        print(f"       Genre/Mood : {song['genre']} / {song['mood']}")
        print(f"       Energy     : {song['energy']:.2f}")
        print(f"       Score      : {score:.2f}")
        print(f"       Why        : {explanation}")
    print()


def main() -> None:
    songs = load_songs(os.path.join(_ROOT, "data", "songs.csv"))

    for label, prefs in PROFILES:
        recs = recommend_songs(prefs, songs, k=5)
        print_results(label, prefs, recs)

    print("=" * 60)
    print("  Done — all profiles evaluated.")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
