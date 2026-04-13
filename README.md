# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world recommenders like Spotify's Discover Weekly and YouTube's Up Next work by building a mathematical portrait of your taste from your listening behavior — what you skipped, replayed, saved, or ignored — and then finding items whose attributes sit closest to that portrait in a multi-dimensional feature space. They combine two broad strategies: collaborative filtering, which looks at what users with similar histories enjoyed, and content-based filtering, which compares the intrinsic attributes of songs or videos directly. This simulation focuses on the content-based side. It takes a user's explicitly stated preferences, represents them as a target feature vector, and scores every song in the catalog by measuring how far each track's audio features sit from that target. The features with the most influence on "vibe" — energy and valence — are given higher weights, while supporting features like danceability and tempo refine the ranking. The system prioritizes transparency and interpretability over scale: every score is explainable as a weighted sum of feature proximities, which makes it easy to trace why a specific song was ranked first or last.

### `Song` Features

Each `Song` object stores the following attributes drawn from `data/songs.csv`:

| Feature | Type | Role |
|---|---|---|
| `id` | Integer | Unique identifier |
| `title` | String | Display name |
| `artist` | String | Artist name |
| `genre` | String (categorical) | Hard-filter and categorical score |
| `mood` | String (categorical) | Secondary categorical score |
| `energy` | Float (0.0–1.0) | Primary vibe axis — intensity and activity level |
| `tempo_bpm` | Integer | Rhythmic pace (normalized before scoring) |
| `valence` | Float (0.0–1.0) | Emotional positivity — sad to euphoric |
| `danceability` | Float (0.0–1.0) | Groove and rhythmic regularity |
| `acousticness` | Float (0.0–1.0) | Organic vs. produced texture |

### `UserProfile` Features

Each `UserProfile` object stores the user's target preferences using the same feature vocabulary as `Song`, so scoring is a direct comparison between the two:

| Feature | Type | Role |
|---|---|---|
| `preferred_genre` | String | Matched categorically against `song.genre` |
| `preferred_mood` | String | Matched categorically against `song.mood` |
| `target_energy` | Float (0.0–1.0) | Target energy level for scoring |
| `target_valence` | Float (0.0–1.0) | Target emotional positivity for scoring |
| `target_danceability` | Float (0.0–1.0) | Target groove level for scoring |
| `target_tempo_bpm` | Integer | Target tempo (normalized before scoring) |
| `weights` | Dict | Per-feature importance multipliers (must sum to 1.0) |

### Scoring and Recommendation Logic

**Algorithm Recipe — finalized**

For each song in the catalog, four components are computed and summed into a single score:

| Component | Rule | Max Points | Rationale |
|---|---|---|---|
| Genre match | `+2.0` if `song.genre == user.favorite_genre` | 2.0 | Strongest taste signal — wrong genre overrides everything else |
| Mood match | `+1.0` if `song.mood == user.favorite_mood` | 1.0 | Important but softer — users sometimes cross mood boundaries |
| Energy proximity | `1.5 × (1 − |song.energy − user.target_energy|)` | 1.5 | Best continuous predictor of "feel"; rewards closeness on a 0–1 scale |
| Acoustic bonus | `+0.5` if `user.likes_acoustic` and `song.acousticness ≥ 0.6` | 0.5 | Tiebreaker preference, not a primary filter |

**Maximum possible score: 5.0**

```
score = genre_pts + mood_pts + energy_pts + acoustic_bonus

For each song in catalog:
  1. genre_pts   = 2.0 if genre matches, else 0.0
  2. mood_pts    = 1.0 if mood matches, else 0.0
  3. energy_pts  = 1.5 × (1 − |song.energy − target_energy|)
  4. acoustic_bonus = 0.5 if likes_acoustic and song.acousticness ≥ 0.6, else 0.0
  5. score = sum of above
  6. explanation = list of which components fired

Sort all scored songs by score descending.
Return top K as (song, score, explanation) tuples.
```

### Potential Biases

