# VibeFinder: Music Recommender Simulation

A simplified content-based music recommender that scores and ranks songs against a user's "taste profile" — built to understand, in miniature, how platforms like Spotify or TikTok decide what to play next.

## How The System Works

Real streaming platforms mostly blend two approaches. **Collaborative filtering** looks at what *other, similar users* liked, skipped, or played on repeat — it doesn't need to know anything about the song itself, just behavior patterns across millions of listeners. **Content-based filtering**, which is what this project builds, looks at the *attributes of the song itself* — genre, mood, energy, tempo, danceability — and compares them directly to what one user says they like. Collaborative filtering is powerful because it can surprise you with songs you've never heard of that "people like you" enjoy, but it struggles for brand-new users or brand-new songs with no history yet (the "cold start" problem). Content-based filtering solves cold start neatly, since it only needs the song's own attributes, but it tends to stay inside a narrower box — it will keep recommending things that *look* like what you already told it you like, which is exactly the "filter bubble" risk described below.

This simulation prioritizes **transparency over cleverness**: every recommendation comes with a plain-language list of *reasons* it was chosen, rather than a black-box score.

### Song and UserProfile Features

Each `Song` (a row in `data/songs.csv`) has:
- `title`, `artist` (identifiers, not used for scoring)
- `genre` (categorical, e.g. pop, rock, lofi, edm, metal, jazz, classical, country, r&b, indie)
- `mood` (categorical, e.g. happy, sad, chill, energetic, intense, angry)
- `energy` (0.0–1.0)
- `tempo_bpm` (numeric, beats per minute — tracked but not currently weighted)
- `danceability` (0.0–1.0)
- `acousticness` (0.0–1.0)

A `UserProfile` is a dictionary with any of:
- `favorite_genre`, `favorite_mood` (categorical targets)
- `target_energy`, `target_danceability`, `target_acousticness` (numeric targets, 0.0–1.0)

### Algorithm Recipe

For each song, `score_song()` adds up:
- **+2.0 points** if the song's genre matches the user's favorite genre
- **+1.0 point** if the song's mood matches the user's favorite mood
- **Up to 2.0 points** for energy closeness — the closer the song's energy is to the user's `target_energy`, the more points it earns (a direct match earns the full 2.0, and points shrink smoothly as the gap grows), *not* just "higher energy = better"
- **Up to 1.0 point each** for danceability and acousticness closeness, using the same closeness formula, if the user profile specifies those targets

We use both a **Scoring Rule** and a **Ranking Rule** because they solve two different problems: the Scoring Rule judges *one song in isolation* ("how well does this song match this person?"), while the Ranking Rule takes the *entire scored catalog* and decides the order to present it in (highest score first, top `k` only). You need the first to produce a number, and the second to turn a pile of numbers into an actual ordered list a user can act on.

**Expected bias:** genre match is worth more than any single other factor, so the system likely over-prioritizes genre — a song with the exact right genre but a mismatched mood can still outrank a song with the perfect mood and energy in a different genre. See `model_card.md` for what we actually observed.

## Data Flow

```
Input (User Prefs dict)
        │
        ▼
Process: for every song in songs.csv →
        score_song(user_prefs, song) → (score, reasons)
        │
        ▼
Output: sort all (song, score, reasons) by score, descending
        → return top k → Ranked Recommendations
```

## Project Structure

```
music-recommender/
├── data/
│   └── songs.csv          # 20-song catalog
├── src/
│   ├── recommender.py     # load_songs, score_song, recommend_songs
│   └── main.py            # CLI: runs several test profiles
├── README.md
└── model_card.md
```

## Running It

```bash
python -m src.main
```

## Sample Recommendation Output

