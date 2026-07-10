"""
Tests for the function-based recommender in src/recommender.py.

These replace the original starter tests, which were written against
a class-based Song/UserProfile/Recommender API that doesn't match
this project's actual implementation (plain dicts + functions).
"""

from src.recommender import score_song, recommend_songs


def make_test_songs():
    """Two small test songs: one pop/happy, one lofi/chill."""
    return [
        {
            "title": "Test Pop Track",
            "artist": "Test Artist",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.8,
            "tempo_bpm": 120.0,
            "danceability": 0.8,
            "acousticness": 0.2,
        },
        {
            "title": "Chill Lofi Loop",
            "artist": "Test Artist",
            "genre": "lofi",
            "mood": "chill",
            "energy": 0.4,
            "tempo_bpm": 80.0,
            "danceability": 0.5,
            "acousticness": 0.9,
        },
    ]


def test_score_song_rewards_genre_and_mood_match():
    """A song matching both genre and mood should score higher than
    a song matching neither."""
    user_prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.8,
    }
    songs = make_test_songs()

    pop_score, pop_reasons = score_song(user_prefs, songs[0])
    lofi_score, lofi_reasons = score_song(user_prefs, songs[1])

    assert pop_score > lofi_score
    assert any("genre match" in r for r in pop_reasons)
    assert any("mood match" in r for r in pop_reasons)


def test_score_song_returns_score_and_reasons():
    """score_song must return a (score, reasons) tuple where reasons
    is a non-empty list when there's at least one match."""
    user_prefs = {"favorite_genre": "pop", "favorite_mood": "happy"}
    songs = make_test_songs()

    score, reasons = score_song(user_prefs, songs[0])

    assert isinstance(score, float)
    assert isinstance(reasons, list)
    assert len(reasons) > 0


def test_recommend_songs_returns_sorted_top_k():
    """recommend_songs should return exactly k results, sorted by
    score descending, with the best match for this profile first."""
    user_prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.8,
    }
    songs = make_test_songs()

    results = recommend_songs(user_prefs, songs, k=2)

    assert len(results) == 2

    top_song, top_score, top_reasons = results[0]
    assert top_song["genre"] == "pop"
    assert top_song["mood"] == "happy"

    scores = [score for _, score, _ in results]
    assert scores == sorted(scores, reverse=True)


def test_recommend_songs_respects_k_limit():
    """Asking for k=1 should return exactly one result even if more
    songs are available."""
    user_prefs = {"favorite_genre": "lofi", "favorite_mood": "chill"}
    songs = make_test_songs()

    results = recommend_songs(user_prefs, songs, k=1)

    assert len(results) == 1