- **Genre over-prioritization.** Because genre carries 2.0 points — double the weight of mood — a perfect mood-and-energy match in the wrong genre will almost always rank below a mediocre genre match. A chill neo-soul track with exactly the right energy can be beaten by an unfamiliar pop song just because the genre string matches. This may cause the system to miss genuinely great cross-genre discoveries.
- **Catalog representation bias.** The 18-song catalog skews toward certain genres (lofi, pop, rock) and is absent entire regions of global music. Users with preferences for underrepresented styles will consistently receive low scores across the board, not because their taste is niche, but because the data is thin.
- **Energy linearity assumption.** The energy proximity formula treats the distance from 0.3 to 0.5 the same as from 0.7 to 0.9. In practice, human perception of intensity is not linear — the difference between very calm and medium-calm may feel larger than the formula suggests.
- **Binary acoustic threshold.** Acousticness is treated as an on/off bonus at 0.6. Songs just below that threshold (e.g., 0.58) are penalized equally with fully electronic tracks, even though they may still satisfy a user who leans acoustic.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Terminal Output — All Profiles

Run with:

```bash
python src/main.py
```

### Profile 1 — High-Energy Pop

```
============================================================
  Profile : High-Energy Pop
  Prefs   : genre='pop'  mood='happy'  energy=0.9
============================================================

  #1  Sunrise City  —  Neon Echo
       Genre/Mood : pop / happy
       Energy     : 0.82
       Score      : 4.42
       Why        : genre match (+2.0), mood match (+1.5), energy proximity 0.82 vs 0.90 (+0.92)

  #2  Gym Hero  —  Max Pulse
       Genre/Mood : pop / intense
       Energy     : 0.93
       Score      : 2.97
       Why        : genre match (+2.0), energy proximity 0.93 vs 0.90 (+0.97)

  #3  Rooftop Lights  —  Indigo Parade
       Genre/Mood : indie pop / happy
       Energy     : 0.76
       Score      : 2.36
       Why        : mood match (+1.5), energy proximity 0.76 vs 0.90 (+0.86)

  #4  Honey Static  —  Velvet Margin
       Genre/Mood : neo soul / happy
       Energy     : 0.58
       Score      : 2.18
       Why        : mood match (+1.5), energy proximity 0.58 vs 0.90 (+0.68)

  #5  Storm Runner  —  Voltline
       Genre/Mood : rock / intense
       Energy     : 0.91
       Score      : 0.99
       Why        : energy proximity 0.91 vs 0.90 (+0.99)
```

### Profile 2 — Chill Lofi

```
============================================================
  Profile : Chill Lofi
  Prefs   : genre='lofi'  mood='chill'  energy=0.35
============================================================

  #1  Library Rain  —  Paper Lanterns
       Genre/Mood : lofi / chill
       Energy     : 0.35
       Score      : 4.50
       Why        : genre match (+2.0), mood match (+1.5), energy proximity 0.35 vs 0.35 (+1.00)

  #2  Midnight Coding  —  LoRoom
       Genre/Mood : lofi / chill
       Energy     : 0.42
       Score      : 4.43
       Why        : genre match (+2.0), mood match (+1.5), energy proximity 0.42 vs 0.35 (+0.93)

  #3  Focus Flow  —  LoRoom
       Genre/Mood : lofi / focused
       Energy     : 0.40
       Score      : 2.95
       Why        : genre match (+2.0), energy proximity 0.40 vs 0.35 (+0.95)

  #4  Spacewalk Thoughts  —  Orbit Bloom
       Genre/Mood : ambient / chill
       Energy     : 0.28
       Score      : 2.43
       Why        : mood match (+1.5), energy proximity 0.28 vs 0.35 (+0.93)

  #5  Coffee Shop Stories  —  Slow Stereo
       Genre/Mood : jazz / relaxed
       Energy     : 0.37
       Score      : 0.98
       Why        : energy proximity 0.37 vs 0.35 (+0.98)
```

### Profile 3 — Deep Intense Rock

