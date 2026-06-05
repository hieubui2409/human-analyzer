# cre:humanize — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You drafted a post (often with an LLM) and it reads "off" — too smooth, too even, sprinkled
with "it's worth noting", "trong thế giới ngày nay", forced triples and em-dashes. `cre:humanize`
locates those tells deterministically, then (opt-in) lets the LLM rewrite the prose so it reads
like a person wrote it. It does not care whether it sounds like a specific character — only
whether it sounds human at all.

## 2. Core concepts (the mental model)

- **Script gathers, LLM judges.** The scanner is deterministic and may over-flag. It produces a
  worklist; you (the LLM) decide what to fix. Never let the script "decide".
- **One taxonomy home.** Every tell lives in `platform_lib/humanizer_patterns.py`. The skill and
  the `cre:post-writer` / `cre:multiplatform` gates all import it. No duplicate lists.
- **Strictness is a dial.** `conservative ⊆ balanced ⊆ high`. `low_burstiness` only fires at
  `high` and is advisory (never blocks) — Vietnamese social posts legitimately vary in rhythm.
- **Rewrite is opt-in, one-shot, and re-chained.** A rewrite mutates `assets/` text, so the
  evidence / privacy / voice gates must re-run on the new version. If any fails, HOLD and report
  — do not auto re-rewrite. Corpus (profiles/materials) is flag-only (Rule 09).

## 3. Learning path

First run: scan one draft → read the findings. Next: tune `--strictness`, or set the
`humanize_strictness` preference once. As you grow: wire it as the de-slop gate before
`cre:voice-audit`, and let `cre:post-writer` / `cre:multiplatform` call it per draft/variant.

## 4. Use cases (each = a sample conversation)

### Use case: locate the tells in a draft
> You: "this post sounds like AI, find the tells"
> Skill: runs `scan-content-for-ai-tells.py --path <draft>`, prints each finding with category,
> severity, span and a concrete suggestion. Exit 1 means tells were found.

### Use case: de-slop and rewrite an asset
> You: "humanize and rewrite assets/facebook/260413-slug"
> Skill: scans with `--rewrite`, the LLM rewrites the flagged prose in place, then re-runs
> `cre:evidence-scanner` → `cre:privacy-guard` → `cre:voice-audit`. One pass; a gate FAIL → HOLD.

### Use case: flag-only a profile (no rewrite)
> You: "check docs/profiles/... for AI tells"
> Skill: scans and reports. `--rewrite` here is refused (exit 2) — corpus is never auto-rewritten
> (Rule 09). You get the worklist; any edit is a human/PSY decision.

## 5. Important caveats

- The scanner over-flags by design — treat findings as candidates, not verdicts.
- `low_burstiness` is advisory and high-tier only; do not block on it.
- The script never mutates text; rewrite is LLM work and must re-chain the safety gates.
- This is NOT voice fitting, evidence checking, or privacy scanning — those are separate skills.
