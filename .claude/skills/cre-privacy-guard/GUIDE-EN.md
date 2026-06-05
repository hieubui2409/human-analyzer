# cre:privacy-guard — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You've written a post about Nhân vật A's mentoring journey, but before you publish, you want to make sure you didn't accidentally leak someone's real name, a clinical diagnosis, or a confidential family detail. This skill scans your post for privacy tags (`[CONFIDENTIAL: Nhân vật B]`, `[PRIVATE]`), restricted names, raw clinical terms (DSM codes, ICD codes), and PII (phone numbers, emails). It outputs a clean violation report: what leaked, where, how severe. You fix, re-run, done.

## 2. Core concepts (the mental model)

**Four scanning layers:**

1. **Tag detection:** Grep for privacy markers (`[PRIVATE]`, `[CONFIDENTIAL: {person}]`, `[ANONYMIZE]`, `[UNCERTAIN]`, `[DISPUTED]`). Severity escalates from INFO to CRITICAL.

2. **Name detection:** Load all restricted names from profile metadata (identity/core.md, relationships/family.md, cross-character files, traumas.md). Grep assets for those names. Match = CRITICAL.

3. **Clinical term detection (Layer 1 — explicit):** Load clinical→colloquial mapping from Rule 02. Grep for raw DSM/ICD codes and formal clinical terms. Match = HIGH/MEDIUM per term.

4. **Clinical term detection (Layer 2 — implicit):** LLM reads flagged passages to detect implicit clinical language (not formal terms, but "too clinical for social media"). Suggest natural paraphrasing.

**Output:** Violation table (file, line, type, content, severity) + pass/fail verdict.

## 3. Learning path

**First run:** Scan all published posts:
```bash
.claude/skills/.venv/bin/python3 .claude/skills/cre-privacy-guard/scripts/scan-for-privacy-violations.py --scan
```
You see a table: 10 files scanned, 2 violations found. Line 15 in assets/facebook/260413-post.md: name "Huyền" (CRITICAL). Fix by redacting or removing that sentence.

**As you grow:** Try `--strict` for zero tolerance (any tag, even `[UNCERTAIN]`, = FAIL). Good for sensitive topics. Default mode allows `[UNCERTAIN]` in drafts.

**Standard flow:** Write post → `cre:post-writer` calls this auto → FAIL blocks; author fixes → re-run to confirm PASS.

## 4. Use cases (each = a sample conversation)

### Use case: Pre-publish scan

> **You:** "I wrote a LinkedIn post. Before publishing, check for leaks."
>
> **Skill:** `--file assets/linkedin/260526-post` → scans post.md + post.txt → "✅ Clean — safe to publish."
>
> **You:** Copy-paste post.txt to LinkedIn.

### Use case: Strict governance audit

> **You:** "Audit all published posts with zero tolerance."
>
> **Skill:** `--audit --strict` → scans all assets/ + framework dirs → generates `plans/reports/privacy-audit-{date}.md` + JSONL log.
>
> **You:** Review report, address HIGH/CRITICAL findings.

### Use case: Cross-framework check after material ingestion

> **You:** "Just ingested 5 new materials. Check if PII leaked into any docs."
>
> **Skill:** `--cross-framework` → scans assets/ + profiles/ + materials/ + graph/ → flags any unredacted PII.
>
> **You:** Redact materials, re-run.

### Use case: Clinical term leak detection

> **You:** "I'm worried I used clinical jargon in a TikTok post. Check it."
>
> **Skill:** `--file assets/tiktok/260526-post` → Layer 1 finds raw terms (DSM codes). Layer 2 LLM detects implicit clinical language.
>
> **You:** Replace clinical terms with colloquial paraphrasing from Rule 02 mapping.

## 5. Important caveats

- **CRITICAL always fails:** Tag leaks, restricted names, diagnostic codes outside psychology/ = non-negotiable FAIL.
- **MEDIUM/HIGH flagged, not auto-FAIL:** Clinical terms are detected; author decides context (some clinical terms OK in blog, not OK in TikTok).
- **Implicit clinical is heuristic:** Layer 2 LLM detection is advisory, not deterministic. Author has final say.
- **READ-ONLY audit:** This skill detects, never fixes. Author owns remediation.
- **Governance JSONL:** `--audit` appends to `.claude/telemetry/privacy-audit.jsonl`. Query with `jq` for compliance reporting.

## See also

- [`SKILL.md`](./SKILL.md) for technical contract
- `cre:post-writer` (calls this auto in quality phase)
- `cre:evidence-scanner` — complementary; this is PII/tags; scanner is evidence tier
- Rule 09 (confidentiality protocol), Rule 02 (clinical reference show-don't-tell)
