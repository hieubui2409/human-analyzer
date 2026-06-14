# evl:compatibility — Guide

The dyad rubric scoring skill: score a pair of characters on relational compatibility using
versioned, evidence-cited criteria.

## 1. What this skill does for you

You give it two characters and (optionally) a rubric id; it gives you back a standardized dyad
scorecard — a score per criterion (each with a cited evidence tier), a weighted overall score, a
verdict band, and a loud list of anything that couldn't be verified. The default rubric
(`relationship-compatibility`) implements five Gottman/ECR-R criteria across one dyadic domain.

The scorecard lands at `docs/profiles/{char-a}/eval/relationship-compatibility--{char-b}.{md,json}`
so one character can hold many dyad scorecards (one per partner) without collision.

## 2. Core concepts (the mental model)

- **Dyad rubric** — a shared, versioned file in `docs/rubrics/` with `subject: dyad`. Criteria
  carry anchors (0/mid/5), a weight, evidence hints that target BOTH characters' files, and a
  minimum evidence tier.
- **Evidence pooling** — the script gathers candidates independently from each character's profile
  (each side capped at `MAX_CANDIDATES`) then merges and re-ranks; neither partner can crowd the
  other out. Each snippet carries a `character` field so the judge knows whose file it came from.
- **Evidence tier (T1–T5)** — how strong the cited source is (T1 primary … T5 auxiliary). Every
  score must cite one. No citation ⇒ `[UNVERIFIED]`, excluded from the score and counted.
- **Gather vs. judge** — the script gathers candidate evidence and does the weighted maths; the
  **LLM** does the per-criterion judgment. Scripts never reason about scores.
- **Coverage** — the fraction of criteria that were verified; it headlines the scorecard so a thin
  assessment can't masquerade as a confident one.

## 3. Verdict bands

| Band | Score range | What it means |
|------|-------------|---------------|
| **Incompatible** | < 2.0 | Pervasive Four Horsemen and/or very-low-stability attachment; high breakup risk |
| **At-Risk** | 2.0 – 3.0 | Declining positivity ratio / inconsistent repair; active intervention needed |
| **Compatible** | 3.0 – 4.0 | Functional conflict patterns; workable with sustained conscious effort |
| **Highly-Compatible** | ≥ 4.0 | Secure base; consistent repair; 5:1 or better ratio; optimal pairing |

## 4. Criteria (relationship-compatibility rubric)

| Criterion | Weight | Research basis |
|-----------|--------|----------------|
| `horsemen-absence` | 0.25 | Gottman's Four Horsemen — contempt is the single strongest predictor |
| `repair-attempts` | 0.20 | Softened start-ups, accepting influence, humour, physiological soothing |
| `positivity-ratio` | 0.20 | Gottman's 5:1 rule — below 3:1 signals breakup within years |
| `attachment-pairing` | 0.20 | ECR-R stability hierarchy: Secure×Secure most stable; Fearful×Fearful least |
| `similarity-complementarity` | 0.15 | Moderate similarity optimal; complementarity offsets functional gaps |

## 5. Learning path

1. Run `gather` for a pair and read the pooled evidence bundle — note how each snippet is tagged
   with `character` so you can attribute signals.
2. Judge two or three criteria by hand to feel the citation discipline (cite source + tier, or
   return `UNVERIFIED`).
3. Run `finalize` with a small scores file and read the rendered scorecard file.
4. Compare the dyad scorecard filename (`rubric--partner.md`) against the solo scorecard pattern
   to confirm no collision with single-subject scorecards.

## 6. Use cases (each = a sample conversation)

### Use case: Default compatibility score for a pair

> "Score compatibility between character-a and character-b."

The skill validates the `relationship-compatibility` rubric, gathers evidence pooled from both
profiles' `relationships/*.md` and `psychology/attachment-style.md`, spawns a judge per criterion,
aggregates, and writes
`docs/profiles/{char-a}/eval/relationship-compatibility--{char-b}.{md,json}` with a verdict band
and coverage headline.

### Use case: Custom dyad rubric

> "Score character-a and character-b on my custom dyad rubric."

Pass `--rubric <id>` pointing to any `docs/rubrics/<id>.yaml` that declares `subject: dyad`. The
script validates the rubric type and raises immediately if it is not a dyad rubric — wrong rubric
kinds are loud, never silently mis-scored.

## 7. Important caveats

- A judge that cannot find supporting evidence from either character MUST return `UNVERIFIED` — do
  not let it guess or synthesize from general knowledge.
- The `horsemen-absence` criterion is scored inverted: 5 = no horsemen, 0 = all four pervasive.
  The judge must orient the score correctly against the anchors in the rubric.
- Evidence from `relationships/*.md` is the primary source for most criteria; if those files are
  sparse, expect low coverage and multiple `[UNVERIFIED]` markers — this is correct behaviour.
- The script is offline; real judging happens through the Agent tool.
- Scores are per the first character's perspective unless both characters have relationship files
  pointing to each other — the judge must reconcile asymmetric evidence and note it.
