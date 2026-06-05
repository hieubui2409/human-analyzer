# cre:humanize

> De-AI-slop content so it reads like a human wrote it. Bilingual: English below, Tiếng Việt cuối file.

## What it does

Scans content for generic "AI tells" — filler phrases, formulaic openers/closers, forced
rule-of-three, em-dash overuse, hedging, mechanically-uniform sentences — in Vietnamese and
English. Input is a file or directory (default `assets/`); output is a per-file findings
report. An opt-in `--rewrite` hands the findings to the LLM, which rewrites `assets/` content
and re-runs the safety gates.

## When to use

- A draft feels AI-generated and you want the tells located.
- Before publishing — runs as the pre-publish de-slop gate, BEFORE `cre:voice-audit`.
- Auditing already-published `assets/`.
- Inside `cre:post-writer` (Phase 5) and `cre:multiplatform` (per-variant gate).

## Flags

| Flag                        | Effect                                                                 |
| --------------------------- | --------------------------------------------------------------------- |
| `--path <file\|dir>`        | Target to scan (default `assets/`).                                    |
| `--strictness <tier>`       | `high` \| `balanced` \| `conservative`; overrides the preference knob. |
| `--json`                    | Machine-readable output.                                               |
| `--rewrite`                 | Mark findings as an LLM rewrite worklist (assets/ only; refused on corpus). |
| `--character <slug>`        | Advisory label only — the scanner is character-agnostic.              |

## What it does NOT do

- Does NOT fit content to a character voice — that is `cre:voice-audit` (Rule 02/14).
- Does NOT check evidence tiers — that is `cre:evidence-scanner` (Rule 14).
- Does NOT scan PII/privacy — that is `cre:privacy-guard` (Rule 09).
- Does NOT rewrite `docs/profiles/` or `docs/materials/` — flag-only (Rule 09).

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)
- Taxonomy home: `.claude/scripts/platform_lib/humanizer_patterns.py`

---

## Tiếng Việt

### Kỹ năng này làm gì

Quét nội dung tìm các "dấu vết AI" chung — cụm từ thừa, mở/kết bài sáo rỗng, lạm dụng cấu
trúc bộ-ba, lạm dụng dấu gạch ngang dài, nói nước đôi, câu dài đều đều như máy — cho cả tiếng
Việt và tiếng Anh. Đầu vào là một file hoặc thư mục (mặc định `assets/`); đầu ra là báo cáo
phát hiện theo từng file. Cờ `--rewrite` (tùy chọn) chuyển danh sách phát hiện cho LLM viết
lại nội dung trong `assets/` rồi chạy lại các cổng an toàn.

### Khi nào dùng

- Một bản nháp "nghe có mùi AI" và bạn muốn định vị các dấu vết.
- Trước khi đăng — chạy như cổng làm-mềm, TRƯỚC `cre:voice-audit`.
- Rà soát nội dung đã đăng trong `assets/`.
- Bên trong `cre:post-writer` (Phase 5) và `cre:multiplatform` (cổng từng biến thể).

### KHÔNG làm gì

- KHÔNG khớp giọng nhân vật — đó là `cre:voice-audit` (Rule 02/14).
- KHÔNG kiểm tra bậc bằng chứng — đó là `cre:evidence-scanner` (Rule 14).
- KHÔNG quét PII/bảo mật — đó là `cre:privacy-guard` (Rule 09).
- KHÔNG viết lại `docs/profiles/` hay `docs/materials/` — chỉ gắn cờ (Rule 09).