```
Loaded songs: 35

=== Default Profile (Afrobeats/Energetic) ===
Profile: {'favorite_genre': 'afrobeats', 'favorite_mood': 'energetic', 'target_energy': 0.75, 'target_danceability': 0.8}
------------------------------------------------------------
1. Longtime by Wizkid ft. Skepta  |  score: 5.95
   reasons: genre match (+1.5), mood match (+1.5), energy closeness (+2.0), danceability closeness (+0.95)
2. CTMF by Davido  |  score: 5.92
   reasons: genre match (+1.5), mood match (+1.5), energy closeness (+1.94), danceability closeness (+0.98)
3. Aje by Davido  |  score: 5.86
   reasons: genre match (+1.5), mood match (+1.5), energy closeness (+1.94), danceability closeness (+0.92)
4. City Boys by Burna Boy  |  score: 5.85
   reasons: genre match (+1.5), mood match (+1.5), energy closeness (+1.9), danceability closeness (+0.95)
5. Fall by Davido  |  score: 4.36
   reasons: genre match (+1.5), energy closeness (+1.86), danceability closeness (+1.0)

=== High-Energy Pop ===
Profile: {'favorite_genre': 'afrobeats', 'favorite_mood': 'energetic', 'target_energy': 0.9, 'target_danceability': 0.8}
------------------------------------------------------------
1. City Boys by Burna Boy  |  score: 5.75
   reasons: genre match (+1.5), mood match (+1.5), energy closeness (+1.8), danceability closeness (+0.95)
2. Aje by Davido  |  score: 5.68
   reasons: genre match (+1.5), mood match (+1.5), energy closeness (+1.76), danceability closeness (+0.92)
3. Longtime by Wizkid ft. Skepta  |  score: 5.65
   reasons: genre match (+1.5), mood match (+1.5), energy closeness (+1.7), danceability closeness (+0.95)
4. CTMF by Davido  |  score: 5.62
   reasons: genre match (+1.5), mood match (+1.5), energy closeness (+1.64), danceability closeness (+0.98)
5. Gym Hero by Pump Nation  |  score: 4.4
   reasons: mood match (+1.5), energy closeness (+2.0), danceability closeness (+0.9)

=== Chill Lofi ===
Profile: {'favorite_genre': 'lofi', 'favorite_mood': 'chill', 'target_energy': 0.2, 'target_acousticness': 0.8}
------------------------------------------------------------
1. Quiet Room by Soft Static  |  score: 5.95
   reasons: genre match (+1.5), mood match (+1.5), energy closeness (+2.0), acousticness closeness (+0.95)
2. Rainy Window by Soft Static  |  score: 4.3
   reasons: genre match (+1.5), energy closeness (+1.9), acousticness closeness (+0.9)
3. Velvet Room by Slow Jazz Society  |  score: 4.3
   reasons: mood match (+1.5), energy closeness (+1.9), acousticness closeness (+0.9)
4. Morning Light by Echo Hall  |  score: 4.3
   reasons: mood match (+1.5), energy closeness (+1.9), acousticness closeness (+0.9)
5. Just Friends (Sunny) by Musiq Soulchild  |  score: 4.05
   reasons: mood match (+1.5), energy closeness (+1.8), acousticness closeness (+0.75)

=== Deep Intense Rock ===
Profile: {'favorite_genre': 'rock', 'favorite_mood': 'intense', 'target_energy': 0.85}
------------------------------------------------------------
1. Midnight Drive by Neon Static  |  score: 5.0
   reasons: genre match (+1.5), mood match (+1.5), energy closeness (+2.0)
2. City Lights by Neon Static  |  score: 3.4
   reasons: genre match (+1.5), energy closeness (+1.9)
3. Broken Mirror by Static Fury  |  score: 3.24
   reasons: mood match (+1.5), energy closeness (+1.74)
4. Rooftop Summer by Voltage Kids  |  score: 1.94
   reasons: energy closeness (+1.94)
5. Gym Hero by Pump Nation  |  score: 1.9
   reasons: energy closeness (+1.9)

=== Adversarial: Conflicted Metal/Sad ===
Profile: {'favorite_genre': 'metal', 'favorite_mood': 'sad', 'target_energy': 0.9}
------------------------------------------------------------
1. Iron Fist by Static Fury  |  score: 3.4
   reasons: genre match (+1.5), energy closeness (+1.9)
2. Broken Mirror by Static Fury  |  score: 3.34
   reasons: genre match (+1.5), energy closeness (+1.84)
3. Late Night Drive by Velvet Groove  |  score: 2.4
   reasons: mood match (+1.5), energy closeness (+0.9)
4. Heartbreak Hotel by Lonely Strings  |  score: 2.3
   reasons: mood match (+1.5), energy closeness (+0.8)
5. Blue Note Blues by Slow Jazz Society  |  score: 2.3
   reasons: mood match (+1.5), energy closeness (+0.8)
```
Loaded songs: 20

=== Default Profile (Pop/Happy) ===
Profile: {'favorite_genre': 'pop', 'favorite_mood': 'happy', 'target_energy': 0.7}
------------------------------------------------------------
1. Sunny Days by The Bright Sides  |  score: 4.9
   reasons: genre match (+2.0), mood match (+1.0), energy closeness (+1.9)
2. Golden Hour by The Bright Sides  |  score: 4.9
   reasons: genre match (+2.0), mood match (+1.0), energy closeness (+1.9)
3. Gym Hero by Pump Nation  |  score: 3.6
   reasons: genre match (+2.0), energy closeness (+1.6)
4. Indie Sunrise by Paper Wings  |  score: 2.7
   reasons: mood match (+1.0), energy closeness (+1.7)
5. Rooftop Summer by Voltage Kids  |  score: 2.64
   reasons: mood match (+1.0), energy closeness (+1.64)

