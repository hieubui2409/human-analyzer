# Release Notes — frameworks v1.0.0

_Released 2026-06-06. Clinical-grade character-profile intelligence toolkit — 6 frameworks · 59 skills · 6 domain agents · 6 framework hooks · 33 platform-lib modules · 16 rules._

> Privacy: this toolkit ships ZERO character profiles, materials, graph, or references — the entire real-character corpus is pack-excluded. The released tarball is byte-reproducible and passes a fail-closed whole-pack PII/secret scan with no carve-out.

## Highlights
- **Character roster externalised (code → data):** the roster moved out of `paths.py` into a pack-excluded `docs/profiles/characters.yaml`; the public `paths.py` API is unchanged.
- **New-character registration + drift invariant:** scaffolding auto-registers a character; an invariant fails on any roster↔profile mismatch.
- **PII-safe pack:** real names (display, full, romanised slug) + org/location extras live only in the excluded corpus; docs/tests/tools are name-free; a deterministic build + whole-pack scan gate it.
- **Framework-owned pack:** manifest ships only the 6 domain agents + 6 framework hooks (settings.json is filtered to wire exactly those); an independent scanner ratchet rejects any non-framework agent/hook.

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

### COM — Common (4 skills)

- **`com:git`** — Git commit & push with conventional commit format for human-analyzer.
- **`com:health-check`** — Monitor Claude Code session health — detect stalls, API errors, process death for main/subagent/team sessions.
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

## Change History (PII-filtered commit subjects)

