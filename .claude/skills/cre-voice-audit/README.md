# cre:voice-audit

> Audit published content for tone/voice consistency against character identity/writing-voice.md profiles. Detects tone drift, vocabulary mismatches, persona breaks. Uses re-runnable verdict cache (keyed on asset content) for efficiency.

## What it does

Scans published posts (`assets/`) for voice consistency. Reads character's `identity/writing-voice.md` (Voice Profile Structured section) + `psychology/archetype.md`. Analyzes each post for drift (tone break, vocabulary mismatch, persona break, clinical leak). Flags severity. Generates report or verdict-cache entry. Uses `--fresh` to force re-judge (ignores cache).

## When to use

- Periodic quality check across published content
- After batch content creation (verify consistency)
- When voice "feels off" compared to character profile
- Before repurposing (ensure source maintains voice integrity)
- Post-publish validation (called by `cre:post-writer` Phase 5)

## Flags

| Flag | Effect |
|------|--------|
| `--character <name>` | Audit posts written as/about this character |
| `--platform <platform>` | Audit specific platform only |
| `--file <path>` | Audit single post file |
| `--report` | Generate formal report to plans/reports/ |
| `--fresh` | Force re-judge (ignore verdict cache) |

## What it does NOT do

- **Not generative** — doesn't rewrite content, detects drift
- **Not auto-fixing** — flags issues; author decides action
- **Not deterministic** — voice analysis is LLM-heuristic, not script-based
- **Not a validator** — detects drift but doesn't judge "correct" voice (only consistency vs. profile)
- **Not a modifier** — READ-ONLY, never edits posts or profiles

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)
- Verdict cache: [`verdict-cache-contract.md`](../_framework-shared/references/verdict-cache-contract.md)
- Related: `cre:post-writer`, `cre:repurpose`, `cre:multiplatform`
- Rules: Rule 02 (clinical reference), Rule 03 (content pipeline)

---

## Tiếng Việt

**Công dụng:** Quét các bài đăng đã công bố để kiểm tra tính nhất quán về giọng điệu. Đọc `identity/writing-voice.md` + `psychology/archetype.md` của nhân vật. Phân tích từng bài để tìm kiếm drift (gãy giọng, không khớp từ vựng, gãy nhân vật). Gắn cờ mức độ. Tạo báo cáo hoặc mục nhập verdict-cache.

**Khi nào sử dụng:**
- Kiểm tra chất lượng định kỳ trên nội dung đã công bố
- Sau khi tạo nội dung hàng loạt (xác nhận tính nhất quán)
- Khi giọng điệu "cảm thấy bị tắt" so với hồ sơ nhân vật
- Trước khi sử dụng lại (đảm bảo rằng nguồn duy trì tính toàn vẹn giọng điệu)
- Xác nhận sau khi công bố (được gọi bởi `cre:post-writer` Giai đoạn 5)

**Điều nó KHÔNG làm:**
- Không sinh ra — không viết lại nội dung, phát hiện drift
- Không tự động sửa chữa — gắn cờ vấn đề; tác giả quyết định hành động
- Không xác định — phân tích giọng điệu là LLM-heuristic, không dựa trên kịch bản
- Không phải bộ xác nhận — phát hiện drift nhưng không đánh giá giọng điệu "chính xác"
- Không sửa đổi — CHỈ ĐỌC, không bao giờ chỉnh sửa bài hoặc hồ sơ
