# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeMatch 1.0**

---

## 2. Intended Use

VibeMatch suggests the top 5 songs from a small catalog based on three things a user tells it: their preferred genre, their current mood, and how energetic they want the music to feel. It assumes the user knows what they want and can express it in simple words like "pop," "chill," or a number between 0 and 1 for energy. This system is built for classroom exploration — it is not designed for real users or production use. It does not learn from listening history, does not personalize over time, and does not connect to any streaming service.

**Non-intended use:** This system should not be used to make real product decisions, should not be used as a substitute for a proper recommendation engine, and should not be applied to catalogs larger than a few hundred songs without significant redesign.

---

## 3. How the Model Works

For every song in the catalog, the system gives it a score based on how well it matches what the user asked for. The score is the sum of three parts:

- **Genre points (+1.0):** If the song's genre exactly matches what the user wants, it gets a bonus. No partial credit — it either matches or it doesn't.
- **Mood points (+1.5):** Same idea. If the song's mood label matches the user's mood preference, it earns points.
- **Energy points (0.0 to 2.0):** The system measures how far apart the song's energy level and the user's target energy are. Songs with energy very close to the target score close to 2.0. Songs far away score close to 0.0.

The five songs with the highest total scores are returned as recommendations. Every result comes with a plain-English explanation showing exactly which parts of the score fired and why.

One change I made from the starter logic: I halved the genre weight from +2.0 to +1.0 and doubled the energy range from 0–1.0 to 0–2.0 after experiments showed that the original genre weight was too dominant — it was overriding mood preferences in profiles where the user's mood and genre pointed in different directions.

---

## 4. Data

The catalog contains **18 songs** stored in `data/songs.csv`. Each song has 10 attributes: id, title, artist, genre, mood, energy, tempo, valence, danceability, and acousticness. The scoring logic only uses genre, mood, and energy directly — the other attributes are stored but not scored.

**Genres represented:** lofi (3 songs), pop (2), and one each of rock, ambient, jazz, synthwave, indie pop, afrobeat, jazz fusion, neoclassical, bossa nova, drum and bass, neo soul, post-rock, and flamenco.

**Moods represented:** intense (4 songs), happy (3), chill (3), relaxed (2), focused (2), melancholic (2), moody (1), euphoric (1).

No songs were added or removed from the original dataset. The main gaps in the data are: very few low-energy songs (only 5 below 0.4 energy), no songs below energy 0.19, heavy representation of Western and electronic genres, and no representation of classical, country, R&B, or hip-hop. Users whose taste falls outside what is in the catalog will consistently get weak recommendations.

---

## 5. Strengths

The system works best for users with clear, common preferences that the catalog actually covers. A user who wants lofi/chill music at low energy gets an excellent top 5 — three genre matches, two mood matches, and energy scores right on target. A user who wants pop/happy at high energy also gets strong results because both pop and happy are represented well enough for the scores to separate clearly.

The scoring is fully transparent. Every result comes with an explanation showing exactly which components fired and what each contributed to the score. This makes it easy to understand why a song ranked where it did, which is valuable for a learning context.

The system also degrades gracefully on impossible inputs. A user who asks for a genre that does not exist in the catalog (like "vaporwave") does not crash the system — it simply falls back to mood and energy scoring without any error, and still returns a sensible-looking top 5.

---

## 6. Limitations and Bias

**Genre string equality creates a filter bubble for niche listeners.**
The scoring system treats genre as a strict binary match — either the genre string is identical or no points are awarded. Because 13 of the 15 genres in the catalog appear in only one song, a user who prefers "jazz," "flamenco," or "bossa nova" will receive at most one genre-match boost across the entire catalog, while a lofi listener gets three. This means the system systematically gives niche-genre users a weaker signal and pushes them toward songs ranked almost entirely by energy proximity — a much noisier fallback. A user who asks for rock and a user who asks for post-rock are treated as completely unrelated even though those genres share nearly identical sonic qualities.

**The catalog skews high-energy, creating a proximity gap for calm listeners.**
Eight of the eighteen songs (44%) have an energy value of 0.7 or higher, and the catalog mean energy is 0.61. A user requesting very low energy (e.g., 0.0 or 0.2) will find that even their closest matches sit 0.19–0.35 energy units away, producing energy-proximity scores noticeably lower than what high-energy users receive. The zero-energy adversarial experiment confirmed this: Library Rain (energy 0.35) ranked first even though the user wanted near-silence, because no song in the catalog actually sits below 0.19. Calm, ambient, or sleep-focused listeners are penalized not because of any preference mismatch, but simply because the dataset does not represent them.

**The "intense" mood over-representation creates an uneven recommendation pool.**
Four songs carry the mood label "intense" (22% of the catalog), while moods like "euphoric" and "moody" appear only once each. A user who prefers euphoric music has a single song eligible for a mood-match bonus; any energy deviation in that one song means the mood signal disappears entirely from the top results. This is a data representation bias, not a logic flaw — the scoring algorithm is fair in isolation, but the catalog it operates on is not.

---

## 7. Evaluation

Seven user profiles were tested in total — three standard profiles and four adversarial edge cases — by running `python src/main.py` and inspecting the ranked top-5 results for each.

**Profiles tested:**

