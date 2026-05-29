---
name: psy:relation-intelligence
description: "Proactively mine the cross-character relationship graph for publishable content angles. Reads dyad graph + relationship files + GRO mentoring + backing materials, scores angles by evidence tier × coherence × consent, tags each with primary_character + consent_status, and hands ranked angles to cre:post-writer. READ-ONLY. Complements (not replaces) psy:crossref (validation) and psy:propagate (cascade). Triggers: 'relation intelligence', 'content angles', 'mine relationships', 'dyad angles', 'what to write about X and Y', 'relationship content ideas'."
argument-hint: "--dyad <c1> <c2> [--all] [--character <main>] [--graph-signal] [--json] [--report]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "psy-framework"
  position: "proactive-mining"
  dependencies: []
---

# psy:relation-intelligence — Proactive Relationship Angle Mining

Turn the static cross-character graph into a ranked, evidence-backed, consent-gated
list of publishable content angles. Where `psy:crossref` reactively _validates_
consistency and `psy:propagate` traces _cascade_ dependencies, this skill
_proactively discovers_ what story is worth telling about a dyad — and refuses
to surface what must stay private.

## Determinism Split (GOLDEN RULE #4)

| Layer      | Owner                                | Does                                                                                                                                                                                                                                                                                                                                                                          |
| ---------- | ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Gather     | `extract-dyad-relationship-facts.py` | Parse dyad graph + relationship files + GRO mentoring milestones; attach backing-material evidence tier; scan Rule-09 + crisis markers; compute primary_character hint. Optional **`--graph-signal`** (default OFF) appends KG `dyad_angle_signals` as `kind=graph_dyad_signal` facts tagged `consent_status=REVIEW` (content-blind; downstream gate decides). Deterministic. |
| Synthesize | **LLM**                              | Read facts → compose candidate angles (title, hook, which fact_ids back it, coherence + publishability judgments). Heuristic.                                                                                                                                                                                                                                                 |
| Rank       | `rank-content-angles-by-evidence.py` | Combine LLM judgments with tier strength + consent propagation → final score + ranking. Deterministic arithmetic.                                                                                                                                                                                                                                                             |

## Usage

```bash
PY=$HOME/.claude/skills/.venv/bin/python3
SK=.claude/skills/psy-relation-intelligence/scripts

# 1. gather facts for a dyad (READ-ONLY)
$PY $SK/extract-dyad-relationship-facts.py hieu hoa --json > facts.json

# 2. LLM synthesizes angles from facts.json → angles.json (schema below)

# 3. rank angles by evidence + consent
$PY $SK/rank-content-angles-by-evidence.py --angles angles.json --facts facts.json --json
```

### Angle schema (LLM output, ranked by step 3)

```json
{
  "title": "...",
  "hook": "...",
  "primary_character": "character-a",
  "supporting_fact_ids": ["F3", "F7"],
  "coherence": 0.9,
  "publishability": 0.8,
  "emotional_register": "hopeful",
  "platform_fit": ["facebook", "linkedin"]
}
```

`evidence_tier` + `consent_status` are derived from the cited facts (don't hand-set them).

## primary_character (OQ#3 A)

Each angle carries a `primary_character` — the narrative-centrality POV (most edges /
most mentions across the dyad facts; `--character` overrides). `cre:post-writer`
loads ONLY that character's VOICE PROFILE; the other character appears _as described
by_ the main one (honors A2 voice authenticity). Resolved here, BEFORE CRE.

## Consent Gate (OQ#6 A, red-team R2) — FAIL-CLOSED

A fact is marked `consent_status=BLOCKED` when its source line carries a Rule-09 tag
(`[PRIVATE]`/`[CONFIDENTIAL: x]`/`[ANONYMIZE]`) **or** a crisis/self-harm marker
(tự tử, tự hại, "chết", trầm cảm, suicide, self-harm, …). An angle citing any BLOCKED
fact inherits BLOCKED, sinks to the bottom of the ranking, and is flagged ⛔ — never
silently dropped, never auto-published. `cre:evidence-scanner` (B8) re-checks at draft
time (two-layer: discovery + publish).

**Exclusion:** `darkness/traumas.md` content is NEVER read into a fact payload — only
its existence is noted as `traumas_present` metadata. Trauma detail cannot enter an angle.

## Events

Emits **`PSY.relation-angle-discovered`** → `character-events.jsonl`. When any angle is
BLOCKED, ALSO emit **`COM.governance`** → `governance-audit.jsonl`.

```bash
$PY .claude/skills/orc-event-log/scripts/append-event-to-log.py \
  --event-type PSY.relation-angle-discovered --source psy:relation-intelligence \
  --character <primary> --reason "dyad <c1>-<c2>: <n> angles, <k> blocked"
```

## Graceful Degradation

If the NetworkX knowledge graph (Batch 8, KG-03a Graph Context API) exists, richer
edges are available; otherwise this skill parses `docs/graph/{dyad}.md` directly.
KG is an enhancement, not a hard dependency.

## See Also

- `psy:crossref` — reactive 10-dim consistency validation (this = proactive mining).
- `psy:propagate` — cross-character cascade dependency tracing (this = angle discovery).
- `cre:post-writer` — consumes top angle: `--character <primary_character> --from-angle`.
- `cre:evidence-scanner` — re-checks the chosen angle's claims at draft time.
- `psy:crisis-assess` — if a dyad surfaces crisis content, route there, not to content.
