# Model Card: VibeFinder 1.0

## Model Name
**VibeFinder 1.0** — a simple content-based song scorer and ranker.

## Goal / Task
Given a user's stated taste profile (favorite genre, favorite mood, and target values for energy/danceability/acousticness), predict which songs from a fixed catalog that user would most likely enjoy next, and rank them highest-to-lowest. It does not predict clicks, listens, or skips from real behavior — it only measures attribute similarity between what a user says they like and what a song actually is.

## Data Used
- **Size:** 20 songs, 8 columns each (`title`, `artist`, `genre`, `mood`, `energy`, `tempo_bpm`, `danceability`, `acousticness`).
- **Features used for scoring:** `genre` (categorical, exact match), `mood` (categorical, exact match), `energy`, `danceability`, `acousticness` (numeric, 0.0–1.0, closeness-based).
- **Features tracked but not used for scoring:** `tempo_bpm` — currently just metadata; it's never compared to anything.
- **Limits:** 20 songs is a tiny catalog. 10 genres are represented, but several (pop, rock, r&b) have 3+ entries while others (indie) have just 1, so the dataset itself is unbalanced before any scoring even happens.

## Algorithm Summary
Every song gets scored against the user's profile using a simple point system:
- Exact genre match is worth the most (2 points) — it's treated as the strongest signal of taste.
- Exact mood match is worth half as much (1 point).
- For each numeric preference the user specifies (energy, danceability, acousticness), the song earns partial credit based on how *close* it is to the target, not just whether it's high or low. A perfect match on one of these earns up to 2 points (energy) or 1 point (danceability/acousticness).
- All the points for a song are added up into one final score, and the songs are sorted from highest score to lowest. The top 5 (or however many are requested) are shown to the user, along with the plain-language reasons that produced that score.

## Observed Behavior / Biases

After I set genre and mood to equal weight and added 7 real songs from artists I actually listen to (Wizkid, Davido), those songs immediately filled the top 3 spots in my own Default Profile and pushed everything else down. That's the filter bubble the assignment is pointing at — the moment I told the system what I like, it just kept giving me more of exactly that, with no room for something like a jazz or lofi song that might've matched my mood on a different day. I don't think this is "wrong," exactly, but it shows the system doesn't know the difference between "this is my genre forever" and "this is what I'm in the mood for today."


## Evaluation Process

We tested VibeFinder against four hand-built profiles plus one adversarial profile, then compared outputs pair by pair:

- **Default Pop/Happy vs. High-Energy Pop:** Both favor pop, but shifting the mood target from "happy" to "energetic" and raising `target_energy` from 0.7 to 0.9 flipped the #1 result from Sunny Days to Gym Hero — makes sense, since Gym Hero's actual energy value (0.90) is much closer to the new target.
- **High-Energy Pop vs. Chill Lofi:** These two profiles barely share any top-5 songs at all — the EDM/pop-leaning profile prefers high-energy, danceable tracks, while the lofi/chill profile shifts entirely toward low-energy, high-acousticness tracks like Quiet Room and Rainy Window. This is the clearest evidence the scoring logic is actually differentiating "vibes," not just outputting the same list every time.
- **Deep Intense Rock vs. Adversarial Metal/Sad:** Surprisingly similar top songs (Midnight Drive, Broken Mirror, Gym Hero all appear in both), which exposed a real weakness: the adversarial profile's contradictory preferences (a "sad" mood target paired with a very high 0.9 energy target) didn't produce obviously broken or nonsensical output — the system just quietly ignored the tension and leaned on genre + energy, since no song in the catalog is both sad-mood and high-energy. In a bigger dataset with more genre/mood combinations this masking effect might not hold, and a truly conflicted profile could expose more erratic-looking rankings.

What surprised us most: the system didn't need to be "broken" to reveal bias — it behaved exactly as designed, and the bias (favoring genre, favoring well-represented genres) was a direct, predictable consequence of the weights we chose, not a bug.

I also tested this by raising mood weight to match genre weight and adding my own songs to the dataset. Before adding my own songs, the Default Profile pulled from generic dataset entries. After adding Wizkid and Davido tracks, my own songs jumped straight to the top 3, which confirmed the scoring logic is actually reacting to genre/mood match and not just noise. I specifically checked "If" by Davido since I like that song — it never cracked the top 5, and looking at the energy value I gave it (0.55), that tracks; it's more of a chill song than an "energetic" one, so it makes sense it lost to higher-energy tracks in an energetic-focused ranking.

I later added more Afrobeats and R&B songs (Tems, Burna Boy, Musiq Soulchild, Steve Lacy) to see if my first result was a fluke or if the weighting held up across more than just my first three songs. It held up — "City Boys" by Burna Boy landed right next to my Wizkid/Davido picks in the Default Profile (score 5.85 vs. 5.95), and that felt correct to me, it's genuinely one of my energetic go-to songs. This gave me more confidence that the genre+mood weighting is doing what it's supposed to do, not just favoring whichever songs I happened to type in first.

I also caught a mislabeling of my own: I first tagged "Last Last" by Burna Boy as "sad" mood, but on reflection that's not right — it's more moody/reflective than straight-up sad, so I relabeled it. It's a small thing, but it's a good example of how easy it is for a "simple" categorical tag to misrepresent a song, especially moods that aren't cleanly happy/sad/energetic. If the mood categories were more specific (e.g. adding "moody" or "reflective" as real options instead of forcing everything into a handful of labels), the system would probably score things more accurately.

I also noticed that Steve Lacy and Musiq Soulchild songs, which I labeled "r&b" instead of "afrobeats," never showed up in my Default Profile top 5 since that profile is locked to "afrobeats" as the favorite genre. I like some of those songs too, but the system has no way of knowing that unless I explicitly change my favorite_genre — it's another version of the filter bubble problem, just genre-based instead of purely popularity-based.

## Intended Use and Non-Intended Use

**Intended use:** A teaching tool and prototype for understanding how simple content-based recommendation math works, and for small, well-labeled catalogs (e.g., a personal playlist tool, a class project, an internal demo) where transparency ("why was this recommended?") matters more than state-of-the-art accuracy.

**Not intended for:** Production recommendation at scale, any system making decisions about real users' data without their knowledge, or any claim that this reflects how real platforms like Spotify actually rank songs (real systems combine content-based signals like these with collaborative filtering, deep learning embeddings, and behavioral signals like skips and replays, which this project does not attempt to model). It should not be used to justify hiring, credit, or any other high-stakes decision — it exists purely for songs and taste, on a 20-song toy dataset.

## Ideas for Improvement

1. **Rebalance or normalize the weights** so genre doesn't automatically dominate — for example, scale each category's contribution by how many features the user actually specified, so a fully-specified profile isn't accidentally more "genre-driven" than a sparse one.
2. **Grow and rebalance the dataset** so every genre has a similar number of songs, removing the "more pop songs = more chances to score well" bias entirely.
3. **Add a lightweight collaborative-filtering layer** (even something as simple as "users with a similar profile also liked X") so the system isn't purely dependent on attribute overlap, and can surprise users the way real recommenders do.