| Profile | genre | mood | energy | Purpose |
|---|---|---|---|---|
| High-Energy Pop | pop | happy | 0.9 | Standard well-represented user |
| Chill Lofi | lofi | chill | 0.35 | Standard low-energy user |
| Deep Intense Rock | rock | intense | 0.95 | Standard high-energy niche user |
| Conflicting Energy+Mood | pop | melancholic | 0.9 | Adversarial: mood vs. energy tension |
| Unknown Genre (vaporwave) | vaporwave | happy | 0.7 | Adversarial: genre not in catalog |
| Zero Energy | lofi | chill | 0.0 | Adversarial: extreme energy boundary |
| Empty Preferences | (none) | (none) | 0.5 | Adversarial: fully anonymous user |

**What was checked:** Whether the #1 result felt intuitively correct, whether wrong-mood songs appeared above right-mood songs, and whether the system crashed or degraded gracefully on impossible inputs.

**What surprised me:**

The biggest surprise was the Conflicting Energy+Mood profile. I expected the mood preference to be honored since it was explicitly stated, but under the original weights (genre +2.0, mood +1.5), Gym Hero — a pop/intense song — ranked #1 over two genuinely melancholic songs. The genre weight silently overrode the mood signal. Doubling energy and halving genre in the weight-shift experiment fixed this: Signal at the Edge (post-rock/melancholic) correctly rose to #1, showing that the original weight hierarchy was the cause, not a fundamental flaw in the approach.

The second surprise was the Zero Energy profile. The catalog contains no song below energy 0.19, so even the "closest" match is 0.19 units away. Despite this, the genre+mood double-match still kept lofi/chill songs at the top — meaning the energy gap was invisible in the output. A real user wanting near-silence would never know the system failed to serve them.

**Weight-shift experiment:** Halving genre (2.0 → 1.0) and doubling energy (1.0 → 2.0) with the max score held constant at 4.5 fixed the adversarial mood profile and surfaced more mood-appropriate results across other profiles, at the cost of slightly more energy-only noise in the tail positions.

---

## 8. Future Work

**1. Replace genre exact-match with a genre similarity map.**
Instead of treating "rock" and "post-rock" as completely unrelated, I would build a small dictionary that gives partial credit to similar genres. This would fix the filter bubble problem for niche listeners without changing anything else about the scoring.

**2. Add a diversity penalty.**
Right now the top 5 can be dominated by one artist or one genre cluster. I would subtract a small penalty for each song that shares an artist or genre with a higher-ranked result, so the recommendations feel more varied and exploratory.

**3. Expand the catalog to at least 100 songs with better energy balance.**
The current catalog has no songs below energy 0.19 and only 5 below 0.4. Adding more low-energy, ambient, and non-Western songs would fix the high-energy skew that currently penalizes calm listeners — this is a data problem, not an algorithm problem, and more data would fix it faster than any weight adjustment.

---

## 9. Personal Reflection

**My biggest learning moment** came when I ran the adversarial "Conflicting Energy+Mood" profile — a user who wanted pop music but with a melancholic mood and high energy. I fully expected the system to surface sad, introspective songs near the top. Instead it returned Gym Hero, an upbeat pop/intense track, at #1. That result stopped me cold because it was technically correct by the math and completely wrong by intuition. It forced me to go back and trace exactly why: the genre weight (+2.0) was large enough on its own to outrank a mood match (+1.5) plus a decent energy score. I had written those numbers myself minutes earlier, yet I hadn't thought through what they'd do when two signals pointed in opposite directions. That gap between "I set the weights" and "I understand what the weights will do in every case" was the sharpest thing I took away from this project.

**AI tools helped me move faster on the parts that would otherwise slow me down** — generating the adversarial profiles, writing the scoring math explanation, and drafting the model card structure. Where I had to slow down and double-check was anywhere the tool made a confident claim about what the output *meant*. Early on I accepted an explanation of why a song ranked highly without re-running the arithmetic myself, and the score breakdown was slightly off. After that I made a habit of verifying every score by hand against the formula in `recommender.py` before writing it into documentation. AI tools are good at structure and language; the actual numbers and logical consequences of weight choices still needed my own attention.

**What surprised me most** was how much the output felt like real recommendations even though the entire algorithm is three lines of arithmetic. Genre match, mood match, and an absolute difference — that is all it takes to produce a ranked list that, for a well-represented profile like Chill Lofi, feels completely natural. Library Rain at #1 with a perfect energy score genuinely seemed like something I would listen to while studying. I kept expecting to find the seam where the simplicity showed, and for standard profiles it mostly didn't. The illusion only broke on the adversarial cases, which made me realize that real recommenders probably feel convincing for the same reason: most users have fairly normal, non-conflicting preferences, so even a simple weighted sum lands in a comfortable place. The edge cases expose the cracks, but average users never push into the edges.

**If I extended this project**, the first thing I would do is replace the strict genre string-equality check with a genre similarity map — a small dictionary where `"indie pop"` and `"pop"` share partial credit, and `"post-rock"` and `"rock"` score closer to each other than `"rock"` and `"lofi"`. That single change would fix the filter-bubble problem for niche genres without touching the rest of the scoring logic. Beyond that, I would add a diversity penalty so the top 5 cannot be monopolized by one artist or one genre cluster, and I would expand the catalog to at least 100 songs with better representation of low-energy, ambient, and non-Western genres. The bias toward high-energy songs is a data problem, not an algorithm problem, and more balanced data would fix it faster than any weight adjustment.
