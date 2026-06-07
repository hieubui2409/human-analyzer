# Release Notes — frameworks v1.1.0

_Released 2026-06-07. Clinical-grade character-profile intelligence toolkit — 6 frameworks · 60 skills · 6 domain agents · 7 framework hooks · 33 platform-lib modules · 16 rules._

> Privacy: this toolkit ships ZERO character profiles, materials, graph, or references — the entire real-character corpus is pack-excluded. The released tarball is reproducible within the build toolchain (CI determinism-gated; the packed content is byte-identical across environments and `SHA256SUMS` is the reference) and passes a fail-closed whole-pack PII/secret scan with no carve-out.

## Highlights
- **Character roster externalised (code → data):** the roster moved out of `paths.py` into a pack-excluded `docs/profiles/characters.yaml`; the public `paths.py` API is unchanged.
- **New-character registration + drift invariant:** scaffolding auto-registers a character; an invariant fails on any roster↔profile mismatch.
- **PII-safe pack:** real names (display, full, romanised slug) + org/location extras live only in the excluded corpus; docs/tests/tools are name-free; a deterministic build + whole-pack scan gate it.
- **Framework-owned pack:** manifest ships only the 6 domain agents + 7 framework hooks (settings.json is filtered to wire exactly those); an independent scanner ratchet rejects any non-framework agent/hook.

## Framework & Skill Catalog

### ORC — Orchestration (17 skills)