=== High-Energy Pop ===
Profile: {'favorite_genre': 'pop', 'favorite_mood': 'energetic', 'target_energy': 0.9, 'target_danceability': 0.8}
------------------------------------------------------------
1. Gym Hero by Pump Nation  |  score: 5.9
   reasons: genre match (+2.0), mood match (+1.0), energy closeness (+2.0), danceability closeness (+0.9)
2. Sunny Days by The Bright Sides  |  score: 4.7
   reasons: genre match (+2.0), energy closeness (+1.7), danceability closeness (+1.0)
3. Golden Hour by The Bright Sides  |  score: 4.45
   reasons: genre match (+2.0), energy closeness (+1.5), danceability closeness (+0.95)
4. Electric Pulse by Voltage Kids  |  score: 3.85
   reasons: mood match (+1.0), energy closeness (+1.9), danceability closeness (+0.95)
5. City Lights by Neon Static  |  score: 3.55
   reasons: mood match (+1.0), energy closeness (+1.8), danceability closeness (+0.75)

=== Chill Lofi ===
Profile: {'favorite_genre': 'lofi', 'favorite_mood': 'chill', 'target_energy': 0.2, 'target_acousticness': 0.8}
------------------------------------------------------------
1. Quiet Room by Soft Static  |  score: 5.95
   reasons: genre match (+2.0), mood match (+1.0), energy closeness (+2.0), acousticness closeness (+0.95)
2. Rainy Window by Soft Static  |  score: 4.8
   reasons: genre match (+2.0), energy closeness (+1.9), acousticness closeness (+0.9)
3. Velvet Room by Slow Jazz Society  |  score: 3.8
   reasons: mood match (+1.0), energy closeness (+1.9), acousticness closeness (+0.9)
4. Morning Light by Echo Hall  |  score: 3.8
   reasons: mood match (+1.0), energy closeness (+1.9), acousticness closeness (+0.9)
5. Campfire Nights by Lonely Strings  |  score: 3.45
   reasons: mood match (+1.0), energy closeness (+1.7), acousticness closeness (+0.75)

=== Deep Intense Rock ===
Profile: {'favorite_genre': 'rock', 'favorite_mood': 'intense', 'target_energy': 0.85}
------------------------------------------------------------
1. Midnight Drive by Neon Static  |  score: 5.0
   reasons: genre match (+2.0), mood match (+1.0), energy closeness (+2.0)
2. City Lights by Neon Static  |  score: 3.9
   reasons: genre match (+2.0), energy closeness (+1.9)
3. Broken Mirror by Static Fury  |  score: 2.74
   reasons: mood match (+1.0), energy closeness (+1.74)
4. Rooftop Summer by Voltage Kids  |  score: 1.94
   reasons: energy closeness (+1.94)
5. Gym Hero by Pump Nation  |  score: 1.9
   reasons: energy closeness (+1.9)

=== Adversarial: Conflicted Metal/Sad ===
Profile: {'favorite_genre': 'metal', 'favorite_mood': 'sad', 'target_energy': 0.9}
------------------------------------------------------------
1. Iron Fist by Static Fury  |  score: 3.9
   reasons: genre match (+2.0), energy closeness (+1.9)
2. Broken Mirror by Static Fury  |  score: 3.84
   reasons: genre match (+2.0), energy closeness (+1.84)
3. Gym Hero by Pump Nation  |  score: 2.0
   reasons: energy closeness (+2.0)
4. Rooftop Summer by Voltage Kids  |  score: 1.96
   reasons: energy closeness (+1.96)
5. Midnight Drive by Neon Static  |  score: 1.9
   reasons: energy closeness (+1.9)
```

## Personal Reflection

The biggest thing I learned is how much the weights control everything. I set genre and mood to the same weight (1.5 each), and as soon as I added my own Wizkid/Davido songs and pointed my default profile at Afrobeats/Energetic, those three songs immediately took over the top 3 spots. That made total sense to me — those are songs I'd actually pick — but it showed me just how sensitive the ranking is to whatever the top weights are, way more than I expected before actually seeing it happen with my own music.

One thing that stood out: "If" by Davido never made the top 5, even in my own Afrobeats/Energetic profile. Honestly, that felt right — I like the song, but it's more of a mellow one, not really a top pick for "energetic." That was a good gut check that the energy number I gave it (0.55) was probably accurate.

I used my AI assistant for the actual coding — CSV loading, the scoring math, formatting the output — and it looked right the whole way through, I didn't have to fight it on anything there. Where I did have to think for myself was picking my own weights and getting my own songs labeled correctly (Wizkid and Davido are Afrobeats, not hip-hop or R&B like I first assumed — an easy mix-up since they get lumped together in playlists).

If I kept building this, the first thing I'd want is for it to learn from actual listening behavior instead of just the taste profile I type in — right now it only knows what I say I like, not what I'd actually skip or replay.
