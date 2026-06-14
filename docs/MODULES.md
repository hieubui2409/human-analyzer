# MODULES — Skill Grouping & Cross-Framework Dependency Map

Navigation map for the **68 project-owned skills** across 7 frameworks. Semi-derived from each
`SKILL.md` `metadata.dependencies` frontmatter + the CLAUDE.md catalog — **regenerate after skill
changes** (`orc:skill-stocktake --quick` catches count drift; `--conformance` checks structure).

Count reconciles with CLAUDE.md: **ORC 17 · PSY 16 · CRE 10 · GRO 8 · MAT 4 · COM 5 · EVL 8 = 68**.
ck-origin skills (`cook`, `plan`, `scout`, `skill-creator`, `/ck:*`, `/ckm:*`) are **excluded** — they
are dev tools used read-only, not part of the framework catalog.

## MAT — Materials (4)

| Skill         | Purpose                                        | Depends on   |
| ------------- | ---------------------------------------------- | ------------ |
| `mat:loader`  | Stage 1-2 ingest, classify, CRAAP, frontmatter | —            |
| `mat:indexer` | Stage 3-4 contradiction/gap/integration gate   | `mat:loader` |
| `mat:archive` | Soft-delete/archival with audit trail          | —            |
| `mat:rescore` | Flag materials needing CRAAP re-eval           | —            |

## PSY — Psychology (16)

| Skill                       | Purpose                                    | Depends on                                                     |
| --------------------------- | ------------------------------------------ | -------------------------------------------------------------- |
| `psy:wave`                  | 3-wave orchestration                       | `orc:bootstrap`, `psy:crossref`, `psy:ref-audit`, `mat:loader` |
| `psy:crossref`              | Cross-character 10-dimension validation    | —                                                              |
| `psy:ref-audit`             | Profile → reference accuracy               | —                                                              |
| `psy:ref-scan`              | Reference → profile coverage               | `psy:ref-audit`                                                |
| `psy:ref-create`            | Create reference files (schema)            | `psy:ref-audit`, `psy:ref-scan`                                |
| `psy:ref-maintain`          | Reference library cleanup                  | —                                                              |
| `psy:crisis-assess`         | DSM-5/ICD-11 crisis + risk levels          | `orc:bootstrap`, `psy:ref-audit`                               |
| `psy:hypothesis`            | Predict behavior given hypotheticals       | `orc:bootstrap`, `psy:ref-audit`                               |
| `psy:arc-tracker`           | Growth trajectories, hypothesis vs reality | `orc:bootstrap`, `psy:hypothesis`                              |
| `psy:narrative-twist`       | Handle revealed falsehoods + cascade       | `psy:crossref`                                                 |
| `psy:propagate`             | Cross-character event cascade              | —                                                              |
| `psy:timeline-sync`         | Cross-character timeline validation        | —                                                              |
| `psy:profile-lite`          | Compress profiles (~95%)                   | `orc:bootstrap`                                                |
| `psy:profile-compare`       | Side-by-side dimension comparison          | —                                                              |
| `psy:health-check`          | Profile completeness scoring               | —                                                              |
| `psy:relation-intelligence` | Mine dyad graph for content angles         | —                                                              |

## CRE — Content Creation (10)

| Skill                  | Purpose                                  | Depends on                                                                     |
| ---------------------- | ---------------------------------------- | ----------------------------------------------------------------------------- |
| `cre:post-writer`      | End-to-end content pipeline              | (delegates `cre:humanize`, `cre:evidence-scanner`)                            |
| `cre:exploring`        | 7-question exploration → CONTEXT.md      | —                                                                             |
| `cre:angle-discovery`  | Mine 6 frameworks → ranked angles        | —                                                                             |
| `cre:multiplatform`    | 1→N platform-native variants             | `cre:humanize`, `cre:evidence-scanner`, `cre:voice-audit`, `cre:privacy-guard` |
| `cre:repurpose`        | Adapt content 1→1 across platforms       | —                                                                             |
| `cre:prompt-leverage`  | 5-layer prompt strengthening             | `cre:exploring`                                                               |
| `cre:evidence-scanner` | Per-claim evidence-tier + Rule-09 gate   | —                                                                             |
| `cre:humanize`         | De-AI-slop scan (VN+EN) + opt-in rewrite | —                                                                             |
| `cre:voice-audit`      | Voice/tone consistency check             | `orc:bootstrap`                                                               |
| `cre:privacy-guard`    | Pre-publish privacy/confidentiality scan | —                                                                             |

