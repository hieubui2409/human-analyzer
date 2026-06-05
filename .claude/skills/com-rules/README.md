# com:rules

> Validate changed files against project rules (docs/rules/*.md). Routes validation to specialized skills.

## What it does

Scans uncommitted or specified files, classifies them by domain (profiles, materials, assets, etc.), then routes each to the appropriate rule validator. Reports violations with actionable recommendations. Read-only; never auto-fixes.

## When to use

- User says "check rules", "validate", "rule compliance"
- After making changes, before committing
- Typical position: between implementation and `com:git`

## Flags

| Flag              | Effect                                          |
| ----------------- | ----------------------------------------------- |
| `--validate`      | Validate uncommitted changes (default)          |
| `--list`          | List all 16 rules with status                   |
| `--check <rule#>` | Validate against specific rule (e.g., `--check 01`) |
| `--scope`         | uncommitted / all / path                        |

## What it does NOT do

- **Does not auto-fix violations** — reports only; you fix manually
- **Does not run against .git or IDE configs** — scopes to docs/, assets/, plans/
- **Does not interpret business logic** — checks schema/frontmatter, not semantic correctness
- **Does not skip delegated validators** — if rule 02 (references) applies, it calls `psy:ref-audit` (requires active skill context)
- **Does not validate rules 06, 13** — those are process rules, not file rules

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

Quét các tệp chưa được commit hoặc được chỉ định, phân loại chúng theo miền (hồ sơ, tài liệu, tài sản, v.v.), sau đó định tuyến mỗi tệp đến trình xác thực quy tắc thích hợp. Báo cáo các vi phạm với những khuyến nghị có thể hành động. Chỉ đọc; không bao giờ tự động sửa chữa.

**Khi sử dụng:** người dùng nói "check rules", "validate", "rule compliance" — thường giữa việc triển khai và `com:git`.

**Không làm gì:**
- Không tự động sửa các vi phạm
- Không chạy trên các tệp .git hoặc IDE
- Không diễn giải logic kinh doanh
- Không bỏ qua các trình xác thực được ủy quyền
- Không xác thực quy tắc xử lý (06, 13)
