# CLAUDE.md

Clinical-grade **character profile intelligence system** for storytelling + content creation. Each character = deep, evidence-backed psychological profile feeding platform-native content. Built to **scale to many characters** (currently 3) — never hardcode character specifics in shared logic; resolve dynamically via `paths.py`.

---

## Architecture

Four domain frameworks + orchestrator + common toolkit, wired by an event bus:

```
MAT (Input) → PSY (Analysis) → CRE (Output)
                  ↑ ORC (Orchestration) ↑
            GRO (Growth) ↗ PSY + CRE
```

| FW | Domain | Data location | Purpose |
|----|--------|---------------|---------|
| **MAT** | Materials | `docs/materials/` | Evidence ingestion, tiers, CRAAP |
| **PSY** | Psychology | `docs/profiles/` + `docs/references/` + `docs/graph/` | Clinical profiling, 5P formulation |
| **CRE** | Content | `assets/` | Platform content creation |
| **GRO** | Growth | `docs/profiles/*/growth/` | Career + competency intelligence |
| **ORC** | Coordination | `.claude/` | Event routing, domain boundaries |
| **COM** | Utilities | `.claude/` | Git, health-check, rules |

**Event pipeline:** `MAT.integrated → PSY.refresh → CRE.recalibrate` · `GRO.assessed|mentored → PSY.refresh → CRE.recalibrate`. Domain boundaries enforced — each FW owns its data, communicates via events not cross-domain writes (Rule 12).

**Design principle:** scripts do deterministic gathering (may over-flag); the LLM does heuristic judgment. Never delegate reasoning to scripts.

---

## Load on Demand

Pull a reference only when its topic is active. **Exception:** load `gates-and-anti-rationalization.md` **every turn**.

| Need | Load |
|------|------|
| **Gates / anti-rationalization** (every turn) | `.claude/skills/_framework-shared/references/gates-and-anti-rationalization.md` |
| Skills (60 — ORC 17·PSY 16·CRE 10·GRO 8·MAT 4·COM 5) | harness skill list (auto-injected) + `docs/MODULES.md` (grouping + deps) |
| Per-framework skill→trigger→GUIDE routing | `.claude/skills/_framework-shared/references/{orc,psy,cre,gro,mat,com}-operating-guide.md` |
| Directory structure + profile 25-file schema | `docs/rules/01-profile-structure.md` |
| The 16 rules | `docs/rules/{01..16}-*.md` |
| Workflow tracks (MAT→PSY→CRE + GRO cascades) | `docs/rules/13-orc-workflow.md` |
| Scripts + `platform_lib/` modules + venv usage | `docs/scripts-infrastructure.md` |
| Knowledge map (6 layers) · cross-domain invariants | `docs/knowledge-architecture.md` · `docs/distilled-principles.md` |
| Other operating refs (verdict cache, doc-spine) | `.claude/skills/_framework-shared/references/` |

Asset package convention: `assets/{platform}/{YYMMDD}-{slug}/` → `post.txt`, `image-prompts.txt`, `images/`, `README.txt`.

---

## Operational Notices

**Subagent API retry** — Agent-tool result with a transient API error (`API Error`, `JSON Parse error`, `Unexpected EOF`, `Internal Server Error`, `Service Unavailable`, `ECONNRESET`, `socket hang up`) → auto-retry **once**, identical. Never retry on: `rate_limit`/`429`, `credit`/`billing`, `context_length_exceeded`, `invalid_api_key`.

**Auto-monitoring** — Auto-invoke `com:health-check` for subagents only when the user confirms monitoring OR a health Monitor already runs. Never auto-spawn silently.

**RTK** — Token-optimized CLI proxy (60-90% savings). Hook-based: `git status` → `rtk git status`. Meta: `rtk gain [--history]`, `rtk discover`, `rtk proxy <cmd>`.

**Scripts venv** — `.claude/skills/.venv/bin/python3 .claude/skills/{fw}-{skill}/scripts/{script}.py` (project is self-contained).

**Self-contained** — All skills/agents/hooks/rules/scripts local under `.claude/`. Global `~/.claude/` is runtime-only.

---

_Updated: 2026-06-08_
