# evl:rubric-import — Guide

The external framework intake gate: turn a 3rd-party evaluation instrument into a canonical,
gap-flagged rubric draft ready for human review.

## 1. What this skill does for you

You give it an external framework — a psychometric battery, a casting brief, a competency model,
a clinical screen — as a file, pasted text, or a URL you want fetched. It parses the raw text
into a loose criteria list, scaffolds a canonical rubric skeleton with explicit TODO placeholders
where it has no basis to fill a field, spawns the `evl-rubric-importer` sub-agent to propose a
semantic mapping, re-validates that proposal, and optionally writes the draft YAML to
`docs/rubrics/imported/`. The draft cannot be scored until `evl:validate` passes — which
requires every gap to be filled by a human.

## 2. Core concepts (the mental model)

- **Parse vs. map** — parsing (deterministic, script) extracts structure from the raw text.
  Mapping (LLM sub-agent, input-isolated) proposes which external criterion becomes which
  canonical criterion, with what weight and anchors. These are two separate passes so that
  invented structure is never mixed with deterministic structure.
- **Gaps are the honest output** — a criterion with no basis for a weight or anchor goes into
  `_import_gaps`, not into the rubric with a guessed value. A gap-laden draft is correct
  and honest; a silently filled draft would produce fabricated scores later.
- **Input isolation** — the `evl-rubric-importer` sub-agent sees only the external text +
  canonical schema + the parse output. No character data, no sibling rubrics. This prevents
  cross-contamination and keeps the mapping proposal reviewable.
- **Draft sentinel** — every imported rubric starts at `version: 0.0.0` and `status: draft`.
  It is blocked from scoring until a human promotes it and `evl:validate` passes.
- **No network in the script** — URL fetching is always a skill-level WebFetch call. The script
  is offline and deterministic.

## 3. Learning path

1. Run `--input` on a simple two-section markdown file (no `--write`) and read the draft YAML
   and gap list printed to stdout.
2. Try `--fmt freeform` on a plain bullet list to see how freeform parsing works.
3. Use `--write` to materialise the draft, then open `docs/rubrics/imported/<id>.yaml` and
   fill one criterion's `weight`, `anchors`, and `min_tier` manually.
4. Run `evl:validate` against the filled draft to see what passes and what is still blocked.
5. Try a URL: fetch the page with WebFetch in the skill, pipe the text via `--stdin`, observe
   how much structure the parser recovers and what lands in `_unclassified`.

## 4. Use cases (each = a sample conversation)

### Use case: Import a markdown competency model

> "Import this competency framework markdown file as a decision rubric with id leadership-eval."

The skill reads the file, calls the script to parse and scaffold, spawns the importer agent to
propose weights and anchors for each competency, re-validates the proposal, and prints the draft
YAML with a gap list. If the user then asks to write it, `--write` materialises
`docs/rubrics/imported/leadership-eval.yaml`.

### Use case: Ingest a pasted psychometric instrument

> "Here is a Big Five instrument description — convert it to a psychometric rubric."

The skill accepts the pasted text via `--stdin`, selects `--kind psychometric`, runs the
parse+scaffold, spawns the importer agent, and returns the draft + gaps. The gaps (likely
missing scale anchors for each facet) are listed verbatim so the human knows exactly what to fill.

### Use case: Fetch and import a public framework from a URL

> "Fetch https://example.org/clinical-screen and import it as a clinical rubric."

The skill calls WebFetch (not the script) to retrieve the page text, then pipes the result to
the script via `--stdin` with `--kind clinical --source "https://example.org/clinical-screen"`.
Provenance is embedded in `_source` so the draft is traceable.

## 5. Important caveats

- The importer agent proposes; the re-validation gate decides. A well-intentioned proposal that
  cannot be grounded in the source text must land in `gaps`, not `mapping`.
- Do not edit a draft file while the script is running — write is atomic (single `write_text`
  call) but concurrent edits will race.
- A `version: 0.0.0` rubric that passes `evl:validate` should be bumped to `version: 1.0.0`
  before first production scoring to establish a clean provenance baseline.
- Freeform input produces the thinnest parse (one criterion per non-empty line); prefer markdown
  or JSON/YAML when the source has any hierarchical structure.
- `--source` is not validated — supply the canonical URL or citation string so the draft is
  auditable long after the import session ends.
