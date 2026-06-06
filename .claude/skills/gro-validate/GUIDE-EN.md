# gro:validate — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You're building or maintaining GRO profile files and want to **catch data quality issues before downstream skills consume them.** Are all 4 required files present? Do cross-references check out (e.g., skills mentioned in career-path appear in competencies)? Are there stale files? PSY-domain term leaks? This skill runs deterministic checks and (optionally) suggests LLM-powered fixes. Useful for quality-assurance before publishing profiles or triggering downstream events.

## 2. Core concepts (the mental model)

**Script does deterministic checks; LLM judges heuristics.** The Python script verifies:

1. **Frontmatter schema:** All 4 files exist, have required fields (`domain: growth`, `type: data`, `character:` slug, `last_updated`, `updated_by`), and timestamps aren't stale (default: >90 days = warning).
2. **Cross-file consistency:** Keyword presence (do skills appear in multiple files? do mentors match relationship files?).
3. **GRO↔PSY boundary:** No defense mechanisms, attachment terms, trauma language in growth files (PSY-only).
4. **Evidence grounding:** Presence of citation markers ([Source:], [UNVERIFIED], [LIMITED DATA], [PRIVATE]).

**Fine-grained skill checks are heuristic.** The script flags "Python mentioned in career-path but not in competencies" as a WARN; the LLM judges if it's a real gap or acceptable (maybe Python is peripheral).

## 3. Learning path

**First run:** `gro:validate --character <name>` — see validation report. Scan for WARN/FAIL items. Most validation is quick; WARN items deserve review.

**Next:** `gro:validate --all --json` — programmatic output for CI/CD pipelines or downstream processing.

**Deepen:** `gro:validate --fix` — include LLM-suggested fixes for failures. Review suggestions before applying manually.

**As you grow:** Run validation before emitting GRO.assessed events (career-path) or GRO.mentored events (mentoring-track) — ensures downstream PSY/CRE consumption is reliable.

## 4. Use cases (each = a sample conversation)

### Use case: Quality-check before publishing a profile

> **You:** "gro:validate --character character-a --fix"
>
> **Skill:** Runs checks. Finds: Frontmatter OK. Cross-file: 2 skills in career-path missing from competencies. Evidence: 3 entries lack [Source:] markers. GRO↔PSY: No boundary violations.
>
> **Findings:** WARN on skill gap, WARN on evidence grounding. LLM suggests: (1) add missing skills to competencies.md or remove from career-path if peripheral, (2) add [Source: materials/hieu/XXX.md] to unsourced entries.
>
> **Use:** You now know what to fix before the profile is consumed by downstream skills.

### Use case: Bulk validation before event emission

> **You:** "gro:validate --all --json | jq '.characters[] | select(.score < 80)'"
>
> **Skill:** Returns characters with validation scores below 80/100. Flags which ones are ready vs need review.
>
> **Use:** Before emitting GRO.assessed event from career-path, check that all characters pass validation. Prevents cascading downstream errors.

## 5. Important caveats

- **Deterministic checks are strict; heuristic checks are lenient.** Frontmatter schema must match exactly (FAIL if mismatch). Skill cross-reference uses keyword matching (WARN if not found, but might be acceptable).
- **Staleness is configurable.** Default is 90 days; you can set `--stale-days 180` for longer tolerance (e.g., if profiles are updated quarterly, not monthly).
- **LLM fixes are suggestions only.** The `--fix` flag outputs proposals; they must be reviewed and applied manually. Never auto-apply fixes in production.
- **Evidence markers are coarse.** The script checks presence ([Source:] exists); it doesn't validate link correctness or evidence quality. Manual review still needed.
- **Boundary (Rule 15):** This skill enforces GRO↔PSY boundary by scanning for PSY-domain terms in growth files. If you find a violation, fix it immediately — it signals a cross-domain write.
