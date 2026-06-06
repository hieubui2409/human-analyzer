# cre:angle-discovery — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

Imagine you wake up and ask: "What interesting thing about Character A should we share this week?" This skill wakes up automatically (or on demand), reads every framework — his recent growth signals, new materials, career milestones, what's been shared before, how people responded, his relationship changes — and surfaces the top 5 ranked, evidence-backed angles **without you typing a word**. You just pick the one you like and write.

## 2. Core concepts (the mental model)

**Three-layer pipeline:**

1. **Gather (deterministic):** Scripts extract raw signals from each framework — B5 Big Five shifts, PSY growth-edges, GRO milestones, MAT recent materials, CRE engagement, ORC timing events. Scripts over-gather; false positives expected.
2. **Synthesize (heuristic):** LLM reads the raw signals and writes candidate angles — title, hook, evidence tier, platform fit score. Discards noise, keeps real signals.
3. **Rank (deterministic):** Script scores each angle by `freshness × evidence_strength × platform_fit × consent_factor` and sorts. BLOCKED angles (consent = deny) sink to the bottom but never disappear (transparency).

**Evidence strength scaling:** T1 (primary) = 1.0, T2 (secondary) = 0.85, T3 (tertiary) = 0.55, T4/T5 (weak) = 0.25/0.15. T4-T5 angles flagged `speculative` — publishable but weak evidence.

**Freshness window:** Signals older than `--since-days` (default 30) decay to zero and drop. Keeps angles current.

## 3. Learning path

**First run:**
```bash
.claude/skills/.venv/bin/python3 .claude/skills/cre-angle-discovery/scripts/aggregate-angle-signals-across-frameworks.py \
  --character character-a --framework all --since-days 30 --json
```
Read the output — you'll see raw signals like "B5 conscientiousness +8% since Jan", "growth-edge: assertiveness unlock", "new material: mentor feedback". These become angle seeds.

**As you grow:** Try `--graph-signal` to include semantic relationship candidates from the knowledge graph (slower, advisory only — don't over-rely on it). Try `--top 3` for daily curated picks instead of top 5.

**Standard flow:** Run discovery → pick an angle → feed to `cre:exploring --resume` to refine → `cre:post-writer --from-context` to write.

## 4. Use cases (each = a sample conversation)

### Use case: Periodic ideation (daily/weekly)

> **You:** "What should we post about Character A this week?"
>
> **Skill:** Runs autonomously overnight; returns top 5 angles ranked by freshness. Discovers "Character A's mentoring consistency (GRO milestone)" scores 0.82, higher than "anxiety recurrence (PSY growth-edge)" at 0.61.
>
> **You:** Pick the mentoring angle, run `cre:post-writer --from-context`.

### Use case: Seeding exploration

> **You:** "I want to refine an angle before writing."
>
> **Skill:** `--to-context` writes top angle as CONTEXT.md (cre:exploring format).
>
> **You:** Run `cre:exploring --resume`, refine through Q2-Q7, then `cre:post-writer --from-context`.

### Use case: Batch multiplatform generation

> **You:** "Generate 5 angles, write native TikTok/LinkedIn/Facebook posts for each."
>
> **Skill:** `--top 5 --json` returns angles JSON.
>
> **You:** Loop: per angle, run `cre:multiplatform --source <angle> --platforms tiktok,linkedin,facebook`.

### Use case: Framework-specific mining

> **You:** "What's fresh in materials this week?"
>
> **Skill:** `--framework mat --since-days 7 --top 3` returns only material-sourced angles from past week.

## 5. Important caveats

- **Over-gathers by design:** Scripts flag many weak signals; LLM prunes noise. False positives expected — that's OK.
- **No event leakage:** Angle text paraphrases event timing ("milestone season", "anniversary of X") — never quotes internal ORC payloads or raw clinical detail. Downstream gates (`cre:evidence-scanner`, `cre:privacy-guard`) enforce Rule 09.
- **Consent matters:** Angles tagged `BLOCKED` (relationship/topic denies consent per Rule 09) sink to bottom but ship in results — transparency. Don't publish them.
- **T4/T5 speculative:** Angles backed only by weak evidence are flagged `speculative` — valid to publish (they're ranked lower), but disclose the evidence tier.
- **Semantic graph optional:** `--graph-signal` adds KG candidates but is SLOW and advisory only; don't rely on it for critical decisions.

## See also

- [`SKILL.md`](./SKILL.md) for technical contract
- `cre:exploring` — interactive refinement
- `cre:post-writer --from-context` — write immediately
- `psy:relation-intelligence` — the relationship-angle specialized source
- Rule 03 (content pipeline), Rule 14 (CRE events + evidence)
