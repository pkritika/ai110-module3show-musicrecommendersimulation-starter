# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

VibeFinder 1.0 is a content-based music recommender designed for a classroom simulation of how real-world recommendation engines work. It is **not** intended for real users or production deployment.

- **What it generates:** A ranked list of up to 5 songs from a 20-song catalog that best match a user's stated genre, mood, and audio feature preferences.
- **Assumptions about the user:** The system assumes the user can explicitly describe their taste (e.g., "I want chill lofi with low energy"). It has no ability to learn from listening history or observe implicit behavior.
- **Purpose:** Educational exploration — to illustrate how scoring rules, feature weights, and ranking algorithms combine to produce music recommendations.

---

## 3. How the Model Works

Imagine you are a music store employee who knows every song in the store by heart. When a customer walks in and says "I want something chill, acoustic, and not too intense," you mentally compare their description to every album on the shelf and hand them the ones that match best.

VibeFinder works the same way. For each song in the catalog, it checks two types of things:

1. **Tags (categorical):** Does the song's genre match what the user asked for? Does the mood match? If yes, the song gets a small bonus — but not an overwhelming one.
2. **Feel (numerical):** How close is the song's energy level to what the user wants? How acoustic does it sound? How emotionally positive is it? Each of these gets a closeness score — the closer the song is to the user's target, the better it scores.

All these numbers are added together to get a single score for each song (max 6.5 points). The songs are then sorted highest to lowest, and the top results are handed back as recommendations.

Energy is intentionally weighted the heaviest because in testing, it was found to be the strongest signal of whether a song "feels right" — even more reliable than genre alone.

---

## 4. Data

- **Catalog size:** 20 songs (10 original starter songs + 10 added during Phase 2 expansion)
- **Genres represented:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, R&B, hip-hop, country, classical, metal, reggae, EDM, folk, blues, soul (17 genres)
- **Moods represented:** happy, chill, intense, relaxed, moody, focused, romantic, energetic, nostalgic, melancholic, peaceful, sad (12 moods)
- **Changes made:** The original 10-song catalog was intentionally expanded to cover a wider range of genres and moods. No songs were removed.
- **What's missing:** The dataset has only **1 song per genre** for most genres. This means the system has very little room to find a "good genre match with okay numerics" — it either gets a perfect match or nothing. Real-world systems like Spotify operate on catalogs of tens of millions of songs, which makes their recommendations far more nuanced.

---

## 5. Strengths

- **Clean genre + mood alignment:** When a user's preferred genre and mood are well-represented in the catalog (e.g., pop/happy), the top result is highly intuitive and the score gap between #1 and #2 meaningfully reflects the quality of the match.
- **Graceful degradation:** When no genre match exists, the system doesn't crash or return nothing — it falls back to the closest numerical match, surfacing songs that share the user's "vibe" even if the genre differs.
- **Transparent scoring:** Every recommendation comes with an itemized list of reasons (e.g., "energy proximity: +1.94"), making it easy to understand and audit exactly why a song was chosen.
- **Vibe-first after rebalancing:** After reducing the genre weight from 2.0 to 1.2 and increasing energy weight from 1.5 to 2.0, the system better reflects how people actually experience music — by feel first, then by category.

---

## 6. Limitations and Bias

**Primary weakness identified during experiment: The "Genre Orphan" problem.**

Because the catalog contains only one or two songs per genre, any user who prefers a minority genre (e.g., jazz, classical, blues) is nearly guaranteed to have that single song appear as their #1 recommendation — regardless of whether it actually matches their energy or mood preferences. For example, a user who wants `classical` music with `energy: 0.95` will receive *Requiem for the Lost* (energy: 0.22) simply because it is the only classical song. This is not a bug in the algorithm — it is a direct consequence of catalog scarcity amplifying the genre bonus. In a real system with millions of songs, this would resolve naturally, but in this 20-song simulation it creates a structural bias **against niche-genre users**.

**Other limitations identified:**

- **Filter bubble risk:** A user who repeatedly gets the same pop songs will never be exposed to the jazz or folk tracks that share their energy/valence profile, because no feedback loop exists to introduce variety over time. The system always gives the same output for the same input — there is no diversity injection, no randomness, and no "exploration vs. exploitation" tradeoff.
- **Energy-centricity:** After rebalancing, energy (weight 2.0) accounts for ~31% of a perfect score. This means the system is implicitly biased toward users who care most about energy level. A user who cares deeply about emotional tone (valence) but is flexible on energy is underserved relative to a user with the reverse preference.
- **No intersectional preferences:** The system treats genre, mood, energy, valence, acousticness, and tempo as fully independent features. It cannot represent preferences like "smooth jazz at high tempo" or "acoustic but upbeat" — it would award full proximity points to a gloomy acoustic ballad even if the user specifically wanted a cheerful acoustic song.
- **No listening history:** Because the system has no memory, it cannot avoid recommending songs the user has already heard, cannot learn from skips or replays, and cannot adapt its weights over time to reflect what an individual user actually responds to.

---

## 7. Evaluation

Seven user profiles were tested during Phase 4 — three standard and four adversarial:

