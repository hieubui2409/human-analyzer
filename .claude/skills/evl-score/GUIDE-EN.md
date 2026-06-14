# evl:score — Guide

The generic rubric scoring engine: turn a character's profile into an evidence-cited scorecard.

## 1. What this skill does for you

You give it a character and a rubric; it gives you back a standardized scorecard — a score per
criterion (each with a cited evidence tier), domain and overall rollups, a verdict, and a loud list
of anything that couldn't be verified. It is the engine the specialized EVL skills (`standardize`,
`fit`, `compatibility`) wrap with a preset rubric.

## 2. Core concepts (the mental model)

- **Rubric** — a shared, versioned, character-agnostic file in `docs/rubrics/`. Criteria carry
  anchors (0/mid/5), a weight, an evidence hint, and a minimum evidence tier.
- **Evidence tier (T1–T5)** — how strong the cited source is (T1 primary … T5 auxiliary). Every
  score must cite one. No citation ⇒ `[UNVERIFIED]`, excluded from the score and counted.
- **Gather vs. judge** — the script gathers candidate evidence and does the weighted maths; the
  **LLM** does the per-criterion judgment. Scripts never reason about scores.
- **Convergence** — high-stakes rubrics run ≥2 independent judges; if they disagree the result is
  `DIVERGED` and a human decides — it is never auto-averaged.
- **Coverage** — the fraction of criteria that were verified; it headlines the scorecard so a thin
  assessment can't masquerade as a confident one.

## 3. Learning path

1. Run `gather` for a character + rubric and read the evidence bundle it emits.
2. Judge two or three criteria by hand to feel the citation discipline.
3. Run `finalize` with a small scores file and read the rendered scorecard.
4. Try a clinical rubric to see tri-state verdicts + the `cache: never` reassess stamp.

## 4. Use cases (each = a sample conversation)

### Use case: Score a character on the Big Five battery

> "Score character-a against psychometric-big-five."

The skill validates the rubric, gathers evidence per trait, spawns a judge per criterion, aggregates,
and writes `docs/profiles/character-a/eval/psychometric-big-five.{md,json}` with a coverage headline.

### Use case: High-stakes clinical risk screen

> "Run the clinical risk rubric on character-b."

Because the rubric is `high_stakes` with `min_judges: 2`, the skill spawns two input-isolated judges
per criterion and converges them; a divergence is flagged for manual review. The verdict is tri-state
(PASS / PASS_WITH_RISK / BLOCKED) and is never cached.

## 5. Important caveats

- A judge that cannot find supporting evidence MUST return `UNVERIFIED` — do not let it guess.
- Clinical scorecards are point-in-time; always `--rescore`, never reuse a stale risk verdict.
- z-score normalization needs ≥3 characters; below that it is suppressed with a note (use raw).
- The script is offline; real judging happens through the Agent tool and, for high-stakes, human review.
