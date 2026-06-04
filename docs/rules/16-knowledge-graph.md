---
title: Knowledge Graph — Usage Policy + Edge Semantics
version: "1.0"
created: "2026-05-27"
---

# Rule 16: Knowledge Graph — Usage Policy

## Overview

The knowledge graph (`platform_lib/knowledge_graph.py`, NetworkX, derived from markdown) is a **navigation + integrity layer**, not a completeness/extraction layer. It is exposed to skills/LLM via `orc:graph`. The markdown corpus is the source of truth; the graph is derived and disposable (rebuilt lazily on stale read).

It answers: "what files relate to X", "what is structurally broken", "show me the map". It does **not** answer: "find every mention of X" or "is this exhaustive".

## When to Use `graph_context()` / the graph

- **Navigation / context-assembly** — seed reading with the most-related files to a character or theory within a token budget (orc:bootstrap, profile-lite, post-writer context loading).
- **Integrity audit** — `validate_graph()` surfaces dangling `cites_theory` targets (links to non-existent reference files) and orphan profile/material nodes.
- **Cross-cutting relationship discovery** — theory→citing-profiles, cross-character mentions, dyad members — where the relationship is not encoded in a single directory path.
- **Visualization** — `visualize_focus()` ego-view for human comprehension.
- **Analytics** (`knowledge_graph_analytics`) — `path` (narrative distance), `anomalies` (over-hubs + degree outliers), and size-gated `centrality`/`community`/`structural_holes`. Lightweight metrics always-on; heavy metrics emit `skipped` notes below `minNodesForHeavyMetrics` (default 500) because rank discrimination is vanity on a 3-hub star-of-stars topology. **Advisory only — never auto-act on a ranking.**
- **Content discovery** (`knowledge_graph_discovery`) — `similar_files` / `dyad_angle_signals` / `latent_links`. Three deterministic noise filters (materials same-basename, both `analysis-*` prefix, INDEX/milestones/CURRENT-STATE meta-files) drop spike-verified noise classes. Fed into `cre:angle-discovery` + `psy:relation-intelligence` via opt-in `--graph-signal` flag (default off → output identical for same inputs).
- **Advisory consistency** (`knowledge_graph_advisory`) — `coverage_gap_candidates` / `timeline_crosscheck_candidates` / `propagation_suggestions`. Every row carries `authoritative:false` and an `owning_skill`; the graph FLAGS candidates, the consumer skill CONFIRMS. Text-scan + `psy:crossref` 10-dim verdict + `psy:propagate` PROPAGATION_MAP causal logic remain source-of-truth.

## When to Keep glob / text-scan (NOT the graph)

- **Completeness-critical audits** that must find _absence_ or _every_ occurrence — unused theories, unlinked clinical terms, exhaustive citation counts. Use the framework text-scan scripts (`psy:ref-audit`, `psy:ref-scan`, `psy:ref-maintain`). See "Edge recall" below for why.
- **Single-character own-file gathering** — a bounded single directory (`docs/profiles/{char}/`, `docs/materials/{char}/`). `rglob` of that directory is complete and optimal; `graph_context(char, hops=2)` returns a cross-contaminated superset (other characters via `cross_character` edges) and truncates at `max_files`.
- **Single-file schema validation** or flat directory listing — `glob` is simpler.

## Edge sources + recall (debugging)

| `source` attr | Layer | Catches                                                                                 | Recall caveat                                                                                                                               |
| ------------- | ----- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `frontmatter` | 1     | explicit YAML links                                                                     | high confidence (0.95)                                                                                                                      |
| `body_text`   | 2     | reference **slug** in prose (`cites_theory`), other character names (`cross_character`) | **English-slug-literal**: a theory written only in Vietnamese prose, or a single mention of a 1-token slug, produces NO `cites_theory` edge |
| `embedding`   | 3     | cross-lingual semantic similarity (bge-m3)                                              | firm-only ≥ threshold; **sparse on profile↔reference** — does not reliably recover Vietnamese-only citations                                |

