# psy:ref-maintain

> Reference library health audit — find orphaned theories (zero citations), coverage gaps, schema compliance issues.

## What it does

Audits `docs/references/` for all 62+ theories. Counts citations across profiles for each theory. Flags zero-citation orphans, missing INDEX.md entries, schema compliance breaches. Checks if all 3 characters have coverage in key categories (defense mechanisms, attachment, trauma, personality). Outputs health report with actionable recommendations.

## When to use

- Periodic library maintenance: "Is our reference library healthy?"
- Pre-validation: "Do we have sufficient theory coverage before psy:crossref?"
- Cleanup: "Which orphaned theories should we archive?"
- Trigger phrases: clean references, unused theories, reference maintenance, orphan theories, reference audit

## Flags

| Flag             | Effect |
|------------------|--------|
| `--orphans-only` | Show only theories with zero citations |
| `--gaps-only`    | Show only character gaps in coverage |
| `--json`         | Output as JSON |

## What it does NOT do

- Does NOT delete orphaned theories (read-only; user decides archival)
- Does NOT validate clinical accuracy (that's psy:ref-audit)
- Does NOT modify profiles or references (audit only)
- Does NOT auto-fix schema breaches (alerts; human review required)

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)
- Rule 10: [`docs/rules/10-reference-library-standard.md`](../../rules/10-reference-library-standard.md)

---

## Tiếng Việt

**Kiểm tra sức khỏe thư viện tài liệu tham khảo** — tìm các lý thuyết mồ côi (không có trích dẫn), khoảng trống phạm vi, vấn đề tuân thủ lược đồ.

**Khi nào sử dụng:** Bảo trì thư viện định kỳ, trước khi xác thực, hoặc dọn dẹp các lý thuyết mồ côi.
