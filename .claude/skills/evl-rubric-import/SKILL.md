---
name: "evl:rubric-import"
description: "EVL rubric import engine — ingest an external evaluation framework (file, pasted text, or pre-fetched URL text) and convert it into a canonical rubric DRAFT under docs/rubrics/imported/. Semantic mapping is done by the evl-rubric-importer sub-agent; structural scaffolding and gap detection are deterministic. Triggers: 'evl rubric import', 'import rubric', 'convert framework to rubric', 'ingest evaluation framework'."
argument-hint: "import --input <path> [--fmt md|json|yaml|freeform] [--id <slug>] [--title <str>] [--kind decision|psychometric|clinical|dyad] [--source <str>] [--write]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "evl-framework"
  position: "import"
  dependencies: []
---

# evl:rubric-import — External Framework → Canonical Rubric Draft (EVL Framework)

Ingest an external evaluation framework and convert it into a canonical rubric DRAFT ready for
human review. This is the intake gate: nothing enters the scoring engine without passing through
this skill and surviving `evl:validate`.

**Design law:** the script does STRUCTURE ONLY — parse, scaffold, detect gaps. It never invents
a weight or an anchor; that would be score-theater. The **semantic mapping** (which external
criterion maps to which canonical anchors and weights) is done by the `evl-rubric-importer`
**sub-agent**, spawned input-isolated with only the external text and the canonical schema. Its
structured proposal is handed back to `import_rubric(mapping=...)` and re-validated by the same
gap-detection logic. A gap-laden draft **fails `evl:validate`** until a human fills it — it
cannot be scored.

**URL handling:** fetching a URL happens in the skill via WebFetch (never in the script — the
script is offline). Pass the fetched text via `--stdin` or write it to a temp file first.

## Default (No Arguments)

Ask for the input source and desired rubric id, then run the workflow below.

## Flags

| Flag | Purpose |
|------|---------|
| `--input <path>` | Read external framework from a file |
| `--stdin` | Read external framework from standard input |
| `--fmt md\|json\|yaml\|freeform` | Input format (default: `md`) |
| `--id <slug>` | Rubric id slug for the draft file (default: derived from title) |
| `--title <str>` | Override rubric title |
| `--kind decision\|psychometric\|clinical\|dyad` | Rubric kind (default: `decision`) |
| `--source <str>` | Provenance string (URL, citation, author) |
| `--write` | Write the draft YAML to `docs/rubrics/imported/` and print path |

## Workflow (LLM-executed)

### Step 1 — Fetch (if URL)

If the user supplies a URL, call **WebFetch** in the skill to retrieve the page text. Hand the
extracted text to the script via `--stdin` (or a temp file). The script never touches the network.

### Step 2 — Parse + scaffold (deterministic, script)

```bash
PY=.claude/skills/.venv/bin/python3

# From a file:
$PY .claude/skills/evl-rubric-import/scripts/run_import.py \
    --input <path> --fmt <fmt> --id <slug> --title "<title>" \
    --kind <kind> --source "<url-or-citation>"

# From stdin:
echo "<text>" | $PY .claude/skills/evl-rubric-import/scripts/run_import.py \
    --stdin --fmt <fmt> --id <slug> --title "<title>" \
    --kind <kind> --source "<url-or-citation>"
```

`run_import.py` calls `evl_import.import_rubric(text, meta, fmt=...)` → prints the draft YAML
and the `_import_gaps` list as structured output. Without `--write` this is a dry-run preview.

### Step 3 — Semantic mapping (LLM, Agent tool, input-isolated)

Spawn the **`evl-rubric-importer`** sub-agent via the Agent tool. Give it ONLY:

- The original external framework text (no conversation history).
- The canonical schema at `.claude/schemas/evl-rubric.schema.json`.
- The `parse_external` output from Step 2 (the loose criteria list + unclassified lines).

The agent returns one JSON object: `{mapping: {criterion_id: {weight, anchors, evidence_hint,
min_tier, source_line, rationale}}, gaps: [...], notes: "..."}`. Its output is scoped: no
sibling-rubric context, no character data.

### Step 4 — Re-validate with mapping (deterministic, script)

Pass the agent's `mapping` back through `import_rubric(mapping=agent_mapping)`. The same gap
detection runs again — criteria the agent flagged in `gaps` remain unfilled and show in
`_import_gaps`. Nothing the agent proposes is trusted without this re-validation pass.

### Step 5 — Write (optional, with --write)

```bash
$PY .claude/skills/evl-rubric-import/scripts/run_import.py \
    --input <path> ... --write
```

Calls `evl_import.write_draft(rubric, id)` → `docs/rubrics/imported/<id>.yaml`. Prints the
absolute path. The draft is marked `status: draft` and `needs_human_review: true`; it will be
rejected by `evl:validate` until weights, anchors, and min_tiers are filled.

### Step 6 — Emit EVL.rubric_imported

After a successful write, emit `EVL.rubric_imported` (see `orc:event-log`) so the user can
proceed to human review → `evl:validate` → `evl:score`.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/run_import.py` | Parse + scaffold (+ write) — no network, no invention |

## Safety

- Writes ONLY under `docs/rubrics/imported/` (fs_guard EVL zone).
- Never invents a weight or anchor; every invented field would be a silent lie in a later score.
- No network in the script path; URL fetching is always a skill-level WebFetch call.
- A draft with gaps cannot pass `evl:validate` → cannot be scored. Loud failure by design.

## Events

- **Emits:** `EVL.rubric_imported` (after a draft is written with `--write`).
- **Downstream:** human review → `evl:validate` → `evl:score`.

## Examples

```bash
# Preview the parsed structure (no write)
/evl:rubric-import --input path/to/framework.md --id my-rubric --kind psychometric

# Import from stdin (e.g. pasted text)
echo "# My Framework\n## Criterion A\n## Criterion B" | \
  /evl:rubric-import --stdin --id my-rubric --kind decision --write

# Import from a URL (skill fetches with WebFetch, then pipes to script)
/evl:rubric-import --source "https://example.org/framework" --id ext-fw --write
```

## See Also

- `evl:validate` — structural check before scoring; rejects gap-laden drafts
- `evl:score` — the scoring engine that consumes validated rubrics
- `evl:standardize` — psychometric battery preset · `evl:fit` — role decision
- `docs/rules/17-evl-framework.md` — EVL domain rules
- Agent: `evl-rubric-importer` — the semantic-mapping sub-agent this skill drives
