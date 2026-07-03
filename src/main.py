"""CLI entry point: loads songs, runs several taste profiles, and prints ranked results."""

from src.recommender import load_songs, recommend_songs

# --- User taste profiles ---

DEFAULT_PROFILE = {
    "favorite_genre": "afrobeats",
    "favorite_mood": "energetic",
    "target_energy": 0.75,
    "target_danceability": 0.8,
}

HIGH_ENERGY_POP = {
    "favorite_genre": "afrobeats",
    "favorite_mood": "energetic",
    "target_energy": 0.9,
    "target_danceability": 0.8,
}

CHILL_LOFI = {
    "favorite_genre": "lofi",
    "favorite_mood": "chill",
    "target_energy": 0.2,
    "target_acousticness": 0.8,
}

DEEP_INTENSE_ROCK = {
    "favorite_genre": "rock",
    "favorite_mood": "intense",
    "target_energy": 0.85,
}

# Adversarial profile: conflicting signals (high energy target + a sad mood preference)
ADVERSARIAL_CONFLICTED = {
    "favorite_genre": "metal",
    "favorite_mood": "sad",
    "target_energy": 0.9,
}


def print_recommendations(title, user_prefs, songs, k=5):
    print(f"\n=== {title} ===")
    print(f"Profile: {user_prefs}")
    print("-" * 60)
    results = recommend_songs(user_prefs, songs, k=k)
    for rank, (song, score, reasons) in enumerate(results, start=1):
        reason_text = ", ".join(reasons) if reasons else "no matching criteria"
        print(f"{rank}. {song['title']} by {song['artist']}  |  score: {score}")
        print(f"   reasons: {reason_text}")


def main():
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    print_recommendations("Default Profile (Afrobeats/Energetic)", DEFAULT_PROFILE, songs)
    print_recommendations("High-Energy Pop", HIGH_ENERGY_POP, songs)
    print_recommendations("Chill Lofi", CHILL_LOFI, songs)
    print_recommendations("Deep Intense Rock", DEEP_INTENSE_ROCK, songs)
    print_recommendations("Adversarial: Conflicted Metal/Sad", ADVERSARIAL_CONFLICTED, songs)


if __name__ == "__main__":
    main()
