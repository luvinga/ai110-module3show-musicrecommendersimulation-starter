# Reflection: Profile Pair Comparisons

Each section below compares two user profiles side by side — what changed between their outputs, and why the difference makes sense given the scoring logic.

---

## Pair 1: High-Energy Pop vs. Chill Lofi

**High-Energy Pop** (`genre=pop, mood=happy, energy=0.9`) returned Sunrise City at #1, Gym Hero at #2, and Rooftop Lights at #3. The top result was a clean triple-match (genre + mood + energy all aligned), and the #2 slot went to a same-genre song despite its mood being wrong.

**Chill Lofi** (`genre=lofi, mood=chill, energy=0.35`) returned Library Rain at #1 with a perfect energy score (1.00), followed closely by Midnight Coding. The entire top 3 stayed within the lofi or ambient universe.

**What changed and why:** Both profiles returned intuitive #1 results, but the depth of the top 5 differed. The pop profile had to lean on non-genre songs (Rooftop Lights = indie pop, Honey Static = neo soul) from position #3 onward because only 2 pop songs exist in the catalog. The lofi profile kept 3 genre matches in the top 4 because lofi is the single most represented genre (3 songs). This reflects the catalog representation bias: well-represented genres produce a tighter, more genre-consistent top 5.

---

## Pair 2: Chill Lofi vs. Deep Intense Rock

**Chill Lofi** top 5 were clustered at energy 0.28–0.42. Almost every pick was acoustic or semi-acoustic (acousticness 0.71–0.93). The mood-word "chill" threaded through three of the five results.

**Deep Intense Rock** (`genre=rock, mood=intense, energy=0.95`) returned Storm Runner as a clear #1, then filled positions #2–4 with high-energy songs from unrelated genres (pop, drum and bass, flamenco) purely on mood+energy proximity.

**What changed and why:** The energy axis flipped completely — low-energy ambient textures vs. high-energy driving intensity. This is exactly what the energy preference is designed to capture. The more interesting difference is that Deep Intense Rock ran out of on-genre candidates after #1, because only one rock song exists. Chill Lofi had three lofi songs available and never needed to fall back. This shows that the accuracy of the recommender is tightly coupled to how many genre-matching songs the catalog contains, not just whether the scoring logic is correct.

---

## Pair 3: High-Energy Pop vs. Conflicting Energy+Mood (Adversarial)

**High-Energy Pop** (`genre=pop, mood=happy, energy=0.9`) had a clean result: Sunrise City ranked #1 because it matched genre, mood, and energy simultaneously.

**Conflicting Energy+Mood** (`genre=pop, mood=melancholic, energy=0.9`) showed the system getting "tricked." With the original weights, Gym Hero (pop/intense) ranked #1 — a song with the right genre and energy but the completely wrong mood. The two actually-melancholic songs (Signal at the Edge, Glass Reverie) didn't appear until #3 and #4.

**What changed and why:** Swapping `mood=happy` for `mood=melancholic` while keeping everything else constant should have shifted the top results toward darker-feeling songs. Instead it barely changed the top 2, because the genre weight (+2.0) was strong enough to keep pop songs at the top regardless of mood. The key insight: when genre and mood conflict in a user profile, the original scoring silently sides with genre every time. This is a real failure mode — a user who wants melancholic music for a sad evening would receive energetic pop hits instead. The weight-shift experiment (genre halved to +1.0) fixed this by allowing the mood signal to outweigh a single genre match.

---

## Pair 4: Unknown Genre (Vaporwave) vs. Empty Preferences (Adversarial)

**Unknown Genre** (`genre=vaporwave, mood=happy, energy=0.7`) gracefully degraded — genre match never fired, but mood and energy still guided the results. Rooftop Lights (indie pop/happy, 0.76 energy) ranked #1 with a score of 3.38. The top 3 were all "happy" mood songs with energy near 0.7.

**Empty Preferences** (`genre='', mood='', energy=0.5`) had no categorical signal at all. Every song scored purely on energy proximity. The max score was 1.84, and results were musically arbitrary — a lofi track, a neo soul track, and a jazz fusion track tied near the top simply because they all sit close to energy 0.5.

**What changed and why:** Both are "broken" profiles in different ways, but they fail differently. The vaporwave profile fails on genre yet still produces a coherent, mood-consistent top 5 — the output feels like reasonable recommendations for a happy mid-energy listener. The empty profile produces meaningless output: a completely random assortment of songs that happen to share a similar tempo feel. This shows that mood is a stronger fallback signal than nothing at all. A real product should detect the empty-preferences case and ask the user for at least one preference before generating recommendations, rather than silently returning an unhelpful list.

---

## Pair 5: Deep Intense Rock vs. Zero Energy (Adversarial)

**Deep Intense Rock** (`genre=rock, mood=intense, energy=0.95`) filled the top 4 with intense-mood songs, all above energy 0.78. The output felt appropriate for a gym or action-film soundtrack.

**Zero Energy** (`genre=lofi, mood=chill, energy=0.0`) returned lofi/chill songs at #1 and #2 — which feels right by genre and mood — but those songs sit at 0.35–0.42 energy. The user asked for near-silence and received songs that are simply the calmest the catalog has, not songs that actually match the preference.

**What changed and why:** Both profiles express extreme energy preferences at opposite ends of the scale (0.95 vs. 0.0). The high-energy profile was served well because the catalog has 8 songs at energy ≥ 0.7 — plenty of close matches. The zero-energy profile was underserved because the catalog minimum is 0.19, leaving a 0.19-unit gap that the genre+mood double-match partially masked. This asymmetry — the catalog skews high-energy with a mean of 0.61 — means the system is structurally more accurate for energetic users than for calm or ambient listeners, even when both use identical scoring logic. Fixing this requires adding more low-energy songs to the data, not changing the algorithm.