| Profile | Result | Verdict |
|---|---|---|
| High-Energy Pop (pop/happy) | *Sunrise City* ranked #1 at 6.83/6.5 | ✅ Intuitive — only song matching both genre and mood |
| Chill Lofi | Lofi tracks dominated; classical/folk appeared as fallbacks | ✅ Correct — acoustic, low-energy songs naturally cluster |
| Deep Intense Rock | *Storm Runner* forced to #1 (only rock song) | ⚠️ Correct result, but forced by catalog scarcity |
| Blues + High Energy + Sad | Genre bonus initially pushed low-energy blues to #1 | ⚠️ Fixed by reducing genre weight from 2.0 → 1.2 |
| Classical + High Energy | Before fix: classical orphan won. After fix: rock songs correctly overtook it | ✅ Fixed — energy now dominant over genre mismatch |
| Jazz + Opposite Numerics | Jazz song did NOT rank #1; mood-matching songs from other genres won | 🔍 Surprising but correct — energy+mood combo overrode genre |
| All Features Maxed (EDM) | *Bass Cathedral* cleanly ranked #1 at 5.69/6.5 | ✅ Graceful — system found the right match even at extremes |

---

### Why Does "Gym Hero" Keep Showing Up for Happy Pop Listeners?

Imagine the recommender as a friend helping you pick a movie. You say: "I want something fun and upbeat." Your friend flips through the list and thinks — *"OK, upbeat means high energy, fun means bright and happy-sounding"* — and they find *Gym Hero* because it has a pounding beat, a bright sound, and a chart-pop feel, even though technically it might be categorized as a "workout track."

The system does the same thing. It sees that *Gym Hero* (pop, energy 0.93, valence 0.77) is extremely close to what the "happy pop" user asked for — but its mood tag is `intense`, not `happy`. Because the mood mismatch only costs 0.80 points but its energy and acousticness proximity earn back almost 2.7 points, *Gym Hero* still ranks #2. To a real listener, this is actually reasonable — a high-energy, bright-sounding pop track is a sensible "happy" recommendation even if its internal tag says intense. The lesson: **how a song is tagged doesn't always match how a listener experiences it**, and numerical features sometimes "feel" more accurate than the categorical labels.

---

### What Surprised Us Most

**Surprise 1 — Genre weight reduction didn't break anything.**
We expected that lowering genre from 2.0 to 1.2 would cause chaos in the pop/lofi profiles. It didn't. Pop users still got pop songs first. This suggests genre was over-weighted in the original design: energy proximity was doing most of the real work anyway.

**Surprise 2 — The Jazz adversarial profile exposed a hidden strength.**
We designed the "jazz + high energy" profile to trick the system into recommending the one jazz song despite its terrible energy match. But the system resisted the "trick" — intense pop and rock songs outscored *Coffee Shop Stories* on energy and mood, and they ranked higher. This means the system is robust enough to surface cross-genre recommendations when the numerical mismatch is severe enough.

**Surprise 3 — Classical + High Energy was the clearest failure before the fix.**
A user who wants classical music but at high energy (e.g., a fan of dramatic orchestral film scores) represents a real listener type. Before rebalancing, the system forced *Requiem for the Lost* (energy 0.22) to the top simply because it was the only classical song — and that is wrong. After rebalancing, rock and EDM songs overtook it, which is arguably better. But the true fix would require more high-energy classical songs in the catalog.

**Surprising discovery (overall):** Reducing genre weight from 2.0 to 1.2 did *not* damage normal profile quality. Pop/happy users still got pop first. This confirms the genre bonus was significantly over-weighted in the original design.

---



## 8. Future Work

- **Genre neighbor bonuses:** Add a `+0.4` bonus for "adjacent" genres (e.g., metal is adjacent to rock, indie pop is adjacent to pop). This would prevent a jazz fan from getting a metal recommendation just because the energy matches.
- **Diversity enforcement:** Add a "max 2 songs per artist" rule to the ranking step, and introduce a controlled randomness factor so the top 10 aren't always identical.
- **Collaborative filtering layer:** Track how many users with similar profiles enjoyed each song, and weight songs that "similar users" loved higher — the core idea behind platforms like Spotify's Discover Weekly.
- **User feedback loop:** Add a thumbs-up/down mechanism that adjusts the weights in the user's personal profile over time (e.g., if a user skips every high-acousticness song, reduce that target).
- **Mood-energy intersection:** Replace independent mood/energy scoring with a 2D "quadrant" model (valence × arousal) so that "high energy + sad" and "high energy + happy" produce meaningfully different results.

---

## 9. Personal Reflection

Building VibeFinder revealed that recommendation algorithms are much more about *design philosophy* than raw math. The hardest choices were not "which formula to use" but "how much should genre matter compared to energy?" — a question that has no mathematically correct answer, only tradeoffs. The most surprising discovery was how quickly a small catalog (20 songs) exposes structural biases that a large-scale system like Spotify could hide for years. When there is only one jazz song, the jazz-lover user is automatically underserved — and that kind of bias would be invisible in a dataset of 50 million tracks. This makes me think about real recommendation engines very differently: the biases that matter most are not in the algorithm code, they are baked into what data was collected, which artists were licensed, and whose musical tastes shaped the training catalog in the first place.
