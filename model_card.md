# 🎧 Model Card — VibeFinder 1.0

---

## 1. Model Name

**VibeFinder 1.0**

A content-based music recommender simulation built as part of an AI course module. The name reflects its goal: find songs that match the user's "vibe" by comparing audio features rather than just song labels.

---

## 2. Goal / Task

VibeFinder tries to answer the question: *"Given what I know about your taste, which songs from this catalog will you probably enjoy?"*

It does this by taking a user's stated preferences — their favorite genre, mood, energy level, and sound texture — and scoring every song in the catalog against those preferences. The songs with the highest scores become the recommendations. It does NOT predict whether a user will like a song they have never heard — it finds songs that are mathematically similar to what the user described liking.

---

## 3. Data Used

- **Catalog size:** 20 songs total (10 original + 10 added during project expansion)
- **Features per song:** genre, mood, energy (0.0–1.0), tempo in BPM, valence (0.0–1.0), danceability, acousticness (0.0–1.0)
- **Genres covered:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, R&B, hip-hop, country, classical, metal, reggae, EDM, folk, blues, soul (17 total)
- **Moods covered:** happy, chill, intense, relaxed, moody, focused, romantic, energetic, nostalgic, melancholic, peaceful, sad (12 total)
- **Key limits:**
  - Only 1–2 songs exist per genre — a tiny catalog compared to real music apps
  - All feature values were manually assigned, not measured from actual audio analysis
  - No user listening history is tracked — the system knows nothing about what users have played before
  - The catalog reflects the creator's taste in choosing which genres/moods to include, creating an inherent representation bias

---

## 4. Algorithm Summary

VibeFinder uses a **weighted proximity scoring system**. Here is how it works in plain language:

For each song in the catalog, the system asks six questions and adds up the answers:

1. **Does the genre match?** If yes, the song gets +1.2 bonus points. Genre is treated as a strong preference but not an absolute requirement.
2. **Does the mood match?** If yes, the song gets +0.8 bonus points. Mood matters, but a slight mismatch is tolerable.
3. **How close is the energy?** Songs with energy very close to what the user wants score up to +2.0 points. This is the most important question.
4. **How close is the acoustic texture?** Plugged-in vs. acoustic matters up to +0.80 points.
5. **How close is the emotional tone?** Uplifting vs. melancholic closeness scores up to +0.85 points.
6. **How close is the tempo?** Fast vs. slow closeness scores up to +0.65 points.

The maximum possible score is **6.50 points**. Songs scoring below 1.5 are filtered out entirely. The remaining songs are sorted from highest to lowest score, and the top results are returned as recommendations.

The most important design decision was making **energy the strongest signal** (weight 2.0) because testing showed that how intense a song feels is the most reliable indicator of whether a recommendation will "feel right" — even more reliable than the genre label itself.

---

## 5. Observed Behavior / Biases

**Bias 1 — The Genre Orphan Problem (most significant)**
Because the catalog only has 1 song per genre for most genres, a user who prefers a niche genre (like jazz, classical, or blues) is almost guaranteed to receive that one song as their top recommendation — even if it is a terrible match on energy and mood. For example, a user asking for "high-energy classical" (like dramatic film scores) received *Requiem for the Lost* (energy 0.22) simply because it was the only classical option. There was no correct answer available in the catalog.

**Bias 2 — Energy-Centric Recommendations**
Energy accounts for about 31% of a perfect score. This means the system implicitly favors users who primarily care about intensity. A user who cares more about emotional tone (valence) than energy level is underserved relative to a user with the reverse preference, even though both are equally valid musical tastes.

**Bias 3 — Filter Bubble Risk**
The system gives exactly the same output every time for the same input. There is no randomness, no diversity enforcement, and no mechanism to introduce songs from different genres that might surprise the user positively. Over time, a real listener using this system would always see the same few songs.

**Bias 4 — Tags Don't Match Perception**
Some songs are tagged as "intense" but feel upbeat and happy to actual listeners (e.g., *Gym Hero* appears in happy pop recommendations despite being tagged `mood: intense`). The system cannot distinguish between "intense-uplifting" and "intense-dark" because mood is treated as a simple text label, not a nuanced emotional description.

---

## 6. Evaluation Process

Seven user profiles were tested — three standard and four adversarial (intentionally tricky):

| Profile Tested | What We Looked For | What We Found |
|---|---|---|
| High-Energy Pop (pop, happy, 0.80 energy) | Did the classic pop songs rank #1? | ✅ Yes — *Sunrise City* scored 6.83/6.5, as expected |
| Chill Lofi (lofi, chill, 0.35 energy) | Did low-energy acoustic songs dominate? | ✅ Yes — lofi tracks clustered naturally due to energy + acousticness proximity |
| Deep Intense Rock (rock, intense, 0.90 energy) | Did the one rock song rank #1? | ⚠️ Yes, but it was forced — no competition in genre |
| Blues + High Energy + Sad (conflicting prefs) | Would the system handle contradictions? | ⚠️ Genre won over energy — the low-energy blues song ranked #1 despite the 0.90 energy request |
| Classical + High Energy (genre mismatch) | Would genre force a bad result? | ⚠️ Before fix: yes. After rebalancing weights, rock/EDM correctly ranked higher |
| Jazz + All Numerics Wrong (adversarial) | Could mood+energy override genre? | 🔍 Yes — jazz song failed to rank #1; intense pop/rock won on energy and mood |
| EDM + All Features Maxed | Would the system degrade gracefully? | ✅ Found *Bass Cathedral* cleanly at 5.69/6.5 |

**Logic experiment performed:** Genre weight was reduced from 2.0 to 1.2 and energy weight was raised from 1.5 to 2.0. This fixed the classical and blues adversarial failures without degrading the normal pop and lofi results — confirming that genre was over-weighted in the original design.

---

## 7. Intended Use and Non-Intended Use

**✅ Intended use:**
- A classroom simulation to demonstrate how content-based recommendation algorithms work
- A teaching tool to explore the tradeoffs between genre-first vs. vibe-first scoring
- A starting point for understanding how features, weights, and proximity scoring combine to produce ranked outputs

**❌ NOT intended for:**
- Real music discovery by real users — the catalog is far too small (20 songs) to be useful
- Any commercial or production environment
- Users who have not explicitly provided a preference profile — the system has no ability to infer taste from behavior
- Recommending music across different cultures or languages — the catalog is entirely English-language and Western-genre-focused
- Replacing human curation or expert music recommendation — it cannot understand lyrics, cultural context, or listener history

---

## 8. Ideas for Improvement

**Idea 1 — Genre Neighbor Bonus**
Instead of treating all genre mismatches the same (0 points), add a partial bonus (+0.4) for adjacent genres. For example, metal is close to rock, indie pop is close to pop, soul is close to R&B. This would prevent a jazz fan from getting a metal recommendation just because the energy happens to match, and would make the system culturally more aware.

**Idea 2 — Diversity Enforcement in Rankings**
Add a rule that no more than one song per artist can appear in the top 5. Also introduce a small random "exploration bonus" (±0.1 points) so the list isn't identical every time. This directly addresses the filter bubble problem and helps users discover songs they wouldn't have found otherwise.

**Idea 3 — Learn from Feedback**
After returning recommendations, ask the user: "Did you enjoy this song?" A thumbs-up or thumbs-down response could incrementally adjust the user's stored weights. If a user consistently skips acoustic songs, the system should automatically reduce their `target_acousticness` toward zero over time. This bridges the gap between content-based filtering (what we built) and collaborative filtering (what Spotify uses).