## GRO — Growth (8)

| Skill                   | Purpose                               | Depends on |
| ----------------------- | ------------------------------------- | ---------- |
| `gro:career-path`       | Career trajectory + stage mapping     | —          |
| `gro:competency-map`    | Skills/competency + gap analysis      | —          |
| `gro:learning-profile`  | Learning style + acquisition patterns | —          |
| `gro:mentoring-track`   | Mentoring relationship documentation  | —          |
| `gro:career-forecast`   | LLM career projection [FORECAST]      | —          |
| `gro:compare`           | Side-by-side career comparison        | —          |
| `gro:milestone-tracker` | Career milestones actual vs planned   | —          |
| `gro:validate`          | Cross-check growth data consistency   | —          |

## ORC — Orchestration (17)

| Skill                 | Purpose                                                                                                                                  | Depends on                                                                                                           |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `orc:graph`           | Knowledge-graph query/visualize/validate + analytics/centrality/community/path subcommands (navigation + integrity + advisory analytics) | `platform_lib.knowledge_graph`, `knowledge_graph_analytics`, `knowledge_graph_discovery`, `knowledge_graph_advisory` |
| `orc:bootstrap`       | Load project context                                                                                                                     | `orc:session-state`                                                                                                  |
| `orc:session-state`   | Track session state + event queue                                                                                                        | —                                                                                                                    |
| `orc:classify`        | Risk classification + MAT gates                                                                                                          | —                                                                                                                    |
| `orc:intake`          | Route work type → skill chain                                                                                                            | `orc:classify`                                                                                                       |
| `orc:compounding`     | Extract session learnings → memory                                                                                                       | `orc:session-state`                                                                                                  |
| `orc:dream`           | Periodic memory consolidation                                                                                                            | `orc:compounding`                                                                                                    |
| `orc:agent-memory`    | Per-agent calibration memory                                                                                                             | `orc:compounding`                                                                                                    |
| `orc:observe`         | Cross-framework observation signals (passive telemetry → instinct)                                                                       | —                                                                                                                    |
| `orc:decisions`       | Append-only decision records                                                                                                             | —                                                                                                                    |
| `orc:event-log`       | Persistent event audit (JSONL)                                                                                                           | —                                                                                                                    |
| `orc:domain-router`   | Route domain events downstream                                                                                                           | —                                                                                                                    |
| `orc:cascade`         | Resolve multi-step event cascades                                                                                                        | —                                                                                                                    |
| `orc:audit`           | Cross-domain event consistency                                                                                                           | —                                                                                                                    |
| `orc:santa`           | Dual-reviewer quality gate                                                                                                               | `orc:classify`                                                                                                       |
| `orc:council`         | 4-voice decision framework                                                                                                               | `orc:decisions`                                                                                                      |
| `orc:skill-stocktake` | Skill catalog + CE-02 conformance audit                                                                                                  | —                                                                                                                    |

## COM — Common (5)

| Skill                 | Purpose                                                               | Depends on     |
| --------------------- | --------------------------------------------------------------------- | -------------- |
| `com:git`             | Project-aware git operations                                          | —              |
| `com:health-check`    | Session health monitoring                                             | —              |
| `com:rules`           | Modular rules management                                              | `orc:classify` |
| `com:skill-analytics` | Skill/script observability — 11 read-only lenses + profile-drift gate | —              |
| `com:release`         | Cut a versioned pack release — Keep a Changelog lock + manifest bump  | —              |

## EVL — Evaluation (8)

| Skill                | Purpose                                                          | Depends on  |
| -------------------- | --------------------------------------------------------------- | ----------- |
| `evl:score`          | Generic rubric scoring engine (gather → judge → aggregate)      | —           |
| `evl:standardize`    | Psychometric battery preset (Big Five + Dark Triad + attachment) | `evl:score` |
| `evl:fit`            | Role / casting-fit decision (CAST / CONDITIONAL / NO + veto)    | `evl:score` |
| `evl:compatibility`  | Dyad compatibility scoring on the relationship rubric           | `evl:score` |
| `evl:compare`        | Cross-character ranking on one rubric (uses written scorecards) | —           |
| `evl:track`          | Score-over-time diff + deterministic event attribution          | —           |
| `evl:validate`       | Rubric + scorecard structural checker                           | —           |
| `evl:rubric-import`  | External framework → canonical rubric draft                    | —           |

## Cross-framework dependency edges

The notable couplings that cross a framework boundary (intra-framework deps omitted):

