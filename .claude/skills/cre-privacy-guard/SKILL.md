---
name: cre:privacy-guard
description: "Scan assets/ and content drafts for leaked [PRIVATE], [CONFIDENTIAL], or restricted information before publishing. Use before publishing any social media content, after cre:post-writer completes, or as periodic audit. Triggers: 'privacy check', 'privacy scan', 'leak check', 'content safety', 'before publish', 'confidentiality audit'."
argument-hint: "[--scan|--file <path>|--audit|--strict]"
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

| Flag            | Purpose                                           |
| --------------- | ------------------------------------------------- |
| `--scan`        | Scan all assets/ for privacy violations (default) |
| `--file <path>` | Check specific file or directory                  |
| `--audit`       | Full audit with report generation                 |
| `--strict`      | Fail on ANY privacy tag found (zero tolerance)    |

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

### Location Detection

Check for protected location references:

- Specific addresses, school names, hospital names
- Exact GPS/map references
- Small town names that could identify characters

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
2. Also scan plans/reports/ for accidental `[PRIVATE]` content
3. Cross-reference with `docs/rules/09-confidentiality-protocol.md`
4. Generate report: `plans/reports/privacy-audit-{date}.md`

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

## Safety

- This skill is READ-ONLY for assets/ — it detects but does not auto-fix
- Fixes require human review (some clinical terms may be intentional in certain contexts)
- Scope: privacy violation detection. Does NOT handle content creation or profile management.

## See Also

psy:crisis-assess, cre:post-writer, cre:repurpose