```
============================================================
  Profile : Deep Intense Rock
  Prefs   : genre='rock'  mood='intense'  energy=0.95
============================================================

  #1  Storm Runner  —  Voltline
       Genre/Mood : rock / intense
       Energy     : 0.91
       Score      : 4.46
       Why        : genre match (+2.0), mood match (+1.5), energy proximity 0.91 vs 0.95 (+0.96)

  #2  Gym Hero  —  Max Pulse
       Genre/Mood : pop / intense
       Energy     : 0.93
       Score      : 2.48
       Why        : mood match (+1.5), energy proximity 0.93 vs 0.95 (+0.98)

  #3  Reactor Core  —  Static Fault
       Genre/Mood : drum and bass / intense
       Energy     : 0.97
       Score      : 2.48
       Why        : mood match (+1.5), energy proximity 0.97 vs 0.95 (+0.98)

  #4  Duende Negro  —  Tierra Viva
       Genre/Mood : flamenco / intense
       Energy     : 0.78
       Score      : 2.33
       Why        : mood match (+1.5), energy proximity 0.78 vs 0.95 (+0.83)

  #5  Lagos Sunrise  —  Fela Wave
       Genre/Mood : afrobeat / euphoric
       Energy     : 0.85
       Score      : 0.90
       Why        : energy proximity 0.85 vs 0.95 (+0.90)
```

### Adversarial Profile 1 — Conflicting Energy + Mood

> `genre='pop'`, `mood='melancholic'`, `energy=0.9` — tests whether high energy overrides a sad mood preference.

```
============================================================
  Profile : [ADVERSARIAL] Conflicting Energy+Mood
  Prefs   : genre='pop'  mood='melancholic'  energy=0.9
============================================================

  #1  Gym Hero  —  Max Pulse
       Genre/Mood : pop / intense
       Energy     : 0.93
       Score      : 2.97
       Why        : genre match (+2.0), energy proximity 0.93 vs 0.90 (+0.97)

  #2  Sunrise City  —  Neon Echo
       Genre/Mood : pop / happy
       Energy     : 0.82
       Score      : 2.92
       Why        : genre match (+2.0), energy proximity 0.82 vs 0.90 (+0.92)

  #3  Signal at the Edge  —  Pale Cartographer
       Genre/Mood : post-rock / melancholic
       Energy     : 0.67
       Score      : 2.27
       Why        : mood match (+1.5), energy proximity 0.67 vs 0.90 (+0.77)

  #4  Glass Reverie  —  Pale Cartographer
       Genre/Mood : neoclassical / melancholic
       Energy     : 0.19
       Score      : 1.79
       Why        : mood match (+1.5), energy proximity 0.19 vs 0.90 (+0.29)

  #5  Storm Runner  —  Voltline
       Genre/Mood : rock / intense
       Energy     : 0.91
       Score      : 0.99
       Why        : energy proximity 0.91 vs 0.90 (+0.99)
```

**Finding:** Genre weight (+2.0) outranks mood weight (+1.5), so cheerful pop tracks beat actually-melancholic songs. The system gets "tricked" by genre alignment.

### Adversarial Profile 2 — Unknown Genre (vaporwave)

> `genre='vaporwave'` — a genre that matches no song in the catalog.

```
============================================================
  Profile : [ADVERSARIAL] Unknown Genre (vaporwave)
  Prefs   : genre='vaporwave'  mood='happy'  energy=0.7
============================================================

  #1  Rooftop Lights  —  Indigo Parade
       Genre/Mood : indie pop / happy
       Energy     : 0.76
       Score      : 2.44
       Why        : mood match (+1.5), energy proximity 0.76 vs 0.70 (+0.94)

  #2  Sunrise City  —  Neon Echo
       Genre/Mood : pop / happy
       Energy     : 0.82
       Score      : 2.38
       Why        : mood match (+1.5), energy proximity 0.82 vs 0.70 (+0.88)

  #3  Honey Static  —  Velvet Margin
       Genre/Mood : neo soul / happy
       Energy     : 0.58
       Score      : 2.38
       Why        : mood match (+1.5), energy proximity 0.58 vs 0.70 (+0.88)

  #4  Signal at the Edge  —  Pale Cartographer
       Genre/Mood : post-rock / melancholic
       Energy     : 0.67
       Score      : 0.97
       Why        : energy proximity 0.67 vs 0.70 (+0.97)

  #5  Night Drive Loop  —  Neon Echo
       Genre/Mood : synthwave / moody
       Energy     : 0.75
       Score      : 0.95
       Why        : energy proximity 0.75 vs 0.70 (+0.95)
```

