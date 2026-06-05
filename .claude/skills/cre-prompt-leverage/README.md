# cre:prompt-leverage

> Strengthen content briefs into execution-ready prompts — layer in character voice, clinical accuracy, platform constraints, profile facts, and sensitivity checks. Reads CONTEXT.md or raw prompt text.

## What it does

Takes a vague content brief or CONTEXT.md from `cre:exploring`. Applies 5 layers: voice lock (character's linguistic patterns), clinical guards (theory + accuracy), platform formatting (length/structure), profile cross-reference (facts/relationships), sensitivity scan (trauma/names/clinical). Outputs strengthened execution prompt + pre-read file list. Guides `cre:post-writer` internally; also runnable standalone.

## When to use

- Before writing any content (called auto by `cre:post-writer`)
- Standalone: strengthen a raw brief before delegating to writer
- Batch prep: strengthen 10 briefs, then write 10 posts
- Prompt engineering: explore how layers affect content quality

## Flags

| Flag | Effect |
|------|--------|
| (prompt text) | Strengthen this raw prompt directly |
| `--from-context` | Read CONTEXT.md from exploration (default if no text) |
| `--platform <name>` | Emphasize platform-specific constraints |

## What it does NOT do

- **Not generative** — doesn't write content (output is a prompt for post-writer)
- **Not deterministic** — strengthened prompts are better, but LLM quality depends on other factors
- **Not a validator** — doesn't check if strengthened prompt is "correct," just more complete
- **Not a modifier** — reads profiles read-only, never edits them
- **Not a rewrite tool** — output is a prompt, not final content

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)
- Related: `cre:exploring`, `cre:post-writer` (uses internally), `cre:multiplatform`
- Rules: Rule 03 (content pipeline), Rule 09 (confidentiality)

---

## Tiếng Việt

**Công dụng:** Lấy một bài tóm tắt nội dung mơ hồ hoặc CONTEXT.md từ `cre:exploring`. Áp dụng 5 lớp: khóa giọng (mô hình ngôn ngữ của nhân vật), bảo vệ lâm sàn, định dạng nền tảng, tham chiếu chéo hồ sơ, quét nhạy cảm. Xuất ra prompt thực thi được tăng cường + danh sách tệp trước khi đọc.

**Khi nào sử dụng:**
- Trước khi viết bất kỳ nội dung nào (được gọi tự động bởi `cre:post-writer`)
- Độc lập: tăng cường bài tóm tắt thô trước khi ủy quyền cho người viết
- Chuẩn bị hàng loạt: tăng cường 10 bài tóm tắt, sau đó viết 10 bài
- Kỹ thuật prompt: khám phá cách các lớp ảnh hưởng đến chất lượng nội dung

**Điều nó KHÔNG làm:**
- Không sinh ra — không viết nội dung
- Không xác định — prompt được tăng cường tốt hơn, nhưng chất lượng LLM phụ thuộc vào các yếu tố khác
- Không phải bộ xác nhận — không kiểm tra xem prompt được tăng cường có "chính xác" không
- Không sửa đổi — đọc hồ sơ chỉ đọc, không bao giờ chỉnh sửa chúng
