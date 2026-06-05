# cre:privacy-guard

> Scan content for privacy violations — leaked names, clinical terms, DSM/ICD codes, PII. Enforce Rule 09 (confidentiality protocol) before publishing. READ-ONLY audit tool; detects but does not auto-fix.

## What it does

Scans `assets/` and (optionally) framework directories for privacy tag leaks (`[PRIVATE]`, `[CONFIDENTIAL: {person}]`), restricted names, raw clinical terms, and diagnostic codes. Generates violation report with line/severity. Runs `--strict` for zero-tolerance (any tag = FAIL). Appends audit JSONL for governance queries.

## When to use

- Mandatory before publishing (called by `cre:post-writer` quality phase)
- Periodic governance audit (`--audit`, generates report)
- Cross-framework check (`--cross-framework`) after materials ingestion
- Pre-repurpose validation (`--file` on source post)

## Flags

| Flag | Effect |
|------|--------|
| `--scan` | Scan all `assets/` for violations (default) |
| `--file <path>` | Scan specific file or directory |
| `--audit` | Full audit: all assets + framework dirs + report generation |
| `--strict` | Zero tolerance — ANY privacy tag = FAIL |
| `--cross-framework` | Extend scan to `docs/profiles/`, `docs/materials/`, `docs/graph/` |

## What it does NOT do

- **Not auto-fixing** — detects violations; author must review and fix
- **Not a content modifier** — READ-ONLY, never writes to profiles or posts
- **Not context-aware** — detects raw terms; implicit clinical language requires human judgment (Layer 2 LLM heuristic optional)
- **Not a substitute for human review** — complex privacy edge cases need judgment
- **Not a whitelist tool** — doesn't allow exceptions; CRITICAL violations always fail

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)
- Related: `cre:post-writer`, `cre:evidence-scanner`, `cre:multiplatform`, `cre:repurpose`
- Rules: Rule 09 (confidentiality), Rule 02 (clinical reference show-don't-tell)

---

## Tiếng Việt

**Công dụng:** Quét nội dung tìm kiếm vi phạm quyền riêng tư — tên rò rỉ, thuật ngữ lâm sàn, mã DSM/ICD, PII. Thực thi Quy tắc 09 (giao thức bảo mật) trước khi công bố. Công cụ kiểm toán CHỈ ĐỌC; phát hiện nhưng không tự động sửa chữa.

**Khi nào sử dụng:**
- Bắt buộc trước khi công bố (được gọi bởi giai đoạn chất lượng `cre:post-writer`)
- Kiểm toán quản lý định kỳ (`--audit`, tạo báo cáo)
- Kiểm tra xuyên khuôn khổ (`--cross-framework`) sau khi tiếp nhận tài liệu
- Xác nhận trước khi sử dụng lại (`--file` trên bài đăng nguồn)

**Điều nó KHÔNG làm:**
- Không tự động sửa chữa — phát hiện vi phạm; tác giả phải xem xét và sửa chữa
- Không sửa đổi nội dung — CHỈ ĐỌC, không bao giờ viết sang hồ sơ hoặc bài đăng
- Không có nhận thức bối cảnh — phát hiện các thuật ngữ thô; ngôn ngữ lâm sàn ẩn yêu cầu xét xử con người