**Finding:** No crash — genre match simply never fires. Results gracefully fall back to mood + energy proximity.

### Adversarial Profile 3 — Zero Energy

> `energy=0.0` — the minimum possible energy preference.

```
============================================================
  Profile : [ADVERSARIAL] Zero Energy
  Prefs   : genre='lofi'  mood='chill'  energy=0.0
============================================================

  #1  Library Rain  —  Paper Lanterns
       Genre/Mood : lofi / chill
       Energy     : 0.35
       Score      : 4.15
       Why        : genre match (+2.0), mood match (+1.5), energy proximity 0.35 vs 0.00 (+0.65)

  #2  Midnight Coding  —  LoRoom
       Genre/Mood : lofi / chill
       Energy     : 0.42
       Score      : 4.08
       Why        : genre match (+2.0), mood match (+1.5), energy proximity 0.42 vs 0.00 (+0.58)

  #3  Focus Flow  —  LoRoom
       Genre/Mood : lofi / focused
       Energy     : 0.40
       Score      : 2.60
       Why        : genre match (+2.0), energy proximity 0.40 vs 0.00 (+0.60)

  #4  Spacewalk Thoughts  —  Orbit Bloom
       Genre/Mood : ambient / chill
       Energy     : 0.28
       Score      : 2.22
       Why        : mood match (+1.5), energy proximity 0.28 vs 0.00 (+0.72)

  #5  Glass Reverie  —  Pale Cartographer
       Genre/Mood : neoclassical / melancholic
       Energy     : 0.19
       Score      : 0.81
       Why        : energy proximity 0.19 vs 0.00 (+0.81)
```

**Finding:** Genre+mood matches still dominate, so the truly lowest-energy song (Glass Reverie, 0.19) only reaches #5. A user wanting near-silence gets lofi tracks at 0.35–0.42 energy instead.

### Adversarial Profile 4 — Empty Preferences

> All categorical fields empty, `energy=0.5` — tests graceful degradation with no genre or mood signal.

```
============================================================
  Profile : [ADVERSARIAL] Empty Preferences
  Prefs   : genre=''  mood=''  energy=0.5
============================================================

  #1  Midnight Coding  —  LoRoom
       Genre/Mood : lofi / chill
       Energy     : 0.42
       Score      : 0.92
       Why        : energy proximity 0.42 vs 0.50 (+0.92)

  #2  Honey Static  —  Velvet Margin
       Genre/Mood : neo soul / happy
       Energy     : 0.58
       Score      : 0.92
       Why        : energy proximity 0.58 vs 0.50 (+0.92)

  #3  Focus Flow  —  LoRoom
       Genre/Mood : lofi / focused
       Energy     : 0.40
       Score      : 0.90
       Why        : energy proximity 0.40 vs 0.50 (+0.90)

  #4  Chromatic Drift  —  The Polaris Quartet
       Genre/Mood : jazz fusion / focused
       Energy     : 0.61
       Score      : 0.89
       Why        : energy proximity 0.61 vs 0.50 (+0.89)

  #5  Coffee Shop Stories  —  Slow Stereo
       Genre/Mood : jazz / relaxed
       Energy     : 0.37
       Score      : 0.87
       Why        : energy proximity 0.37 vs 0.50 (+0.87)
```

**Finding:** With no genre or mood signal, the max achievable score drops to ~0.92 and results are arbitrary — any song near 0.5 energy wins. The system has no fallback strategy for an anonymous user.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"

