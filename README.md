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

