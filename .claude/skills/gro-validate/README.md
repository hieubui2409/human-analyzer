# gro:validate

> Cross-check growth data consistency across all 4 GRO profile files and identity/core.md.

## What it does

Validates frontmatter schema, cross-file consistency (career-path ↔ competencies cross-reference, mentoring-map relationship links), GRO↔PSY boundary (no PSY-domain terms in growth files), evidence grounding (presence of citations), and staleness warnings (default: 90 days). Outputs structured findings (pass/warn/fail per check) and optionally suggests LLM-powered fixes.

## When to use

- **Trigger phrases:** "gro validate", "growth validation", "growth consistency", "gro check"
- **Workflow position:** Pre-publish validation; runs after any GRO skill updates
- **Output user:** profile builders ensuring data quality before PSY/CRE consumption

## Flags

| Flag | Effect |
|------|--------|
| `--character <name>` | Validate one character only |
| `--all` | Validate all 3 characters (default) |
| `--json` | Machine-readable output |
| `--fix` | Include LLM fix suggestions |
| `--stale-days <N>` | Staleness threshold (default 90) |

## What it does NOT do

- **Not auto-fixing:** `--fix` suggests changes; does not apply them
- **Not fine-grained skill checks:** does not verify each skill exists in competencies.md (LLM judgment only)
- **Not prescriptive:** does not recommend data additions; only flags consistency issues

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

**Mục đích:** Xác thực frontmatter schema, tính nhất quán tệp chéo, biên giới GRO↔PSY, nền tảng bằng chứng, và cảnh báo cũ. Xuất kết quả có cấu trúc (pass/warn/fail trên mỗi kiểm tra). Tùy chọn gợi ý các bản sửa chữa.

**Khi nào dùng:** Xác thực trước khi xuất bản; chạy sau bất kỳ cập nhật kỹ năng GRO nào.

**Không làm được:** Không auto-fix. Không kiểm tra kỹ năng chi tiết. Không gợi ý dữ liệu.
