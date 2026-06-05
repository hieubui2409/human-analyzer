# Character Profile Intelligence System

A clinical-grade system that turns deep, evidence-backed psychological profiles of characters into
platform-native content. Built to **scale from a handful of characters to many** — tooling is
character-agnostic and resolves subjects dynamically via `paths.py`.

> **For Claude Code / LLM agents:** read [`CLAUDE.md`](./CLAUDE.md) (architecture + rules + workflow) and
> the rule files under [`docs/rules/`](./docs/rules/). Every skill ships a 4-doc spine —
> `SKILL.md` (contract) + `README.md` + `GUIDE-EN.md` + `GUIDE-VI.md`. This README is the human entry point.
>
> Tiếng Việt: jump to [**# Tiếng Việt**](#tiếng-việt) below.

---

## What it does

1. **Ingest** raw source material (transcripts, interviews, logs, articles) and score it for evidence quality.
2. **Analyze** it into a structured clinical profile — case formulation, defenses, attachment, trauma, strengths, timeline, growth.
3. **Generate** platform content (Facebook, LinkedIn, blog, …), gated by evidence tier and confidentiality.

Everything is event-driven: ingesting material cascades into a profile refresh, which cascades into content recalibration.

```
MAT (Input) → PSY (Analysis) → CRE (Output)
                  ↑ ORC (Orchestration) ↑
            GRO (Growth) ↗ PSY + CRE
```

**58 framework skills** across 6 frameworks, invoked as `{framework}:{skill}` (e.g. `psy:crossref`). The
full catalog with per-skill descriptions is in [`CLAUDE.md`](./CLAUDE.md); per-skill walkthroughs are in each
skill's `GUIDE-EN.md` / `GUIDE-VI.md`.

---

## The six frameworks

### `MAT` — Materials (input) · 4 skills

**What it does:** ingests + classifies source material into `docs/materials/` with evidence tiers (T1–T5) and
CRAAP quality scores, through a 5-stage pipeline (raw → extracted → analyzed → validated → integrated). Material
must be **integrated before PSY may analyse it**.

**Deep links:** `mat:loader` · `mat:indexer` · `mat:archive` · `mat:rescore` (see each skill's `GUIDE-EN.md`) ·
rule [`11-mat-pipeline`](./docs/rules/11-mat-pipeline.md).

**What it does NOT do:** does not write outside `docs/materials/` (Rule 12); does not analyse psychology (that's PSY); does not invent evidence tiers from CRAAP (tier = source type, CRAAP = separate quality gate).

### `PSY` — Psychology (analysis) · 16 skills

**What it does:** builds + refreshes the clinical 5P formulation, defenses, attachment, diagnostics (Big Five +
ICD-11), trauma, strengths, timeline, and cross-character consistency from integrated material + the theory library.

**Deep links:** `psy:wave` (3-wave build) · `psy:crossref` (10-dimension consistency) · `psy:crisis-assess` ·
`psy:health-check` · `psy:timeline-sync` · rules [`01`](./docs/rules/01-profile-structure.md),
[`02`](./docs/rules/02-clinical-reference-usage.md), [`08`](./docs/rules/08-cross-validation.md).

**What it does NOT do:** does not expose raw psychiatric labels in published content (show-don't-tell, Rule 02);
crisis verdicts are never cached (always re-assessed); writes only `docs/profiles/`, `docs/references/`, `docs/graph/`.

### `CRE` — Content (output) · 9 skills

**What it does:** translates the refreshed profile into platform-native content under `assets/`, gated per-claim
by evidence tier (T1–T5) and per-asset by confidentiality + voice consistency before publish.

**Deep links:** `cre:post-writer` · `cre:multiplatform` (1→N native variants) · `cre:evidence-scanner` ·
`cre:privacy-guard` · `cre:voice-audit` · rules [`03`](./docs/rules/03-content-creation-pipeline.md),
[`09`](./docs/rules/09-confidentiality-protocol.md), [`14`](./docs/rules/14-cre-evidence-and-events.md).

**What it does NOT do:** does not publish content that fails the evidence/privacy gates; does not edit profiles
or materials; writes only `assets/`.

### `GRO` — Growth · 8 skills

**What it does:** career-trajectory, competency (Dreyfus), learning-profile (Kolb), and mentoring (Kram)
intelligence feeding PSY + CRE. Forecasts are explicitly labelled `[FORECAST — NOT FACTUAL]`.

**Deep links:** `gro:career-path` · `gro:competency-map` · `gro:validate` · `gro:milestone-tracker` ·
rule [`15-gro-framework`](./docs/rules/15-gro-framework.md).

**What it does NOT do:** does not do clinical analysis (the GRO↔PSY boundary, Rule 15); writes only `docs/profiles/*/growth/`.

### `ORC` — Orchestration · 17 skills

**What it does:** routes events across domains, resolves cascades, audits cross-domain consistency, and owns
session state, memory, decisions, and the knowledge graph.

**Deep links:** `orc:bootstrap` · `orc:intake` · `orc:audit` · `orc:cascade` · `orc:council` · `orc:graph` ·
rules [`12-orc-orchestration`](./docs/rules/12-orc-orchestration.md), [`13-orc-workflow`](./docs/rules/13-orc-workflow.md).

**What it does NOT do:** does not own content — it routes and audits; writes only `.claude/`.

### `COM` — Common · 4 skills

**What it does:** shared toolkit — git operations, session-health monitoring, rules management, and skill/script
observability (11 read-only lenses).

**Deep links:** `com:git` · `com:health-check` · `com:rules` · `com:skill-analytics`.

**What it does NOT do:** does not edit domain content; utility only.

---

## How to run

The project is self-contained — all skills/scripts/rules/schemas live under `.claude/`, run with the
project-local virtualenv:

```bash
.claude/skills/.venv/bin/python3 .claude/skills/{framework}-{skill}/scripts/{script}.py [args]
```

First run: `bash .claude/scripts/install.sh` provisions the venv from `.claude/scripts/requirements.txt`
(pyyaml + jsonschema + pytest).

**Tests + gates** (also run in CI — `.github/workflows/`):

```bash
.claude/skills/.venv/bin/python3 -m pytest tests/ -q          # full suite
.claude/skills/.venv/bin/python3 -m pytest tests/ -m bug_class # closed-bug-class invariants
.claude/skills/.venv/bin/python3 eval/run_evals.py            # golden deterministic-skill evals
.claude/skills/.venv/bin/python3 e2e/run-full-pipeline.py     # synthetic-fixture pipeline run
```

---

## Bilingual

Every skill ships `GUIDE-EN.md` + `GUIDE-VI.md`. Skill IDs, flag names, frontmatter keys, and event names stay
English; prose + examples localize. Vietnamese is native-quality with full diacritics. The clinical corpus
(profiles, materials) is authored in Vietnamese.

---

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `ModuleNotFoundError: yaml / jsonschema / pytest` | venv not provisioned | `bash .claude/scripts/install.sh` |
| A script "scans nothing" for a character | passing an alias the resolver doesn't know | use a known slug/alias; tooling resolves via `paths.resolve_character()` |
| `pytest` collection error after a refactor | a test imports a removed module | the `bug_class` gate catches this — run `pytest -m bug_class` |
| Verdict cache feels stale | content unchanged ⇒ cache hit by design | pass `--fresh` to force a re-judge (crisis/twist are never cached) |
| Skill count mismatch warning | `CLAUDE.md` catalog out of sync | the `bug_class` gate asserts count == catalog |

---

## Privacy

This is clinical-grade data. Confidentiality is enforced by [Rule 09](./docs/rules/09-confidentiality-protocol.md):
privacy tags gate what reaches published content; `cre:privacy-guard` + `cre:evidence-scanner` scan before publish.
Committed caches store **verdict labels only — never raw profile text**. The distribution pack
(`tools/pack/`) drops the live character corpus, telemetry, runtime caches, and secrets. The synthetic e2e
fixture under `e2e/` contains **no real PII**.

---

## Documentation

| Topic | File |
| --- | --- |
| LLM context (start here) | [`CLAUDE.md`](./CLAUDE.md) |
| Domain rules (16) | [`docs/rules/`](./docs/rules/) |
| Shared operating guides + GATEs | [`.claude/skills/_framework-shared/references/`](./.claude/skills/_framework-shared/references/) |
| Knowledge architecture / module map | [`docs/knowledge-architecture.md`](./docs/knowledge-architecture.md) · [`docs/MODULES.md`](./docs/MODULES.md) |
| Clinical theory library | [`docs/references/INDEX.md`](./docs/references/INDEX.md) |
| Applied-pattern ledger | [`STANDARDIZE.md`](./STANDARDIZE.md) |

---

# Tiếng Việt

Hệ thống tình báo hồ sơ nhân vật cấp lâm sàng — biến hồ sơ tâm lý sâu, có bằng chứng, thành nội dung
gốc cho từng nền tảng. Thiết kế để **mở rộng từ vài nhân vật đến rất nhiều**.

## Hệ thống làm gì

1. **Thu nhận** tư liệu nguồn (bản ghi, phỏng vấn, bài báo) và chấm điểm chất lượng bằng chứng.
2. **Phân tích** thành hồ sơ lâm sàng có cấu trúc — case formulation, cơ chế phòng vệ, gắn bó, sang chấn, sức mạnh, dòng thời gian, phát triển.
3. **Tạo** nội dung nền tảng (Facebook, LinkedIn, blog…), kiểm soát theo bậc bằng chứng + bảo mật.

Tất cả theo sự kiện: thêm tư liệu → làm mới hồ sơ → hiệu chỉnh nội dung.

## Sáu framework

- **MAT — Tư liệu (4):** thu nhận + phân loại nguồn (bậc T1–T5, CRAAP); tư liệu phải *tích hợp* trước khi PSY phân tích.
- **PSY — Tâm lý (16):** dựng + làm mới formulation 5P, chẩn đoán, sang chấn, dòng thời gian, kiểm tra nhất quán 10 chiều. Không lộ thuật ngữ lâm sàng thô ra nội dung (Rule 02).
- **CRE — Nội dung (9):** chuyển hồ sơ thành nội dung gốc nền tảng, kiểm soát theo bậc bằng chứng + bảo mật trước khi đăng.
- **GRO — Phát triển (8):** sự nghiệp, năng lực (Dreyfus), học tập (Kolb), cố vấn (Kram). Dự báo gắn nhãn `[FORECAST — NOT FACTUAL]`.
- **ORC — Điều phối (17):** định tuyến sự kiện, giải cascade, kiểm toán nhất quán, sở hữu session/memory/đồ thị tri thức.
- **COM — Chung (4):** git, giám sát sức khỏe phiên, quản lý quy tắc, quan trắc skill/script.

Mỗi skill có `GUIDE-VI.md` — hướng dẫn tiếng Việt theo từng use case.

## Cách chạy

```bash
bash .claude/scripts/install.sh                                   # lần đầu: dựng venv
.claude/skills/.venv/bin/python3 -m pytest tests/ -q             # bộ test
.claude/skills/.venv/bin/python3 e2e/run-full-pipeline.py        # chạy pipeline trên fixture giả lập
```

## Quyền riêng tư

Dữ liệu cấp lâm sàng — bảo mật theo [Rule 09](./docs/rules/09-confidentiality-protocol.md). Cache đã commit
chỉ lưu **nhãn phán quyết, không bao giờ lưu văn bản hồ sơ thô**. Gói phân phối loại bỏ corpus nhân vật thật,
telemetry, cache runtime, và secrets. Fixture e2e hoàn toàn giả lập, không có PII thật.

## Cần trợ giúp

Bắt đầu từ [`CLAUDE.md`](./CLAUDE.md), các quy tắc trong [`docs/rules/`](./docs/rules/), và `GUIDE-VI.md`
của từng skill.
