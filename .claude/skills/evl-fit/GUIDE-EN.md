# evl:fit — Guide

Role / casting-fit decision engine: turn a character's profile into an evidence-cited CAST / CONDITIONAL / NO verdict.

## 1. What this skill does for you

You give it a character (and optionally a custom decision rubric); it gives you back a standardized
scorecard — a score per criterion (each with a cited evidence tier), an overall weighted-mean score,
a three-band verdict, a loud list of anything that couldn't be verified, and an explicit safety-veto
note if a blocking risk flag was found. It is a thin preset over `evl:score` wired to `role-casting-fit`
by default; swap `--rubric` to score fit against any other role spec.

## 2. Core concepts (the mental model)

- **Decision rubric** — `kind: decision`, `high_stakes: true`, `min_judges: 2`. Score range 0–5;
  higher = better fit. The rubric's `target_profile` names the role spec criteria are anchored to.
- **Verdict bands** — three contiguous ranges over the weighted-mean score:
  - **CAST** (≥ 4.0): strong fit, ready for the role.
  - **CONDITIONAL** (3.0 – < 4.0): partial fit, casting possible with named conditions.
  - **NO** (< 3.0): insufficient fit at this time.
  The band is computed by `evl_aggregate` from `verdict_thresholds` in the rubric — the LLM does
  not pick the band.
- **Safety veto** — the rubric's `red_flags` list names criteria whose RED score (0 on a 0–5 scale)
  is a hard block. For `role-casting-fit` the gating criterion is `safety-clearance`. A RED score
  there means one or more severe risk flags exist; the final verdict becomes NO regardless of the
  overall aggregate. The veto is **enforced by the LLM** inspecting `red_flags` after collecting
  judge scores — not by threshold math.
- **Evidence tier (T1–T5)** — how strong the cited source is (T1 primary … T5 auxiliary). Every
  score must cite one. No citation ⇒ `[UNVERIFIED]`, excluded from the roll-up and counted.
- **Gather vs. judge** — the script gathers candidate evidence and does the weighted maths; the
  **LLM** does the per-criterion judgment. Scripts never reason about scores.
- **Multi-judge convergence** — because `high_stakes`, the skill spawns exactly `required_judges`
  (≥ 2) input-isolated judges per criterion. Each judge sees only its criterion + evidence bundle,
  never sibling verdicts. Convergence checks both verdict agreement (≥ 80% modal share) and score
  spread (within 20% of scale range). Disagreement ⇒ `DIVERGED` + manual review required —
  never auto-averaged.
- **Coverage** — the fraction of criteria that were verified; it headlines the scorecard so a thin
  assessment can't masquerade as a confident one.

## 3. Learning path

1. Run `gather` for a character against the default rubric and read the evidence bundle it emits.
2. Read the `target_profile` field in the bundle — it tells you which role spec the criteria are anchored to.
3. Judge two or three criteria by hand (with a mandatory citation) to feel the citation discipline.
4. Run `finalize` with a small scores file and read the rendered scorecard — note the verdict band and coverage.
5. Try a case where `safety-clearance` should be RED and verify the veto overrides the aggregate.
6. Try a custom decision rubric with `--rubric` to see how `target_profile` swapping works.

## 4. Use cases (each = a sample conversation)

### Use case: Standard casting decision

> "Can character-a play the trauma-informed therapist role?"

The skill validates `role-casting-fit`, gathers evidence per criterion, spawns 2 input-isolated
judges per criterion, converges them, checks for safety veto, aggregates, and writes
`docs/profiles/character-a/eval/role-casting-fit.{md,json}` with a CAST / CONDITIONAL / NO verdict.

### Use case: Safety veto in action

> "Score character-b for the therapist role."

Two judges independently return score 0 on `safety-clearance` (RED — untreated high-risk
condition). Even if trait-match, competency-match, and motivational-fit all score high, the LLM
surfaces a safety-veto note and the final verdict is **NO** regardless of the weighted mean.

### Use case: Custom role rubric

> "Evaluate character-a's fit for the executive-coach role."

The user provides a rubric id `executive-coach-fit` whose `target_profile` points to
`docs/references/role-profiles/executive-coach`. Run with `--rubric executive-coach-fit`. The
engine and script are role-agnostic — only the rubric changes.

### Use case: Diverged judges

> "Score character-c for the analyst role."

Two judges disagree on `competency-match` (spread exceeds threshold). The skill returns
`DIVERGED` for that criterion with `manual_review_required: true`. Finalize is deferred until
a human resolves the disagreement.

## 5. Important caveats

- A judge that cannot find supporting evidence MUST return `UNVERIFIED` — do not let it guess.
- The safety veto (`red_flags`) is LLM-enforced, not math-enforced — the LLM must check it explicitly.
- `target_profile` is a reference field; the scoring skill reads it for context, but the actual
  role-spec document must exist under `docs/references/` for the judge to anchor to.
- Decision scorecards are `cache: allow` — they may be reused until the profile changes; use
  `--rescore` when PSY or GRO data has been updated significantly.
- The script is offline; real judging happens through the Agent tool and, for high-stakes, human review.
