"""Core logic for the content-based music recommender simulation."""

import csv

# --- Scoring weights (our "Algorithm Recipe") ---
GENRE_WEIGHT = 1.5
MOOD_WEIGHT = 1.5
ENERGY_WEIGHT = 2.0
DANCEABILITY_WEIGHT = 1.0
ACOUSTICNESS_WEIGHT = 1.0

NUMERIC_FIELDS = ("energy", "tempo_bpm", "danceability", "acousticness")


def load_songs(filepath="data/songs.csv"):
    """Read songs.csv and return a list of song dicts with numeric fields converted."""
    songs = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for field in NUMERIC_FIELDS:
                if field in row and row[field] != "":
                    row[field] = float(row[field])
            songs.append(row)
    return songs


def _similarity_points(target, actual, weight):
    """Give up to `weight` points based on how close actual is to target (0.0-1.0 scale)."""
    if target is None or actual is None:
        return 0.0
    gap = abs(float(target) - float(actual))
    gap = min(gap, 1.0)  # clamp in case of odd inputs
    return round((1 - gap) * weight, 2)


def score_song(user_prefs, song):
    """Score a single song against a user's taste profile. Returns (score, reasons)."""
    score = 0.0
    reasons = []

    # Genre match
    fav_genre = user_prefs.get("favorite_genre")
    if fav_genre and song.get("genre", "").lower() == fav_genre.lower():
        score += GENRE_WEIGHT
        reasons.append(f"genre match (+{GENRE_WEIGHT})")

    # Mood match
    fav_mood = user_prefs.get("favorite_mood")
    if fav_mood and song.get("mood", "").lower() == fav_mood.lower():
        score += MOOD_WEIGHT
        reasons.append(f"mood match (+{MOOD_WEIGHT})")

    # Energy closeness
    target_energy = user_prefs.get("target_energy")
    if target_energy is not None:
        pts = _similarity_points(target_energy, song.get("energy"), ENERGY_WEIGHT)
        if pts > 0:
            score += pts
            reasons.append(f"energy closeness (+{pts})")

    # Danceability closeness (optional preference)
    target_dance = user_prefs.get("target_danceability")
    if target_dance is not None:
        pts = _similarity_points(target_dance, song.get("danceability"), DANCEABILITY_WEIGHT)
        if pts > 0:
            score += pts
            reasons.append(f"danceability closeness (+{pts})")

    # Acousticness closeness (optional preference)
    target_acoustic = user_prefs.get("target_acousticness")
    if target_acoustic is not None:
        pts = _similarity_points(target_acoustic, song.get("acousticness"), ACOUSTICNESS_WEIGHT)
        if pts > 0:
            score += pts
            reasons.append(f"acousticness closeness (+{pts})")

    return round(score, 2), reasons


def recommend_songs(user_prefs, songs, k=5):
    """Score every song, then return the top k as (song, score, reasons) tuples, highest first."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, reasons))

    # sorted() returns a new list and lets us sort by a key without mutating `scored`
    ranked = sorted(scored, key=lambda item: item[1], reverse=True)
    return ranked[:k]