**Consequence:** `cites_theory` reflects _linked_ relationships, not an exhaustive text scan. Any decision requiring completeness (especially Vietnamese-aware citation detection) must read source markdown — the graph is a navigation aid, not authoritative for absence.

## Cache behavior

`get_graph()` hash-checks every file on each call and incrementally rebuilds only changed files — never returns stale data. A project SessionStart hook warms the cache. `get_graph(force_rebuild=True)` forces a full rebuild. Generated artifacts (`.cache/`, `plans/visuals/knowledge-graph-*.html`) are git-ignored.

## Migration policy for skills

- New / modified skills doing **cross-cutting relationship discovery** SHOULD use `graph_context()` (opt-in).
- Skills doing **bounded single-directory gathering** or **completeness audits** keep `rglob`/text-scan — migrating them to the graph adds truncation risk and lossy recall with no benefit.
- The graph is a supplementary signal, never a replacement for source-of-truth text scans in completeness-critical paths.

## Anti-Patterns

| Anti-pattern                                                  | Correct approach                                                                                |
| ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Use `graph_context` to prove a theory is unused               | Text-scan all profiles (`psy:ref-scan`) — graph misses Vietnamese/plain-prose mentions          |
| Trust `files` as the complete set for a character at `hops=2` | `hops=1` + `node_types` for own-files; `hops=2` intentionally pulls related characters/theories |
| Treat `embedding` edges as citations                          | They are semantic similarity, not references                                                    |
| Hand-edit the cache or graph JSON                             | Edit the markdown; the graph re-derives                                                         |

## See Also

- `orc:graph` — skill wrapper for query/stats/visualize/validate/rebuild/analytics/centrality/community/path
- `plans/260521-1508-knowledge-graph-networkx-architecture/` — design + phase history
- Rule 02 (clinical-reference-usage), Rule 10 (reference-library-standard) — citation/reference conventions the graph indexes

## Cut + Deferred features

The following capabilities were considered and excluded from the navigation/discovery/advisory lenses to keep the surface honest and to avoid eroding trust in safety-sensitive consumer skills:

| Item                                                                                                                                                             | Status             | Reason                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `contradiction_candidates` (cross-character semantically-similar pairs flagged as conflicts)                                                                     | **CUT**            | Cosine measures topical closeness, the structural opposite of contradiction — fires on the densest profile↔profile edges, ~all false positives, would flood `psy:crossref` and erode its 10-dim verdict. The graph has no proposition extraction; `check_narrative_twist:true` is a tag, not a check. `psy:crossref` already covers genuine cross-character contradiction via its timeline / relationship / fact dimensions. |
| `triangulate(entity, hops, top_n)` (re-rank `graph_context` reachable set by embedding similarity to seed)                                                       | **CUT**            | Built on top of the verified `graph_context` 50-cap + cross-character-leak primitive — re-ranking polishes a corrupted candidate pool. The cap is scale-invariant: leak at small scale, truncation at large. Fixing requires either re-litigating the verified-sticky primitive decision or a dedicated reachable-set replacement.                                                                                           |
| `centrality`/`community`/`structural_holes` (heavy metrics) below `minNodesForHeavyMetrics`                                                                      | **DEFERRED**       | Auto-activates at corpus scale. Top-3 = the 3 character hubs by topology; rank discrimination grows with comparably-connected nodes that the small corpus structurally does not yet have.                                                                                                                                                                                                                                    |
| Temporal embedding arcs · ref link-prediction · multimodal · engagement-rank · GraphRAG summaries · semantic-compression · archetype-embedding · audit-migration | **DEFERRED / CUT** | Surveyed during use-case triage; either proven negative (audit-migration: completeness undercounted by graph) or unproven positive (engagement-rank: no telemetry to validate). Revisit only with new empirical data justifying ROI flip.                                                                                                                                                                                    |
