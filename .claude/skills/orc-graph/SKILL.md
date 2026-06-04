---
name: orc:graph
description: "Search and visualize the character-corpus knowledge graph (NetworkX, derived from markdown). Use for finding files related to a character or theory, inspecting graph stats, and rendering an interactive ego-view. Triggers: 'graph context', 'related files', 'knowledge graph'."
argument-hint: "query <entity> [--hops N] [--types profile,material,reference] | stats | visualize <entity> | validate | rebuild | analytics | centrality [--metrics …] | community | path <a> <b>"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "orc-orchestration"
  position: "infrastructure"
  dependencies: []
---

# orc:graph — Knowledge Graph Query & Visualization

Thin LLM-facing wrapper over the project knowledge graph (`platform_lib.knowledge_graph`). The graph is **derived from markdown** (source of truth) and **disposable** — rebuilt lazily on stale read. No scripts of its own: the LLM calls the verified Python functions inline.

## When to Use

- **Exploration / navigation** — "which files relate to this character or theory?" to seed reading.
- **Relationship discovery** — cross-character links, theory→profile citations, dyad members.
- **Health snapshot** — node/edge counts by layer, dangling citations, orphans.
- **Visual map** — interactive ego-view HTML for a character/theory.

## When NOT to Use

- **Completeness-critical / exhaustive scanning** (audits that must find _absence_ — unused theories, unlinked terms, every citation incl. Vietnamese prose). Use the framework text-scan scripts (`psy:ref-audit`, `psy:ref-scan`) — see "Edge coverage" below.
- **Single-file schema validation** or flat single-directory listing — plain `glob` is simpler.

## API (call inline via venv python)

Interpreter: `.claude/skills/.venv/bin/python3` · `sys.path.insert(0, ".claude/scripts")` then `from platform_lib import knowledge_graph as kg`.

| Subcommand                     | Function                                                          | Returns                                                                               |
| ------------------------------ | ----------------------------------------------------------------- | ------------------------------------------------------------------------------------- | ------------- |
| `query <entity>`               | `kg.graph_context(entity, hops=2, node_types=None, max_files=50)` | `{entity, files, summary, token_estimate, node_count, edge_count}`                    |
| `stats`                        | `kg.graph_stats()`                                                | nodes/edges by type + `edges_by_source` + `embedding_layer`                           |
| `visualize <entity>`           | `kg.visualize_focus(entity, hops=2)`                              | path to written HTML (`""` if pyvis missing / unknown entity)                         |
| `validate`                     | `kg.validate_graph()`                                             | list of `{kind: missing_reference                                                     | orphan, ...}` |
| `rebuild`                      | `kg.get_graph(force_rebuild=True)`                                | rebuilt `DiGraph` (also refreshes cache)                                              |
| `analytics`                    | `kga.analytics_summary()`                                         | bundle: centrality + community + structural_holes + anomalies (size-gated)            |
| `centrality [--metrics m1,m2]` | `kga.centrality(metrics, top_n)`                                  | per-metric top-N nodes + `skipped` notes for gated metrics                            |
| `community`                    | `kga.community(algorithm)`                                        | partition + modularity (greedy default; Louvain opt-in if `python-louvain` installed) |
| `path <a> <b>`                 | `kga.find_paths(a, b, k)`                                         | shortest + K alternative simple paths (narrative distance)                            |

`entity` accepts: a character slug (`character-a`), a reference slug (`savior-complex`), a node key (`char:…`), or a file path. Unknown entity → empty result (never raises). `node_types` ∈ `{profile, material, reference, graph_dyad}`.

**Analytics subcommands**: `from platform_lib import knowledge_graph_analytics as kga`. Heavy metrics (betweenness, community, structural-holes) are size-gated by `knowledgeGraph.analytics.minNodesForHeavyMetrics` (default 500) — at small scale they emit `skipped` notes rather than degenerate output. Rank-based metrics are **low-discrimination** on a 3-character star-of-stars topology; advisory-only — never auto-act on a ranking, the LLM interprets ("hub character / story-circle").

### Examples

```bash
# files related to a character (1 hop = that character's own files; 2 hops reaches cited theories + linked characters)
/orc:graph query character-a --hops 1 --types profile,material

# profiles that cite a theory
/orc:graph query savior-complex --types profile

# graph health + interactive map
/orc:graph stats
/orc:graph visualize complex-ptsd
/orc:graph validate
```

## Edge coverage (read before trusting results)

Three discovery layers feed the graph; each has a different recall profile:

| Layer         | Source attr   | What it catches                                                                         | Caveat                                                                                                                           |
| ------------- | ------------- | --------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| 1 frontmatter | `frontmatter` | explicit YAML links                                                                     | high confidence (0.95)                                                                                                           |
| 2 body regex  | `body_text`   | reference **slug** in prose (`cites_theory`), other character names (`cross_character`) | **English-slug-literal** — a theory mentioned only in Vietnamese prose, or a single mention of a 1-token slug, is NOT edged here |
| 3 embedding   | `embedding`   | cross-lingual semantic similarity (bge-m3)                                              | firm-only ≥0.75; **sparse on profile↔reference** — does not reliably recover Vietnamese-only citations                           |

**Practical consequence:** `query`/`validate` reflect _linked_ relationships, not an exhaustive text scan. For "is this theory cited _anywhere_, including Vietnamese?" the text-scan scripts read the raw markdown and are authoritative. Treat graph output as a navigation aid; verify against source markdown for any decision with consequences.

## Cache behavior

`get_graph()` hash-checks every file on each call and incrementally rebuilds only changed files (never returns stale data). A project SessionStart hook warms the cache. `rebuild` forces a full rebuild. Generated artifacts (`.cache/`, `plans/visuals/knowledge-graph-*.html`) are git-ignored.

## Anti-Patterns

| Don't                                                             | Do                                                                                                  |
| ----------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| Use `query` to prove a theory is _unused_                         | Run `psy:ref-scan` text scan — graph misses Vietnamese/plain-prose mentions                         |
| Trust `files` as the complete set for a character at `hops=2`     | Use `hops=1` + `node_types` for own-files; `hops=2` intentionally pulls related characters/theories |
| Edit the cache or graph JSON by hand                              | Edit the markdown; the graph re-derives                                                             |
| Treat embedding edges as citations                                | They are semantic-similarity, not references                                                        |
| Trust `centrality`/`community` top-3 as discovery at 3-char scale | Top-3 = the 3 character hubs by construction; rank discrimination grows with corpus diversity       |
| Auto-act on a `centrality` ranking                                | Advisory only; LLM interprets, never an authoritative verdict                                       |

## See Also

- `docs/rules/16-knowledge-graph.md` — graph-vs-glob policy + edge-source reference
- `plans/260521-1508-knowledge-graph-networkx-architecture/` — design + phase history
- `psy:ref-audit`, `psy:ref-scan` — authoritative text-scan audits (source-of-truth, exhaustive)
