# Knowledge Architecture — 6-Layer Map

How this project manages knowledge, mapped as 6 layers (ECC § B4). **Documentation of what
already exists** — no new infrastructure. Each layer points at the real asset that implements it.

## The 6 layers

| Layer | Purpose | Project asset | Status |
| ----- | ------- | ------------- | ------ |
| **L1 Active execution** | In-flight task tracking | Claude Tasks (`TaskCreate/Update`) + `plans/{date}-{slug}/` phase files | ✅ live (32 plan dirs) |
| **L2 Claude Code memory** | Cross-session durable facts | `~/.claude/projects/.../memory/*.md` + `MEMORY.md` index | ✅ live (11 memory files) |
| **L3 MCP memory graph** | Semantic/event graph via MCP server | — | ⏸ **DEFERRED** (see below) |
| **L4 KB repo** | Synthesized knowledge, audits | `plans/reports/*.md` (wave findings, validation, red-team) | ✅ live (111 reports) |
| **L5 External store** | Large raw source docs | `docs/materials/{character}/` (evidence-tiered T1–T5 + CRAAP) | ✅ live (3 character stores) |
| **L6 Local archive** | Retired notes, discarded hypotheses | `mat:archive` (soft-delete + audit trail) + `psy:arc-tracker` discarded-hypothesis log | ✅ live |

## L3 — DEFERRED (rationale)

The MCP semantic memory graph is **intentionally not built**:

- Deferred at Batch 5 OQ#7. The two needs it would serve are already covered:
  - **Relational/semantic structure** → the Knowledge Graph (NetworkX file-graph over profiles +
    relationships, `docs/graph/`), not an MCP event server.
  - **Event memory** → the Batch 5 JSONL event streams (`orc:event-log`, 6 append-only streams).
- Adding an MCP server is an external runtime dependency → YAGNI until a query need exists that the
  file-graph + JSONL cannot serve. Revisit only with a concrete failing query.

## Per-framework usage

| Framework | Primary layers | Notes |
| --------- | -------------- | ----- |
| **MAT** | L5 (ingest raw) → L6 (archive) | Materials enter L5 tiered; superseded/retired → L6 via `mat:archive`. |
| **PSY** | L4 (formulation findings) + L6 (discarded hypotheses) | Profiles synthesize L5 evidence; `psy:arc-tracker` logs hypotheses that didn't hold → L6. |
| **CRE** | L4 (angle/report reuse) | Content angles draw on L4 reports + L5 evidence (gated by tier). |
| **GRO** | L4 (career findings) | Growth assessments persist to `plans/reports/` + profile `growth/`. |
| **ORC** | L1 + L2 (session + memory) | `orc:session-state` drives L1; `orc:compounding`/`orc:dream` write L2. |
| **COM** | cross-cutting | `com:git` versions everything; `com:health-check` watches L1 execution. |

## Maintenance

This map is descriptive — regenerate the asset counts (memory files, reports, material stores) when
they drift materially. L3 status flips only if the MCP-graph deferral is revisited.

_See also: `docs/MODULES.md` (skill grouping), `docs/distilled-principles.md` (cross-domain invariants),
`docs/graph/` (the L-adjacent knowledge graph)._
