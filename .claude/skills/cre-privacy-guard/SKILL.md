---
name: cre:privacy-guard
description: "Scan assets/ and cross-framework dirs for leaked PII, privacy tags, clinical terms, DSM/ICD codes. Use before publishing, after cre:post-writer, or as periodic governance audit. Triggers: 'privacy check', 'privacy scan', 'leak check', 'content safety', 'before publish', 'confidentiality audit', 'governance audit'."
argument-hint: "[--scan|--file <path>|--audit|--strict|--cross-framework]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "safety"
  position: "pre-publish"
  dependencies: []
---

# Privacy Guard

Enforce `docs/rules/09-confidentiality-protocol.md` — prevent private/confidential content from leaking into published assets.

## Flags

| Flag                | Purpose                                                       |
| ------------------- | ------------------------------------------------------------- |
| `--scan`            | Scan all assets/ for privacy violations (default)             |
| `--file <path>`     | Check specific file or directory                              |
| `--audit`           | Full audit with report generation + JSONL logging             |
| `--strict`          | Fail on ANY privacy tag found (zero tolerance)                |
| `--cross-framework` | Scan assets/ + docs/profiles/ + docs/materials/ + docs/graph/ |

## Scan Targets

### Tag Detection

Grep assets/ for these patterns:

| Pattern                    | Severity | Action                           |
| -------------------------- | -------- | -------------------------------- |
| `[PRIVATE]`                | CRITICAL | Must remove before publish       |
| `[CONFIDENTIAL: {person}]` | CRITICAL | Must remove/anonymize            |
| `[ANONYMIZE]`              | WARNING  | Verify pseudonym applied         |
| `[UNCERTAIN]`              | INFO     | OK in drafts, review for publish |
| `[DISPUTED]`               | INFO     | OK in drafts, verify resolution  |

### Name Detection

Check for restricted names in assets/:

1. Load all `[CONFIDENTIAL: {person}]` tags from profiles (scan `docs/profiles/*/identity/core.md`, `docs/profiles/*/relationships/family.md`, cross-character files via `list_relationship_files()`, `docs/profiles/*/darkness/traumas.md`)
2. Extract person names
3. Grep assets/ for those names
4. Flag any matches as CRITICAL violations

### Clinical Term Detection

Check for raw clinical terms in assets/ (two layers):

**Layer 1 — Explicit terms (script-gathered):**

1. Load clinical→colloquial mapping from `docs/rules/02-clinical-reference-usage.md`
2. Run clinical term patterns against assets/ post files (via `.claude/scripts/platform_lib/clinical_terms.py`)
3. Flag exact clinical term matches — suggest colloquial replacements

**Layer 2 — Implicit clinical leaks (LLM-heuristic):**

1. Read flagged post files in full context
2. Detect passages that DESCRIBE clinical concepts without using formal terms but still feel "too clinical" for social media audience
3. Examples: "cơ chế phòng vệ tâm lý" (defense mechanism phrasing), "mô hình gắn kết lo âu" (anxious attachment model)
4. Flag as MEDIUM severity — suggest more natural phrasing

**Layer 3 — DSM-5/ICD-11 code leak detection:**

1. Grep ALL framework dirs for diagnostic codes (F##.#, 6A##, etc.)
2. If found OUTSIDE `docs/profiles/*/psychology/` or `docs/references/`:
   - Flag as HIGH severity — diagnostic codes should not appear in content, materials descriptions, or relationship files
   - Exception: `docs/profiles/*/psychology/diagnostics.md` — codes expected there

### Location Detection

Check for protected location references:

- Specific addresses, school names, hospital names
- Exact GPS/map references
- Small town names that could identify characters

### Cross-Framework PII Detection (--audit or --cross-framework mode)

When running `--audit` or `--cross-framework`, extend scan beyond `assets/` to framework directories:

| Directory                        | What to Check                                    | Severity |
| -------------------------------- | ------------------------------------------------ | -------- |
| `docs/profiles/*/identity/`      | Un-tagged real names, phone, email, addresses    | CRITICAL |
| `docs/profiles/*/relationships/` | Third-party names without [CONFIDENTIAL] wrapper | CRITICAL |
| `docs/profiles/*/darkness/`      | Raw trauma details without privacy tags          | HIGH     |
| `docs/materials/`                | Source materials with un-redacted PII            | HIGH     |
| `docs/graph/`                    | Cross-character PII leaks                        | MEDIUM   |

**Exclusions (clinical terms expected):**

- `docs/profiles/*/psychology/` — clinical terms are legitimate here
- `docs/references/` — clinical reference library

### PII Regex Patterns

| Pattern          | Regex                     | Example        |
| ---------------- | ------------------------- | -------------- |
| Vietnamese phone | `0[35789]\d{8}`           | 0912345678     |
| Email            | `[\w.+-]+@[\w-]+\.[\w.]+` | name@email.com |
| Vietnamese CCCD  | `0\d{11}`                 | 012345678901   |

## Workflow

### --scan (Default)

1. Grep all `assets/*/post.md` and `assets/*/post.txt` for tag patterns
2. Grep for restricted names
3. Grep for clinical terms
4. Output violations table:

   ```
   ## Privacy Scan Results
   Files scanned: {N}
   Violations: {M}

   | File | Line | Type | Content | Severity |
   |------|------|------|---------|----------|
   | assets/facebook/260413-.../post.md | 15 | NAME | "Huyền" | CRITICAL |
   ```

5. If violations=0: "✅ Clean — safe to publish"
6. If violations>0: "❌ {M} violations found — fix before publishing"

### --file `<path>`

Same as --scan but limited to specific file/directory.

### --audit

Full audit with report:

1. Run --scan across all assets/
2. Run --cross-framework scan across `docs/profiles/`, `docs/materials/`, `docs/graph/`
3. Also scan plans/reports/ for accidental `[PRIVATE]` content
4. Cross-reference with `docs/rules/09-confidentiality-protocol.md`
5. Generate report: `plans/reports/privacy-audit-{date}.md`
6. Append audit summary to `.claude/telemetry/privacy-audit.jsonl`:
   ```json
   {"timestamp": "ISO", "scan_scope": ["..."], "files_scanned": N, "findings_count": N, "critical": N, "high": N, "medium": N, "low": N, "operator": "cre:privacy-guard"}
   ```
7. JSONL log is append-only. Each `--audit` run adds one line. Use `jq` to query history.

### --strict

Zero-tolerance mode for pre-publish:

- ANY tag match = FAIL
- ANY restricted name = FAIL
- ANY clinical term = FAIL
- Returns clear pass/fail for automation

## MAT Integration

When scanning content that references materials:

1. Check material `confidentiality` field in MAT frontmatter (public/internal/private/confidential)
2. If content cites a `private` or `confidential` material → CRITICAL violation
3. Cross-reference `privacy_flags` array in material frontmatter
4. Materials with evidence tier T1 (primary self-report) require extra scrutiny — may contain raw personal disclosures

## Integration Points

- Called by `cre:post-writer` in quality check phase
- Called by `cre:prompt-leverage` in sensitivity scan layer
- Can be wired as PostToolUse hook for assets/ writes
- Emits `CRE.privacy_cleared` when scan passes (consumed by ORC orchestration)
- Audit JSONL at `.claude/telemetry/privacy-audit.jsonl` queryable via `jq` for governance reporting

## Safety

- This skill is READ-ONLY for assets/ — it detects but does not auto-fix
- Fixes require human review (some clinical terms may be intentional in certain contexts)
- Scope: privacy violation detection. Does NOT handle content creation or profile management.

## See Also

psy:crisis-assess, cre:post-writer, cre:repurpose
