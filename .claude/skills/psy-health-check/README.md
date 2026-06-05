# psy:health-check

> Profile completeness scoring — audit all 25 expected files per character and aggregate health score (0-100).

## What it does

Checks all 25 expected profile files per character, scores each file 0-100 (missing=0, empty=10, thin=40, adequate=70, complete=90, +10 if proper sections). Aggregates per-category and overall score. Surfaces gaps and priorities for filling them.

## When to use

- Before cross-character validation: "Are profiles complete enough?"
- When onboarding new character: "What files are missing?"
- Periodic health check: "Which categories need attention?"
- Trigger phrases: profile health, completeness check, what is missing, profile gaps, health score

## Flags

| Flag                 | Effect |
|----------------------|--------|
| `--character <name>` | Score one character only |
| `--all`              | Score all characters (default) |
| `--gaps-only`        | Show only files with score < 80 |
| `--json`             | Output as JSON |

## What it does NOT do

- Does NOT modify profiles (read-only audit only)
- Does NOT judge quality of content (only size/completeness)
- Does NOT validate consistency (that's psy:crossref)
- Does NOT check against Draft-7 schema (that's validate-all-against-schemas.py)

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

**Chấm điểm tính hoàn chỉnh của hồ sơ** — kiểm tra tất cả 25 tệp dự kiến trên mỗi nhân vật và tính tổng điểm sức khỏe.

**Khi nào sử dụng:** Trước khi xác thực qua các nhân vật, khi nhập hành nhân vật mới, hoặc kiểm tra sức khỏe định kỳ.
