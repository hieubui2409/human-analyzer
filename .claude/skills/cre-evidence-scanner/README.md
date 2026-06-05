# cre:evidence-scanner

> Per-claim evidence-tier safety gate — extract atomic claims from content, map each to MAT evidence tiers (T1-T5), detect privacy leaks, adjudicate PASS/WARN/FAIL verdicts.

## What it does

Scans any `assets/{platform}/{slug}/` draft (or published post) for unsupported or weak claims. Extracts claims, gathers backing materials by evidence tier, detects Rule-09 privacy leaks, and judges each claim PASS (T1-T2), WARN (T3 or unmatched), or FAIL (T4-T5 or leak). Outputs per-claim verdicts; overall draft fails if any claim FAILs.

## When to use

- Mandatory before publishing (called by `cre:post-writer` Phase 6)
- Audit published assets (re-runnable gate)
- Validate variants in `cre:repurpose` or `cre:multiplatform` per-variant batch
- Pre-check in `orc:santa` dual-review workflow (CRE framework)

## Flags

| Flag | Effect |
|------|--------|
| `--asset <dir>` | Path to `assets/{platform}/{slug}/` directory |
| `--character <slug>` | (optional) Link claims to character profile; improves matching |
| `--json` | Output verdicts JSON (for automation) |
| `--strict` | Enforce T3→FAIL (stricter than default T3→WARN) |

## What it does NOT do

- **Not generative** — does not rewrite or fix content (that's on the author)
- **Not auto-learning** — tier mapping is static (`evidence_tier_permissions.py`), not learned
- **Not a substitute for clinical review** — detects explicit leaks; implicit meaning requires human judgment
- **Single source of truth** — all tier logic lives in one module, imported by post-writer (no duplication per Rule 04)
- **Not bypassed by `--strict`** — FAIL-CLOSED always; `--strict` only raises T3 to FAIL instead of WARN

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)
- Related: `cre:post-writer` (Phase 6 delegate), `cre:privacy-guard`, `cre:repurpose`, `cre:multiplatform`
- Rules: Rule 09 (confidentiality), Rule 02 (clinical reference), Rule 14 (CRE evidence)

---

## Tiếng Việt

**Công dụng:** Quét bất kỳ bản nháp `assets/{platform}/{slug}/` nào để tìm các yêu cầu không được hỗ trợ hoặc yếu. Trích xuất các yêu cầu, thu thập các tài liệu hỗ trợ theo cấp độ bằng chứng, phát hiện rò rỉ quyền riêng tư Quy tắc 09, và đánh giá từng yêu cầu PASS (T1-T2), CẢNH BÁO (T3 hoặc không khớp), hoặc THẤT BẠI (T4-T5 hoặc rò rỉ).

**Khi nào sử dụng:**
- Bắt buộc trước khi công bố (được gọi bởi `cre:post-writer` Giai đoạn 6)
- Kiểm toán các tài sản đã công bố (cổng có thể chạy lại)
- Xác nhận các biến thể trong `cre:repurpose` hoặc `cre:multiplatform`
- Kiểm tra trước trong quy trình đánh giá kép `orc:santa` (khuôn khổ CRE)

**Điều nó KHÔNG làm:**
- Không sinh ra — không viết lại hoặc sửa chữa nội dung
- Không tự động học — ánh xạ cấp độ là tĩnh, không được học
- Không phải thay thế cho đánh giá lâm sàng — phát hiện rò rỉ rõ ràng; ý nghĩa ẩn yêu cầu xét xử con người
