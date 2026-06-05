---
title: Knowledge Graph -- Usage Policy + Edge Semantics
version: "2.0"
created: "2026-05-27"
updated: "2026-06-04"
---

# Rule 16: Knowledge Graph -- Usage Policy

## Overview

The knowledge graph (`platform_lib/knowledge_graph.py`, plain Python adjacency, derived from markdown) is a **navigation + integrity layer**, not a completeness/extraction layer. It is exposed to skills/LLM via `orc:graph`. The markdown corpus is the source of truth; the graph is derived and disposable (rebuilt lazily on first call, no disk cache).

No networkx, numpy, pyvis, or sentence-transformers dependency. Graph builds deterministically from frontmatter + body-regex in <1s for the current corpus (~200 nodes).

It answers: "what files relate to X", "what is structurally broken". It does **not** answer: "find every mention of X" or "is this exhaustive".

## When to Use `graph_context()` / the graph

- **Navigation / context-assembly** — seed reading with the most-related files to a character or theory within a token budget (orc:bootstrap, profile-lite, post-writer context loading).
- **Integrity audit** — `validate_graph()` surfaces dangling `cites_theory` targets (links to non-existent reference files) and orphan profile/material nodes.
- **Cross-cutting relationship discovery** — theory->citing-profiles, cross-character mentions, dyad members — where the relationship is not encoded in a single directory path.

## When to Keep glob / text-scan (NOT the graph)

- **Completeness-critical audits** that must find _absence_ or _every_ occurrence — unused theories, unlinked clinical terms, exhaustive citation counts. Use the framework text-scan scripts (`psy:ref-audit`, `psy:ref-scan`, `psy:ref-maintain`). See "Edge recall" below for why.
- **Single-character own-file gathering** — a bounded single directory. `rglob` of that directory is complete and optimal; `graph_context(char, hops=2)` returns a cross-contaminated superset (other characters via `cross_character` edges) and truncates at `max_files`.
- **Single-file schema validation** or flat directory listing — `glob` is simpler.

## Edge sources + recall (debugging)

| `source` attr | Layer | Catches                                                                                 | Recall caveat                                                                                                                               |
| ------------- | ----- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `frontmatter` | 1     | explicit YAML links                                                                     | high confidence (0.95)                                                                                                                      |
| `body_text`   | 2     | reference **slug** in prose (`cites_theory`), other character names (`cross_character`) | **English-slug-literal**: a theory written only in Vietnamese prose, or a single mention of a 1-token slug, produces NO `cites_theory` edge |

**Consequence:** `cites_theory` reflects _linked_ relationships, not an exhaustive text scan. Any decision requiring completeness (especially Vietnamese-aware citation detection) must read source markdown.

## Graph build behavior

`get_graph()` rebuilds on first call per process (or when `force_rebuild=True`). Small corpus (<1s build time) makes the full rebuild cheaper than disk-cache management. No SHA256 hash-checking, no incremental rebuild, no file cache. `get_graph(force_rebuild=True)` clears the module-level memo and rebuilds.

## Migration policy for skills

- New / modified skills doing **cross-cutting relationship discovery** SHOULD use `graph_context()` (opt-in).
- Skills doing **bounded single-directory gathering** or **completeness audits** keep `rglob`/text-scan.
- The graph is a supplementary signal, never a replacement for source-of-truth text scans in completeness-critical paths.

## Anti-Patterns

| Anti-pattern                                                  | Correct approach                                                                                |
| ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Use `graph_context` to prove a theory is unused               | Text-scan all profiles (`psy:ref-scan`) -- graph misses Vietnamese/plain-prose mentions          |
| Trust `files` as the complete set for a character at `hops=2` | `hops=1` + `node_types` for own-files; `hops=2` intentionally pulls related characters/theories |
| Hand-edit the graph in memory                                 | Edit the markdown; call `get_graph(force_rebuild=True)` to refresh                              |

## See Also

- `orc:graph` -- skill wrapper for query/stats/validate/rebuild
- Rule 02 (clinical-reference-usage), Rule 10 (reference-library-standard) -- citation/reference conventions the graph indexes
