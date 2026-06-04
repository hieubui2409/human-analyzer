---
name: orc:graph
description: "Search the character-corpus knowledge graph (plain markdown-derived adjacency). Use for finding files related to a character or theory, inspecting graph stats, and validating integrity. Triggers: 'graph context', 'related files', 'knowledge graph'."
argument-hint: "query <entity> [--hops N] [--types profile,material,reference] | stats | validate | rebuild"
metadata:
  author: hieubt
  version: "2.0.0"
  category: "orc-orchestration"
  position: "infrastructure"
  dependencies: []
---

# orc:graph — Knowledge Graph Query

Thin LLM-facing wrapper over the project knowledge graph (`platform_lib.knowledge_graph`). The graph is **derived from markdown** (source of truth) and **disposable** — rebuilt lazily on first call. No scripts of its own: the LLM calls the verified Python functions inline. No networkx/numpy/pyvis dependency.

## When to Use

- **Exploration / navigation** — "which files relate to this character or theory?" to seed reading.
- **Relationship discovery** — cross-character links, theory->profile citations, dyad members.
- **Health snapshot** — node/edge counts by layer, dangling citations, orphans.

## When NOT to Use

- **Completeness-critical / exhaustive scanning** (audits that must find _absence_ — unused theories, unlinked terms, every citation incl. Vietnamese prose). Use the framework text-scan scripts (`psy:ref-audit`, `psy:ref-scan`) — see "Edge coverage" below.
- **Single-file schema validation** or flat single-directory listing — plain `glob` is simpler.

## API (call inline via venv python)

Interpreter: `.claude/skills/.venv/bin/python3` · `sys.path.insert(0, ".claude/scripts")` then `from platform_lib import knowledge_graph as kg`.

| Subcommand       | Function                                                           | Returns                                                                |
| ---------------- | ------------------------------------------------------------------ | ---------------------------------------------------------------------- |
| `query <entity>` | `kg.graph_context(entity, hops=2, node_types=None, max_files=50)` | `{entity, files, summary, token_estimate, node_count, edge_count}`     |
| `stats`          | `kg.graph_stats()`                                                | nodes/edges by type + `edges_by_source`                               |
| `validate`       | `kg.validate_graph()`                                             | list of `{kind: missing_reference\|orphan, ...}`                      |
| `rebuild`        | `kg.get_graph(force_rebuild=True)`                                | rebuilt `Graph` (clears module-level memo)                            |

`entity` accepts: a character slug (`character-a`), a reference slug (`savior-complex`), a node key (`char:...`), or a file path. Unknown entity -> empty result (never raises). `node_types` in `{profile, material, reference, graph_dyad}`.

### Examples

```bash
# files related to a character (1 hop = that character's own files; 2 hops reaches cited theories + linked characters)
/orc:graph query character-a --hops 1 --types profile,material

# profiles that cite a theory
/orc:graph query savior-complex --types profile

# graph health
/orc:graph stats
/orc:graph validate
```

## Edge coverage (read before trusting results)

Two discovery layers feed the graph:

| Layer         | Source attr   | What it catches                                                                         | Caveat                                                                                                                           |
| ------------- | ------------- | --------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| 1 frontmatter | `frontmatter` | explicit YAML links                                                                     | high confidence (0.95)                                                                                                           |
| 2 body regex  | `body_text`   | reference **slug** in prose (`cites_theory`), other character names (`cross_character`) | **English-slug-literal** — a theory mentioned only in Vietnamese prose, or a single mention of a 1-token slug, is NOT edged here |

**Practical consequence:** `query`/`validate` reflect _linked_ relationships, not an exhaustive text scan. For "is this theory cited _anywhere_, including Vietnamese?" the text-scan scripts read the raw markdown and are authoritative.

## Anti-Patterns

| Don't                                                             | Do                                                                                                  |
| ----------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| Use `query` to prove a theory is _unused_                         | Run `psy:ref-scan` text scan — graph misses Vietnamese/plain-prose mentions                         |
| Trust `files` as the complete set for a character at `hops=2`     | Use `hops=1` + `node_types` for own-files; `hops=2` intentionally pulls related characters/theories |
| Edit the cache or graph by hand                                   | Edit the markdown; the graph re-derives                                                             |

## See Also

- `docs/rules/16-knowledge-graph.md` — graph-vs-glob policy + edge-source reference
- `psy:ref-audit`, `psy:ref-scan` — authoritative text-scan audits (source-of-truth, exhaustive)