- Merge branch 'feat/profile-standardization-vietnamese'
- Merge feat/profile-standardization-vietnamese into master
- Merge master (feat KG Tier-2 + ck toolkit) into framework review branch
- Merge remote-tracking branch 'origin/claude/framework-profiles-review-SzTsE'
- build(pack): drop references+STANDARDIZE, add agents/hooks/config/nav-docs
- chore(config): add Antigravity RTK rules and session cascade event log
- chore(config): cleanup stale skills/agents/hooks, add new infrastructure
- chore(config): refresh tracked skills venv bytecode
- chore(config): remove CKM leftover toolkit
- chore(config): stop tracking ck hook runtime log
- chore(config): stop tracking project-local skills venv
- chore(config): sync ClaudeKit-engineer update (skills, agents, hooks, scripts)
- chore(config): sync goal notes, session state, and runtime logs
- chore(config): use PATH-resolved ccstatusline + homelab global-strip report
- chore(config,plans): reclassify no-ck boundary to Option 1 (project owns its hooks)
- chore(scripts): add validation scripts, plan helpers, remove stale workflows
- chore: rename 16 Vietnamese material files to kebab-case
- chore: rename 3 Vietnamese material directories to kebab-case
- chore: update all Source tags and create missing INDEX.md files
- chore: update notes, journal entries, and session state
- chore: update plans, reports, profiles, and cleanup stale artifacts
- ci(frameworks): persist CI workflows, bug_class gate, pyproject + wiring (index-drift recovery)
- ci(frameworks): stand up CI + bug_class regression gate
- docs(backlog): mark standardization items applied, point to STANDARDIZE ledger
- docs(backlog): mine cleanmatic-skills patterns for framework adaptation
- docs(brainstorm): cre:humanize de-AI-slop design (converged, user-approved)
- docs(config): add subagent API error retry rule to CLAUDE.md
- docs(config): update CLAUDE.md + add plans and research reports
- docs(config): update CLAUDE.md and health-check plan for com namespace rename
- docs(framework): update rules, CLAUDE.md, and user manuals for new skills and 10-dim crossref
- docs(frameworks): operating-guide routing + per-framework changelogs; finalize applied-pattern ledger
- docs(gro): populate growth/ files for all 3 characters + INDEX + indexer update
- docs(materials): update MAT frontmatter and evidence tiers across all characters
- docs(orc): update CLAUDE.md, rules, and project docs for 5-framework architecture
- docs(plan): PII-safe release pack + roster externalization + registration + v1.0.0 (redteam+tdd)
- docs(plan): add phase-04 pack-hardening, phase-05 release-v1.0.0, partial red-team notes
- docs(plan): convergence cycles 1-10 final report; mark plan completed (17/17 BL applied, all gates green)
- docs(plan): cre:humanize TDD implementation plan + red-team review
- docs(plan): roster externalization + anonymization plan (awaiting approval)
- docs(plans): CE-02 conformance baseline — 58 project-owned skills, 0 BLOCK
- docs(plans): KG plan spec sync + 10-cycle project-verification reports
- docs(plans): add 13-batch re-audit to capstone (silent-except / non-standard-error scan)
- docs(plans): add 9-wave deep review reports and fix psy-crossref script
- docs(plans): add Batch 3 instinct-model reports and monitoring-tools plan
- docs(plans): add CAP-5 GPU acceleration decision to final capstone
- docs(plans): add ECC Batches 6-11 + 5-wave capstone, reconcile KG/Monitoring, ck-compliance audit
- docs(plans): add core framework delivery plan (6 phases)
- docs(plans): add driver-update display-break risk + rollback to GPU paths
- docs(plans): consolidated re-validation + fresh red-team of all remaining batches
- docs(plans): expand KG Phase 7 into Tier-2 sub-phases (7b-7e) + pre-flight scan
- docs(plans): expand e2e scenario report to 34 scenarios (90.4 avg)
- docs(plans): mark Batch 5 B2 complete, defer B1 dispatcher with design notes
- docs(plans): note 3 optional GPU acceleration paths for KG embedding
- docs(plans): record B1 dispatcher retirement + B9 schema/stocktake plans
- docs(profile): update profiles for all 3 characters with 9-wave deep review fixes
- docs(readme): comprehensive bilingual README with mermaid diagrams + full skill catalog
- docs(review): cycle 20 convergence — session 11-20 ledger, all gates green
- docs(review): cycle-10 final verification + 10-cycle consolidated summary
- docs(review): cycle-3 convergence scan — lib fan-in, SKILL deps, smoke (advisory only)
- docs(review): cycle-4 corpus-integrity convergence (zero findings)
- docs(review): cycle-9 cross-character structural integrity (zero findings)
- docs(review): cycles 7-8 — constant/path consistency (clean) + asset privacy triage
- docs(review): finalize 10-cycle log + final state summary
- docs(review): sync status for orc/mat/gro/lib fixes landed in prior commits
- docs(skills): bilingual 4-doc spine for all 58 framework skills
- docs(verify): Phases 5+8+9 — cross-validation, skills dual validation, final verification
- docs: add knowledge architecture, MODULES map, distilled principles (Batch 11)
- docs: rewrite CLAUDE.md lean + add README.md
- docs: sync GOAL state + add KG/code-review session reports
- docs: sync MODULES + CLAUDE + NOTES for KG Tier-2
- docs: sync skill catalog for com:skill-analytics + mark B12 monitoring plan complete
- docs: update CLAUDE.md, add plans/reports from recent sessions
- feat(com): add com:skill-analytics — skill/script observability (Monitoring P2)
- feat(com): per-project engagement preferences (deterministic enum-guarded writer)
- feat(config): KG Layer 3 firm-only embedding edges (reviewLow 0.75)
- feat(config): KG Phase 4 — pyvis ego-view visualization module
- feat(config): KG Phase 5 — SHA256 lazy/incremental graph cache
- feat(config): KG Tier-2 analytics/discovery/advisory lenses + graph-signal
- feat(config): add C7 schema validation + C3 orc:skill-stocktake (Batch 9)
- feat(config): add CE-02 progressive-disclosure conformance gate (Batch 9 Phase 4)
- feat(config): add GateGuard profile-protection hook and sensitivity checker
- feat(config): add KG Layer 2 body-text edge discovery (slug + character regex)
- feat(config): add KG Phase 3a graph_context discovery API
- feat(config): add KG Phase 3b embedding Layer 3 (cross-lingual, code+tests)
- feat(config): add com:health-check session health monitoring skill
- feat(config): add com:skill-analytics dashboard + memory-health lenses (B12 P4)
- feat(config): add com:skill-analytics reliability/forensics/workflow lenses (B12 P5)
- feat(config): add com:skill-analytics usage/coverage/content lenses (B12 P3)
- feat(config): add context-budget gauge hook (70/85 two-tier, Monitoring addendum)
- feat(config): add health-check stall suppression for waiting states
- feat(config): add orc:graph skill + Rule 16 knowledge-graph usage policy
- feat(config): add orc:santa dual-review gate and orc:council decision framework
- feat(config): add profile-drift gate + bash/stop telemetry hooks (B12 P6+P7)
- feat(config): add project observation + compact-digest hooks + script test matrix (Batch 10)
- feat(config): add structured error telemetry (I6, B12 P6)
- feat(config): consolidate PreToolUse hooks into single dispatcher (B1)
- feat(config): gitignore ephemeral context-gauge telemetry sink
- feat(config): guard KG embedding against oversized/base64 blobs
- feat(config): knowledge graph Layer 1 — NetworkX frontmatter edges (KG Phase 1)
- feat(config): make KG embedding tunables config-driven via framework-config.json
- feat(config): monitoring P1 — telemetry foundation + consolidated sink
- feat(config): partition event log into 6 framework JSONL streams (B2)
- feat(config): raise KG embedding maxChunksPerFile to 60 (config + fallback)
- feat(config): update ck toolkit to v2.19.2-beta.4
- feat(config): warn (not silent) on oversized/malformed corpus files in KG embedding
- feat(cre): add angle-discovery + multiplatform skills (Batch 7)
- feat(cre): cre:humanize de-AI-slop scanner + gate wiring
- feat(cre,psy): add evidence-scanner + relation-intelligence skills (Batch 6)
- feat(ecc): implement Batch 1 — A2 voice + A6 governance + B5 catalog + C8 unicode
- feat(ecc): implement Batch 2 (A3 GateGuard + B6 sensitivity) and Batch 3 (A5 instinct model)
- feat(framework): add 8 skills, 5 agents, hybrid routing, platform_lib consolidation
- feat(framework): implement MAT+PSY+CRE pipelines, MPC event router, and user docs
- feat(frameworks): deterministic write-fence + content-addressed cache infra + runnable pytest
- feat(frameworks): resolve deferred review items (Q1/Q2/Q4) from owner interview
- feat(gro): add 4 advanced GRO skills — mentoring-track, career-forecast, compare, milestone-tracker
- feat(gro): add 4 core GRO skills — career-path, competency-map, learning-profile, validate
- feat(gro): add GRO framework infrastructure — paths.py, rules, directories, tests
- feat(orc): add 3 new ORC skills + GRO coverage across all 9 existing skills
- feat(pack): reproducible toolkit packaging + release; README/CLAUDE refresh to skill-doc standard
- feat(psy,cre): re-runnable verdict cache + GATE guardrails + skill-doc spine
- feat(skills): update chrome-profile, cti-expert, tech-graph skills + toolkit config
- fix(com): align token window, share skill-id canon, harden git scripts, sync rule count
- fix(com): centralize import introspection, fix table width + empty-file scoring
- fix(com-health-check): narrow Signal 2 to last-line-only, keep errors visible when DEAD
- fix(com-health-check): stop STALL spam for completed/dead subagents
- fix(config): KG cache build-stamp + embedding cache dimension guard
- fix(config): correct skill count 49->51 after santa+council, add post-batch cross-check report
- fix(config): keep 4 cross-machine sinks (instincts, gateguard-audit, growth-signals, privacy-audit)
- fix(config): preserve persistent telemetry in VCS; relocate tracked sinks
- fix(config): resolve engineer-origin hook paths via $CLAUDE_PROJECT_DIR
- fix(config): stop tracking .claude/.env + repair .gitignore newline
- fix(config): stop tracking ephemeral runtime state + cascade-events sink
- fix(config): untrack ephemeral audit/signal sinks; instincts stays cross-machine
- fix(cre): wire Rule-09 privacy enforcement, align asset manifest, share angle scoring
- fix(docs): correct profile file-count (21->25) + profile-lite cache path + rule-10 link
- fix(frameworks): cycle-1 correctness/DRY fixes across GRO/MAT/PSY/COM + platform_lib
- fix(frameworks): cycle-1 root-cause fixes — frontmatter parser, tier helper, DRY + cleanup
- fix(frameworks): cycle-2 — DOB-parse bug, KG-derived connections, scale + except hygiene
- fix(frameworks): purge stale project branding + dedupe memory-dir resolution
- fix(guides): cache-mechanism accuracy — crossref uses content-hash, profile-lite uses git-hash+dirty-check
- fix(guides): correct operating-guide relative links to skill GUIDEs (../ -> ../../)
- fix(lib): make check_fence/verdict_cache/preferences runnable both standalone and as package
- fix(mat): make contradiction detector gather overlap signals, not verdicts
- fix(materials): normalize CRAAP scoring schema and processing_status
- fix(materials): strip 4 oversized inline base64 image blobs from Nhân vật C newspaper material
- fix(orc): correct stale query-event-log script reference in event-log SKILL.md
- fix(orc): cycle-5 — intake stops suggesting mat:loader for unmatched tasks
- fix(orc): detect real skill prefixes in intake, purge stale lucas: strings
- fix(orc): document cycle 12-13 regression rerun + event-system convergence
- fix(orc): repair orc:audit literal-scraping regression + reconcile event registry
- fix(profile): correct broken relative links in profile subdir files
- fix(psy): complete profile_validator retirement in crossref consumer
- fix(psy): conform 11 references to Rule-10 schema + index abandonment-schema
- fix(psy): normalize timeline dates, sync ref-audit script refs, document scopes
- fix(psy): resolve character aliases in profile schema validator
- fix(psy): timeline-sync precision — stop conflating distinct same-keyword events
- fix(psy,com): green the pytest suite — real bugs + dead-test cleanup
- fix(psy,cre,mat): recurse nested materials + resolve character aliases
- fix(psy-ref-create): Vietnamese reference template matching corpus + validator
- fix(refs): normalize 9 ref headings to canonical schema (Định nghĩa/Cơ chế)
- fix(refs,corpus): create 5 clinical refs + remap stale links + remove dead legacy dir
- fix(scripts): resolve pre-existing parser bugs found during validation
- fix(scripts): scaffold full 25-file profile (add growth/) + de-brand init/inject scripts
- fix(telemetry): empty growth-signals.jsonl (clear manual-validation junk)
- fix(tests): repoint stale mpc-* skill paths to orc-* after rename
- fix: MAT/GRO/evidence-tier batch — pipeline states, schema docs, script refs, signal gathering
- merge: framework review + cre:humanize + PII-safe release plan into master
- refactor(config): retire B1 hook-dispatcher, register gateguard natively
- refactor(config): sever last project-hook ck deps (CAP-1) + harden test isolation
- refactor(guides): home shared operating references under .claude/, wire into CLAUDE.md + skills
- refactor(guides): move shared refs to skills/_framework-shared/references (mirror _shared convention)
- refactor(lib): remove 7 dead orphan functions from platform_lib
- refactor(lib): share date/platform constants, drop dead modules, fix instinct dedup
- refactor(lib): share date/platform constants, fix instinct dedup, advisory routing notes
- refactor(orc): consolidate event-routing into single platform_lib source of truth
- refactor(orc): rename mpc-* directories to orc-* (9 skills + 2 rules files)
- refactor(orc): update all MPC→ORC references across SKILL.md, rules, CLAUDE.md, scripts, state.json
- refactor(profile): remove old flat profile files (Nhân vật A, Nhân vật B)
- refactor(profiles): Nhân vật C profile standardization — legacy refs + family.md split
- refactor(profiles): Nhân vật A profile standardization — legacy refs + family.md split
- refactor(profiles): Nhân vật B profile standardization — legacy refs + family.md split
- refactor(psy): centralize dyad pairs + character search aliases in paths.py
- refactor(psy): retire profile_validator, validate profiles via authoritative schema engine
- refactor(scripts): Phase 7 — paths.py + 8 scripts + tests + SKILL.md + rules
- refactor: drop networkx/numpy/pyvis/sentence-transformers; replace KG with plain-Python adjacency
- telemetry: append session gateguard audit entry (tracked audit sink)
- test(bug_class): guard memory-dir slug + project-name regressions; centralize project_dir
- test(config): KG lens test suites + shared singleton-reset fixture
- test(e2e): synthetic-fixture pipeline harness across all 6 frameworks
- test(eval): golden-case harness for deterministic skills
- test(framework): add comprehensive test suite with 273+ tests and LLM E2E scenarios
- test(frameworks): cycle-6 — stop tests masking failures as skips
- test(hooks): repoint test-ckignore to scout-block run()
- test(instinct): drop removed-mutator tests; doc applied cleanmatic patterns
- test(plans): KG Phase 6 — validation + benchmark (reuses schema_validator)
- test(routing): parametrize only over routable scenarios, drop runtime skip noise
- test: persist audit/event telemetry sinks emitted during review verification runs