- **`orc:agent-memory`** — Persistent memory for CK-domain agents (psychologist, content-strategist, growth-analyst).
- **`orc:audit`** — Audit cross-domain event consistency — verify all declarations match.
- **`orc:bootstrap`** — Bootstrap project context for human-analyzer sessions.
- **`orc:cascade`** — Orchestrate multi-step event cascades across domains.
- **`orc:classify`** — Classify task risk level and determine workflow ceremony before implementation.
- **`orc:compounding`** — Extract durable learnings after content or profile work.
- **`orc:council`** — 4-voice decision framework for ambiguous situations.
- **`orc:decisions`** — Record and retrieve character arc decisions.
- **`orc:domain-router`** — Route domain events to downstream skills based on git diff or explicit event.
- **`orc:dream`** — Periodic consolidation of character insights and storytelling patterns.
- **`orc:event-log`** — Persistent event logging and audit trail — append framework events (MAT.integrated, PSY.refresh, CRE.recalibrate, etc.) to a JSONL log and query with filters.
- **`orc:graph`** — Search the character-corpus knowledge graph (plain markdown-derived adjacency).
- **`orc:intake`** — Classify incoming work type and route to the optimal skill chain.
- **`orc:observe`** — Emit a cross-framework observation signal (passive telemetry) to the project observation stream — defense-pattern noticed, source low on CRAAP, voice drift, com…
- **`orc:santa`** — Dual-reviewer quality gate for high-risk changes.
- **`orc:session-state`** — Track session state across conversations — what profiles were updated, content created, decisions made.
- **`orc:skill-stocktake`** — Audit the project skill catalog — Quick Scan (counts per framework vs CLAUDE.md, frontmatter-metadata gaps, catalog drift) + Full Stocktake (pairwise descriptio…

### PSY — Psychology (16 skills)

- **`psy:arc-tracker`** — Track character growth arcs over time — compare hypothesis predictions vs actual profile evolution, verify milestones reached, and document character developmen…
- **`psy:crisis-assess`** — Assess and document mental health crisis indicators in character profiles using clinical frameworks (DSM-5, ICD-11).
- **`psy:crossref`** — Cross-character consistency validation — 10 dimensions (4 automated + 6 LLM judgment).
- **`psy:health-check`** — Profile completeness scoring — check all 25 expected profile files per character, score 0-100 per file, aggregate overall health score, and surface gaps.
- **`psy:hypothesis`** — Predict character behavior given hypothetical events using SOUL/DARKNESS/LIGHT/CHARACTERISTIC patterns + clinical reference theories.
- **`psy:narrative-twist`** — Handle revealed falsehoods and narrative corrections in character profiles.
- **`psy:profile-compare`** — Side-by-side character profile comparison — extract a specific dimension (e.g.
- **`psy:profile-lite`** — Compress full character profiles into token-efficient summaries (~100-150 lines per character vs ~700-1000 lines full).
- **`psy:propagate`** — Cross-character cascade analysis — when a profile section changes, detect which connected characters and profile files need review.
- **`psy:ref-audit`** — Audit clinical psychology references bidirectionally: profile→ref accuracy, ref→ref cross-linkage, and discover missing theories in profiles/materials/refs.
- **`psy:ref-create`** — Create new clinical psychological theory reference files in docs/references/ following mandatory schema.
- **`psy:ref-maintain`** — Reference library health audit — scan docs/references/ for unused theories, count citations across all profiles, flag zero-citation orphans, and surface coverag…
- **`psy:ref-scan`** — Scan clinical reference library and find where theories apply in character profiles.
- **`psy:relation-intelligence`** — Proactively mine the cross-character relationship graph for publishable content angles.
- **`psy:timeline-sync`** — Timeline date validation and consistency check — extracts dates from timeline files across characters, cross-compares shared events, and reports mismatches with…
- **`psy:wave`** — Orchestrate the 3-wave profile generation pipeline.

### CRE — Content Creation (10 skills)

- **`cre:angle-discovery`** — Discover publishable content angles by proactively mining all 6 frameworks — PSY growth-edges (emotional), MAT new materials (story), GRO milestones (profession…
- **`cre:evidence-scanner`** — Standalone, re-runnable evidence-tier safety gate for any content draft.
- **`cre:exploring`** — Structured exploration before content planning.
- **`cre:humanize`** — De-AI-slop / 'làm mềm' content so it reads like a human wrote it, not a machine.
- **`cre:multiplatform`** — Generate N platform-NATIVE content variants from one source/angle simultaneously (1→N) — LinkedIn/Facebook/Instagram/TikTok/YouTube/Twitter/blog.
- **`cre:post-writer`** — End-to-end post creation pipeline.
- **`cre:privacy-guard`** — Scan assets/ and cross-framework dirs for leaked PII, privacy tags, clinical terms, DSM/ICD codes.
- **`cre:prompt-leverage`** — Strengthen content prompts before execution.
- **`cre:repurpose`** — Adapt existing content from one platform to another while respecting platform constraints.
- **`cre:voice-audit`** — Audit published content for voice/tone consistency against character identity/writing-voice.md profiles.

### GRO — Growth (8 skills)

- **`gro:career-forecast`** — GRO framework career projection — gather current career data for LLM-powered trajectory forecasting.
- **`gro:career-path`** — GRO framework career trajectory analysis — gather career data from growth/career-path.md, identity/core.md, and materials for LLM analysis of decisions, inflect…
- **`gro:compare`** — GRO framework cross-character comparison — gather growth data from all characters for side-by-side career, competency, learning, and mentoring comparison.
- **`gro:competency-map`** — GRO framework competency inventory — gather skill data from growth/competencies.md, identity/core.md, and materials for LLM assessment using Dreyfus 7-level mod…
- **`gro:learning-profile`** — GRO framework learning profile analysis — gather learning data from growth/learning-profile.md and materials for LLM mapping using Kolb's Experiential Learning …
- **`gro:mentoring-track`** — GRO framework mentoring relationship documentation — gather mentoring data from growth/mentoring-map.md, relationships/ files, and materials for LLM insight ext…
- **`gro:milestone-tracker`** — GRO framework milestone tracking — gather career milestones from milestones.md and career-path.md to track actual vs planned progression.
- **`gro:validate`** — GRO framework validation — cross-check growth data consistency across career-path, competencies, learning-profile, and mentoring-map.

### MAT — Materials (4 skills)

- **`mat:archive`** — MAT framework material archival — filter and archive processed materials by character, date, tier, or status.
- **`mat:indexer`** — MAT framework indexer — contradiction detection, cross-reference validation, evidence tier verification, and material-to-profile linking.
- **`mat:loader`** — MAT framework material loader — ingest, classify, frontmatter, and normalize source materials into docs/materials/.
- **`mat:rescore`** — MAT framework CRAAP re-scoring — identify materials with missing, incomplete, or stale CRAAP scores and flag them for re-evaluation.

### COM — Common (5 skills)

- **`com:git`** — Git commit & push with conventional commit format for human-analyzer.
- **`com:health-check`** — Monitor Claude Code session health — detect stalls, API errors, process death for main/subagent/team sessions.
- **`com:release`** — Cut a versioned release of the frameworks pack via the Keep a Changelog lifecycle.
- **`com:rules`** — Validate changed files against docs/rules/*.md.
- **`com:skill-analytics`** — Observe and analyze the project's framework skills + scripts across eleven read-only lenses: infrastructure health, dependency graph, cascade topology, usage an…

## Domain Agents

- **content-strategist** — CRE domain specialist — content creation, voice consistency, privacy guard, cross-platform repurposing.
- **cross-validator** — Cross-domain validator — multi-character consistency, timeline synchronization, cross-reference validation across all 3 characters.
- **growth-analyst** — GRO domain specialist — career trajectory analysis, competency mapping, learning profile assessment, mentoring documentation.
- **material-analyst** — MAT domain specialist — material ingestion, classification, evidence tiers, CRAAP scoring.
- **profile-manager** — Profile CRUD operations — new character scaffolding, health checks, profile comparisons, and status reports.
- **psychologist** — PSY domain specialist — clinical profiling, psychological analysis, defense mechanisms, attachment styles, crisis assessment.

## Framework Hooks

- **detect-profile-drift-hook** — PostToolUse:Edit hook (M4, project-owned, CAP-1 clean).
- **gateguard-profile-protect** — gateguard-profile-protect.cjs - Block edits to sensitive profile files
- **observe-framework-signal** — PostToolUse hook: automatic cross-framework observation (B3, project-owned, no ck dependency).
- **pii-guard-on-write** — pii-guard-on-write.cjs — born-time PII write-guard (PreToolUse Edit|Write|MultiEdit).
- **profile-edit-reminder** — PostToolUse hook: profile-edit reminders (project-owned, no ck dependency).
- **rebuild-knowledge-graph** — Project-owned SessionStart warm-up for the knowledge graph.
- **write-framework-delta-compact-digest** — PreCompact hook: write the framework-delta compact-digest before /compact (C5, project-owned).

## Platform Library (`platform_lib`)

- **angle_scoring.py** — Shared scoring primitives for content-angle rankers (cre + psy).
- **asset_packages.py** — Shared helpers for resolving CRE asset-package files (Rule 03 manifest).
- **behavioral_clusters.py** — Behavioral cluster detection: HYBRID approach (regex pre-filter + LLM deep scan).
- **cache_store.py** — cache_store — the shared content-addressed cache primitive.
- **check_fence.py** — check_fence — advisory soft-fence scan (the pull-side companion to fs_guard).
- **clinical_terms.py** — Clinical term detection patterns and reference index builder.
- **csv_search.py** — BM25-based text search over CSV data for framework scripts.
- **encoding_utils.py** — Cross-platform console encoding for framework scripts.
- **env_utils.py** — Environment variable loading and API key resolution for framework scripts.
- **errors.py** — Structured error emission for skill scripts (I6).
- **event_routing.py** — Canonical ORC event-routing vocabulary — single source of truth.
- **evidence_tier_permissions.py** — Evidence-tier publish permissions — single source of truth for gate verdicts.
- **file_sensitivity.py** — File sensitivity classification for human-analyzer profile protection.
- **formatters.py** — Output formatting: markdown tables, JSON, summary blocks.
- **fs_guard.py** — fs_guard — per-framework write-jail for SCRIPT-driven disk writes.
- **growth_taxonomy.py** — Canonical GRO-domain vocabularies (Super / Kolb / Kram / Dreyfus).
- **humanizer_patterns.py** — humanizer_patterns — deterministic VN+EN AI-tell scanner (the ONE taxonomy home).
- **instinct_store.py** — Instinct store — atomic learnings with confidence scoring and JSONL persistence.
- **knowledge_graph.py** — Knowledge graph (Layer 1+2: frontmatter + body-scan edges) — plain Python adjacency over the markdown corpus.
- **markdown_parser.py** — Markdown section parser and metadata extractor.
- **materials_classifier.py** — Classify and inventory materials by type and processing state.
- **paths.py** — Project path constants and discovery utilities for PMC framework.
- **platform_constraints.py** — Single source of platform-native constraints — shared by cre:repurpose (1→1 adapt) and cre:multiplatform (1→N native generation).
- **preferences.py** — preferences — read/write per-project engagement knobs (deterministic writer).
- **privacy_tags.py** — Privacy-tag scanning shared between cre:privacy-guard scripts.
- **profile_stats.py** — Profile statistics: line counts, file inventory, cache validation.
- **roster_io.py** — roster_io — read/write helpers for docs/profiles/characters.yaml (the character roster DATA).
- **schema_validator.py** — Shared JSON Schema Draft-7 validation engine (C7).
- **skill_ids.py** — Canonical skill-id conversions shared across com:skill-analytics scripts.
- **skill_imports.py** — Shared AST introspection of framework-skill scripts → platform_lib import edges.
- **telemetry.py** — Project telemetry: consolidated observability sink + auto script-metrics (I4).
- **verdict_cache.py** — verdict_cache — re-runnable LLM-verdict cache for heuristic skills (crossref, voice-audit).
- **verdict_cache_keys.py** — verdict_cache_keys — deterministic cache-key grammar for re-runnable LLM verdicts.

## Rules

- **01-profile-structure.md** — Profile Structure Rules
- **02-clinical-reference-usage.md** — Clinical Reference Usage Rules
- **03-content-creation-pipeline.md** — Content Creation Pipeline Rules
- **04-materials-ingestion.md** — Materials Ingestion Rules
- **05-wave-pipeline.md** — Wave Pipeline Rules
- **06-crisis-protocol.md** — Crisis Documentation Protocol
- **07-narrative-twist-protocol.md** — Narrative Twist Protocol
- **08-cross-validation.md** — Cross-Validation Rules
- **09-confidentiality-protocol.md** — Confidentiality & Privacy Protocol
- **10-reference-library-standard.md** — Reference Library Standard
- **11-mat-pipeline.md** — Rule 11: MAT Pipeline — Materials Standardization Framework
- **12-orc-orchestration.md** — Rule 12: ORC Orchestration — Event-Driven Framework Coordination
- **13-orc-workflow.md** — Rule 13: ORC Workflow — End-to-End User Prompt to Published Content
- **14-cre-evidence-and-events.md** — CRE Evidence & Event Protocol
- **15-gro-framework.md** — Rule 15: GRO Framework — Career + Intelligence Growth
- **16-knowledge-graph.md** — Rule 16: Knowledge Graph -- Usage Policy

## Schemas

- `ck-config.schema.json`
- `diagnostics.schema.json`
- `event-jsonl.schema.json`
- `growth-career-path.schema.json`
- `growth-competency.schema.json`
- `material-frontmatter.schema.json`
- `material-schema.yaml`
- `profile-frontmatter.schema.json`
- `psychology-formulation.schema.json`
- `skill-schema.json`
- `universal-profile-schema.yaml`

_See the root `CHANGELOG.md` for the human-curated list of changes in this release._
