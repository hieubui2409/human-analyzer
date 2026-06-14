# evl:standardize — Guide

Psychometric battery preset: turn a character's profile into an evidence-cited Big Five · Dark Triad · Attachment scorecard, plus attachment quadrant and Dark Triad elevation flag.

## 1. What this skill does for you

You give it a character (and optionally a rubric override); it gives you back a full
psychometric scorecard — a score per criterion (each with a cited evidence tier), domain and
overall rollups, a verdict, and a loud list of anything that couldn't be verified. On top of the
raw scorecard it adds two LLM-narrated clinical summaries:

- **Attachment quadrant** — maps the ECR-R `attachment-anxiety` and `attachment-avoidance`
  subscale scores onto one of four styles: Secure, Preoccupied, Dismissing-Avoidant, or
  Fearful-Avoidant.
- **Dark Triad elevation flag** — raises `dark_triad_elevated: true` if any of the three SD3
  subscales (`narcissism`, `machiavellianism`, `psychopathy`) scores ≥ 4, naming the elevated
  trait(s) with a one-sentence clinical note.

It is `evl:score` with `--rubric psychometric-big-five` pre-wired. The rubric argument is
optional; override only if you have a different psychometric rubric.

## 2. Core concepts (the mental model)

- **Battery** — three instrument blocks in one rubric: Big Five (OCEAN via BFI-2 / NEO PI-R),
  Dark Triad (SD3 subscales), and Attachment (ECR-R two-dimensional). All scored 0–5 with
  behavioural anchors.
- **Evidence tier (T1–T5)** — how strong the cited source is (T1 primary … T5 auxiliary). Every
  criterion score must cite one. No citation ⇒ `[UNVERIFIED]`, excluded from the score and
  counted.
- **Gather vs. judge** — the script gathers candidate evidence and does the weighted maths; the
  **LLM** does the per-criterion judgment. Scripts never reason about scores.
- **Attachment quadrant** — derived from two scored axes (anxiety, avoidance), each thresholded
  at 2.5 mid-scale. The LLM writes the narrative; the threshold arithmetic is stated explicitly
  here (not in the script) so the LLM can verify it is applying the correct quadrant.
- **Dark Triad elevation** — a simple threshold flag (any subscale ≥ 4 = elevated). The LLM
  names the trait(s) and writes the clinical note; the script does not evaluate this.
- **z-score normalization** — the rubric specifies `normalization: z_score`. This requires ≥ 3
  characters with a finalized scorecard for the same rubric. If the cohort is smaller, the
  normalization step is suppressed and raw scores are used, with a visible note on the scorecard.
- **Coverage** — the fraction of criteria that were verified; it headlines the scorecard so a
  thin assessment can't masquerade as a confident one.

## 3. Learning path

1. Run `gather` for a character and read the evidence bundle — three blocks, eleven criteria.
2. Judge two or three criteria by hand (one from each block) to feel the citation discipline.
3. Run `finalize` with a small scores file and read the rendered scorecard.
4. Write the attachment quadrant narration by hand from the two subscale scores.
5. Check the Dark Triad subscales and practice writing the elevation flag note.

## 4. Use cases (each = a sample conversation)

### Use case: Full psychometric battery with default rubric

> "Run the psychometric battery on character-a."

The skill validates `psychometric-big-five`, gathers evidence for all 11 criteria, spawns a
judge per criterion, aggregates, and writes
`docs/profiles/character-a/eval/psychometric-big-five.{md,json}`. After finalize, the LLM
reads `attachment-anxiety` (e.g. 3.8) and `attachment-avoidance` (e.g. 1.2) → Preoccupied
style. Dark Triad subscales are all < 4 → `dark_triad_elevated: false`.

### Use case: Custom psychometric rubric override

> "Standardize character-b using my-custom-psychometric rubric."

Pass `--rubric my-custom-psychometric`. The script resolves the rubric from `docs/rubrics/`
exactly as `evl:score` does. The attachment quadrant and Dark Triad steps only apply when the
finalized scorecard contains those specific criterion ids; if absent, those steps are skipped
with a note.

### Use case: Re-score after a PSY.refresh event

> "Re-run the psychometric battery on character-a — the profile was updated."

Use `--rescore` to ignore the cached scorecard. Always re-score when `PSY.refresh` is emitted
after a significant profile change.

## 5. Attachment quadrant reference

| Anxiety \ Avoidance | Low (< 2.5) | High (≥ 2.5) |
|---------------------|-------------|--------------|
| **Low (< 2.5)** | Secure | Dismissing-Avoidant |
| **High (≥ 2.5)** | Preoccupied | Fearful-Avoidant |

The LLM narrates the quadrant in 2–4 sentences, citing the two subscale scores and at least one
evidence item (by `file:line`) from the scorecard. A quadrant label without a cited score is
not acceptable.

## 6. Dark Triad elevation rules

- Check `narcissism`, `machiavellianism`, `psychopathy` scores from the finalized scorecard.
- If **any** ≥ 4: write `dark_triad_elevated: true`, name the trait(s), write a one-sentence
  clinical note citing the subscale score and its evidence source.
- If **none** ≥ 4: write `dark_triad_elevated: false` and one sentence summarising the
  subclinical profile (e.g. "All SD3 subscales remain subclinical (highest: machiavellianism 2.8)").
- Never derive the flag from unverified criteria — if a subscale is `[UNVERIFIED]`, state that
  the elevation cannot be evaluated for that trait.

## 7. Important caveats

- A judge that cannot find supporting evidence MUST return `UNVERIFIED` — do not let it guess.
- z-score normalization is suppressed below a cohort of 3 characters; use raw scores with a
  visible note. Do not invent a normalised score.
- Attachment quadrant and Dark Triad flag are written by the LLM AFTER finalize, from verified
  scores only. Never narrate from unverified criteria.
- The script is offline; real judging happens through the Agent tool.
