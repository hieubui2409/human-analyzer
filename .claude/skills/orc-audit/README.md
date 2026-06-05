# orc:audit

> Audit cross-domain event consistency and declaration integrity.

## What it does

Scans all event declaration sources (SKILL.md tables, rules files, Python registries) and cross-checks for consistency. Reports missing events, orphan events, routing mismatches, undeclared emissions. Ensures event system is coherent. Read-only audit.

## When to use

- **After modifying event routing** — verify consistency
- **Before release** — ensure event declarations match implementation
- **Debugging event issues** — find routing conflicts or missing events
- Trigger phrases: "event audit", "consistency check", "domain audit"

## Flags

| Flag | Effect |
|------|--------|
| `--domain <domain>` | Filter to one domain or `all` (default) |
| `--json` | JSON output |
| `--fix-suggestions` | Include suggested edits to resolve issues |

## What it does NOT do

- Does NOT modify files—only reports.
- Does NOT execute fixes—recommends them.
- Does NOT enforce—advisory only, violations are informational.

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

### Nó làm gì

Quét tất cả các nguồn khai báo sự kiện (bảng SKILL.md, tệp quy tắc, đăng ký Python) và kiểm tra chéo tính nhất quán. Báo cáo các sự kiện bị thiếu, các sự kiện mồ côi, không khớp định tuyến, các phát hành không được khai báo. Đảm bảo hệ thống sự kiện là nhất quán. Kiểm tra chỉ đọc.

### Khi nào dùng

- **Sau khi sửa đổi định tuyến sự kiện** — xác minh tính nhất quán
- **Trước phát hành** — đảm bảo các khai báo sự kiện khớp với triển khai
- **Gỡ lỗi các vấn đề sự kiện** — tìm xung đột định tuyến hoặc các sự kiện bị thiếu
- Cụm từ kích hoạt: "event audit", "consistency check", "domain audit"

### Không làm gì

- **Không sửa đổi** tệp—chỉ báo cáo.
- **Không thực hiện** sửa chữa—khuyến nghị chúng.
- **Không thực thi**—chỉ cố vấn, các vi phạm chỉ mang tính thông tin.
