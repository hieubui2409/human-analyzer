---
name: cre:humanize
description: "De-AI-slop / 'làm mềm' content so it reads like a human wrote it, not a machine. Deterministic VN+EN AI-tell scanner (filler phrases, formulaic openers/closers, rule-of-three, em-dash overuse, hedging, low burstiness) with an opt-in LLM --rewrite for assets/. Generic 'sounds human' — distinct from cre:voice-audit ('sounds like character X'). Use when content feels AI-generated, before publishing, or as a pre-voice-audit gate. Triggers: 'humanize', 'de-slop', 'de-ai', 'sounds like ai', 'làm mềm', 'remove ai tells', 'ai slop', 'make it human'."
argument-hint: "[--path <file|dir>] [--strictness high|balanced|conservative] [--json] [--rewrite]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "cre-framework"
  position: "pre-publish-gate"
  dependencies: []
---

# cre:humanize — De-AI-Slop / Make Content Read Human

Flag and (opt-in) rewrite generic "AI tells" in content — the filler phrases, formulaic
openers/closers, forced rule-of-three, em-dash overuse, hedging, and mechanically-uniform
sentence length that mark prose as machine-written. Character-agnostic: this asks "does it
sound human at all?", not "does it sound like this character?" (that is `cre:voice-audit`).

## When to Use

- A draft "feels AI-generated" and you want the tells located.
- Before publishing — as the pre-publish de-slop gate, BEFORE `cre:voice-audit`.
- Auditing already-published `assets/` for slop.
- Inside `cre:post-writer` Phase 5 and `cre:multiplatform` per-variant gating.

Handles generic AI-tell detection + asset rewrite; does NOT do character-voice fitting,
evidence-tier checks, or privacy scanning (those are separate gates — see boundaries below).

## Determinism Split (GOLDEN RULE #4)

| Layer      | Owner                              | Does                                                                                                  |
| ---------- | --------------------------------- | ---------------------------------------------------------------------------------------------------- |
| Gather     | `scan-content-for-ai-tells.py`    | Run `platform_lib.humanizer_patterns.scan` over target files → findings. Deterministic. May over-flag. |
| Taxonomy   | `platform_lib/humanizer_patterns.py` | The ONE home for the VN+EN tell tables + structural thresholds. Imported, never re-rolled.          |
| Adjudicate | **LLM**                           | Judge which findings to act on and perform `--rewrite`. Heuristic. Never in the script.               |

The script may over-flag (false positives are expected) — better to surface a tell and let
the LLM dismiss it than to miss slop. The LLM prunes and decides.

## Usage

```bash
PY=$HOME/.claude/skills/.venv/bin/python3   # or .claude/skills/.venv/bin/python3
SK=.claude/skills/cre-humanize/scripts

# scan assets/ (default) at the preferred strictness
$PY $SK/scan-content-for-ai-tells.py --json

# scan one draft, force strictness
$PY $SK/scan-content-for-ai-tells.py --path assets/facebook/260413-slug/post.txt --strictness high

# mark findings as an LLM rewrite worklist (assets/ only)
$PY $SK/scan-content-for-ai-tells.py --path assets/facebook/260413-slug --rewrite
```

Strictness resolves from the `humanize_strictness` preference (`platform_lib/preferences.py`,
default `balanced`) unless `--strictness` overrides it. The lib stays preference-agnostic —
the skill resolves the knob and passes an explicit value in.

Exit codes: `0` clean · `1` findings (advisory) · `2` `--rewrite` refused on a corpus path.

## The --rewrite Contract (LLM work)

`--rewrite` is **opt-in** and is LLM judgment, not a script transform:

1. Scan locates the tells (deterministic worklist).
2. The LLM rewrites the flagged prose in place — kill the tell, keep the meaning, vary the
   rhythm — covering everything the original covered. Match the requested register; this is a
   generic de-slop, not a voice rewrite.
3. **Re-chain the safety gates on the rewritten text, in this canonical order** (a rewrite
   mutates content, so the downstream gates must re-run on the new version — no safety bypass;
   the hard blocker runs FIRST so a rewrite-introduced leak is caught before any other work):
   **`cre:privacy-guard` → `cre:evidence-scanner` → `cre:voice-audit`.**
   This is the single normative order — `cre:post-writer` and `cre:multiplatform` defer to it
   rather than restating their own.
4. **One-shot (RT-02):** the rewrite runs ONCE. If any re-chained gate FAILs on the rewritten
   text, the asset is **HELD + reported** — do NOT auto re-loop or re-rewrite. Surface the
   failing gate + finding to the operator.

## Corpus Guard (Rule 09)

`docs/profiles/` and `docs/materials/` are **flag-only**. `--rewrite` on a path under either
is hard-refused (exit 2) — clinical corpus is never auto-rewritten (Rule 09). Scanning is
always permitted (read-only flagging is safe anywhere). Rewrite is permitted only under
`assets/`.

## Boundary vs cre:voice-audit (no overlap)

| Skill            | Asks                                  | Basis                                  | Order |
| ---------------- | ------------------------------------- | -------------------------------------- | ----- |
| `cre:humanize`   | "Does it sound human at all?"          | generic AI-tell blocklist + heuristics | first |
| `cre:voice-audit`| "Does it sound like character X?"      | `identity/writing-voice.md` per-char   | after |

De-slop the generic machine-stiffness FIRST, then verify character fit. Running voice-audit
before a rewrite would invalidate it (the rewrite mutates the text), so order matters.

## What it does NOT do

- Does NOT fit content to a character voice (that is `cre:voice-audit`, Rule 02/14).
- Does NOT check evidence tiers (that is `cre:evidence-scanner`, Rule 14).
- Does NOT scan for PII/privacy leaks (that is `cre:privacy-guard`, Rule 09).
- Does NOT rewrite corpus (profiles/materials) — flag-only (Rule 09).
- The script never mutates text — rewrite is LLM-only and re-chains the gates.

## Events

On completion emits **`CRE.humanized`** → `content-events.jsonl` (via `orc:event-log`):

```bash
$PY .claude/skills/orc-event-log/scripts/append-event-to-log.py \
  --event-type CRE.humanized --source cre:humanize \
  --reason "findings=<n> strictness=<tier> rewrite=<bool>"
```

## Single Source of Truth

The tell taxonomy + structural thresholds live ONCE in
`.claude/scripts/platform_lib/humanizer_patterns.py`, imported by this skill and by the
`cre:post-writer` / `cre:multiplatform` gates. There is no duplicate taxonomy.

## See Also

- `cre:voice-audit` — character-voice fit (runs after humanize).
- `cre:evidence-scanner` / `cre:privacy-guard` — the other two re-chained safety gates.
- `cre:post-writer` — Phase 5 runs humanize before voice-audit.
- `cre:multiplatform` — per-variant gate set includes humanize.
- Rule 09 (`confidentiality-protocol`) — corpus flag-only.