```
psy:wave                   → orc:bootstrap, mat:loader   (PSY → ORC, MAT)
psy:crisis-assess          → orc:bootstrap               (PSY → ORC)
psy:hypothesis             → orc:bootstrap               (PSY → ORC)
psy:arc-tracker            → orc:bootstrap               (PSY → ORC)
psy:profile-lite           → orc:bootstrap               (PSY → ORC)
cre:voice-audit            → orc:bootstrap               (CRE → ORC)
com:rules                  → orc:classify                (COM → ORC)
cre:angle-discovery        ~> orc:graph (optional)       (CRE → ORC; default-off `--graph-signal`)
psy:relation-intelligence  ~> orc:graph (optional)       (PSY → ORC; default-off `--graph-signal`)
psy:ref-audit              ~> orc:graph (optional)       (PSY → ORC; advisory `coverage_gap_candidates`)
psy:timeline-sync          ~> orc:graph (optional)       (PSY → ORC; advisory `timeline_crosscheck_candidates`)
psy:propagate              ~> orc:graph (optional)       (PSY → ORC; advisory `propagation_suggestions`)
```

`~>` denotes an OPTIONAL/advisory dependency (skill works without it; `dependencies:[]` in
frontmatter remains accurate). Graph signals are default-off and tagged `authoritative:false`
where applicable — the consuming skill stays source-of-truth.

**Hub:** `orc:bootstrap` (5 inbound hard cross-framework edges) — the context-loading entry every
deep-analysis skill leans on. `orc:graph` (5 inbound optional edges) is the Tier-2 advisory hub.
`mat:loader` is the MAT-side hub (`psy:wave`, `mat:indexer`). Pure intra-framework chains
(`psy:ref-*`, `orc:session-state → compounding → dream`) stay within their domain, respecting
the event-bus boundary (Rule 12).

## Platform Library Modules

Shared Python helpers under `.claude/scripts/platform_lib/`. Skills import these directly; they
are not addressable via the skill catalog. KG modules (7):

| Module                       | Purpose                                                                                                                                                    | Consumers                                                                                                                                               |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `knowledge_graph`            | Core graph (Layers 1+2): `get_graph`, `graph_context`, `graph_stats`, `validate_graph`, `_resolve_entity`, `_undirected`                                   | `orc:graph` (all subcommands); embeddings/viz/cache/analytics/discovery/advisory modules                                                                |
| `knowledge_graph_embeddings` | Layer 3 cross-lingual (bge-m3 + Gemini fallback): `embed_corpus`, `cached_embedding_edges`, `cache_exists`                                                 | `knowledge_graph` (Layer 3 integration); `knowledge_graph_discovery`                                                                                    |
| `knowledge_graph_viz`        | Pyvis dark-theme `visualize_focus` HTML rendering                                                                                                          | `orc:graph visualize`                                                                                                                                   |
| `knowledge_graph_cache`      | SHA256 + JSON node-link cache (`save`/`load`/`current_hashes`/`diff`) — lazy/incremental                                                                   | `knowledge_graph.get_graph()`                                                                                                                           |
| `knowledge_graph_analytics`  | NetworkX built-ins: `centrality` / `community` / `find_paths` / `structural_holes` / `anomalies` / `analytics_summary`. Size-gated (≥500 nodes).           | `orc:graph` (analytics/centrality/community/path subcommands)                                                                                           |
| `knowledge_graph_discovery`  | Embedding-based content discovery: `similar_files` / `dyad_angle_signals` / `latent_links`. Shared `_adjacency()` memoized.                                | `cre:angle-discovery` + `psy:relation-intelligence` (via default-off `--graph-signal`); `knowledge_graph_advisory` (reuses `_adjacency`/`latent_links`) |
| `knowledge_graph_advisory`   | Tagged-advisory lenses (`authoritative:false` + `owning_skill`): `coverage_gap_candidates` / `timeline_crosscheck_candidates` / `propagation_suggestions`. | `psy:ref-audit` · `psy:timeline-sync` · `psy:propagate` (optional inputs)                                                                               |

Non-KG platform_lib modules (paths, markdown_parser, schema_validator, telemetry, instinct_store,
clinical_terms, env_utils, csv_search, profile_stats, formatters, errors, materials_classifier,
profile_validator, …) are catalogued in `CLAUDE.md` → Scripts Infrastructure.

## Maintenance

Regenerate when skills are added/renamed/retired. Source of truth = `SKILL.md` frontmatter; this
file is a derived view. `orc:skill-stocktake` reconciles the count and flags drift vs CLAUDE.md.
