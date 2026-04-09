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

In the real world, platforms like Spotify or YouTube use a complex hybrid of collaborative filtering (analyzing mass user behavior) and content-based filtering (analyzing song characteristics). For this project, my recommender prioritizes **content-based filtering**. It evaluates individual track features — genre, mood, energy, acousticness, valence, and tempo — and computes a total score for each song against a user's defined taste profile. Genre is treated as a near-dealbreaker, while numerical features reward songs that are *close* to the user's target, not just high or low.

---

### Features Used

**`Song` objects** carry the following attributes from `data/songs.csv`:

| Feature | Type | Range | Role |
|---|---|---|---|
| `genre` | Categorical | 14 distinct values | Strongest separator — wrong genre is usually a dealbreaker |
| `mood` | Categorical | 10 distinct values | Secondary separator — mismatch is tolerable |
| `energy` | Numerical | 0.0 – 1.0 | How intense/active the track feels |
| `acousticness` | Numerical | 0.0 – 1.0 | Plugged-in electronic vs. raw acoustic texture |
| `valence` | Numerical | 0.0 – 1.0 | Emotional positivity (low = dark, high = uplifting) |
| `tempo_bpm` | Numerical | 56 – 168 BPM | Pace and drive of the track |

**`UserProfile` objects** store the user's target values for each feature above:

```python
user_profile = {
    "preferred_genre":     "rock",
    "preferred_mood":      "intense",
    "target_energy":       0.85,
    "target_acousticness": 0.08,
    "target_valence":      0.50,
    "target_tempo_bpm":    148,
}
```

---

### Algorithm Recipe — The Scoring Rule

For each song in the catalog, the recommender computes a **total score** out of a maximum of **7.0 points**:

#### Step 1 — Categorical Bonuses (flat points)

```
Genre match  → +2.0 pts
Mood match   → +1.0 pts
```

Genre outweighs mood 2:1 because a wrong genre is usually a dealbreaker (e.g. wanting jazz, getting metal), while a mood mismatch is often tolerable (e.g. slightly too chill, but still enjoyable).

#### Step 2 — Numerical Proximity Scores

Each numerical feature uses the **proximity formula**:

```
proximity = 1 − (|song_value − user_target| / max_range)
contribution = weight × proximity
```

A perfect match scores the full weight. The furthest possible value scores 0.

| Feature | Weight | User Target | Max Range | Max Contribution |
|---|---|---|---|---|
| `energy` | 1.5 | 0.85 | 1.0 | +1.50 |
| `acousticness` | 1.0 | 0.08 | 1.0 | +1.00 |
| `valence` | 0.75 | 0.50 | 1.0 | +0.75 |
| `tempo_bpm` | 0.75 | 148 | 168 | +0.75 |

#### Step 3 — Total Score

```
total_score = genre_pts + mood_pts + energy_score + acousticness_score + valence_score + tempo_score
```

**Example — *Storm Runner* (rock, intense, energy 0.91, acousticness 0.10):**
```
= 2.0 + 1.0 + 1.5×(1 − |0.91−0.85|/1.0) + 1.0×(1 − |0.10−0.08|/1.0) + ...
≈ 5.8 / 7.0  ✅ Strong recommendation
```

**Example — *Library Rain* (lofi, chill, energy 0.35, acousticness 0.86):**
```
= 0.0 + 0.0 + 1.5×(1 − |0.35−0.85|/1.0) + 1.0×(1 − |0.86−0.08|/1.0) + ...
≈ 0.5 / 7.0  ❌ Correctly eliminated
```

---

### The Ranking Rule

After scoring all 20 songs:
1. **Sort** the list from highest score → lowest.
2. **Filter** — discard any song scoring below **3.5 / 7.0** (the minimum useful threshold).
3. **Return** the top K results (default: top 3–5).

The scoring rule and ranking rule are kept deliberately separate: scoring answers *"how good is this one song?"* while ranking answers *"which songs should the user actually see?"*

---

### Expected Biases and Limitations

This system has known weaknesses worth acknowledging:

- **Genre over-penalty:** The system may ignore genuinely great songs that match the user's energy and vibe but fall in a neighboring genre (e.g., *Iron Curtain* metal vs. *Storm Runner* rock). A rock fan would likely enjoy metal, but both get the same 0 genre bonus. A future fix would add a `+0.5` genre-neighbor bonus for adjacent genres.

- **Mood-energy redundancy:** `mood` and `energy` are partially redundant — in this dataset, every `intense` song also has high energy. Giving both full weight means high-energy tracks are effectively double-counted, making the energy dimension artificially more influential than intended.

- **Small catalog cold-start bias:** With only 20 songs, there is only one rock track (*Storm Runner*). The recommender is nearly forced to recommend it regardless of how poor it matches on other features, simply because no better genre match exists.

- **No listening history:** This system knows nothing about a user's past behavior. It recommends the same songs to every user with the same profile, with no ability to learn or adapt over time — unlike real-world systems that use collaborative filtering.

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

