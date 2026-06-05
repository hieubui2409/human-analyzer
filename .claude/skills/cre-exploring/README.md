# cre:exploring

> Structured exploration before content planning — lock decisions via sequential questions, output CONTEXT.md for downstream writing.

## What it does

Guides you through 7 questions (character, content type, angle, platform, tone, clinical framing, constraints) one at a time. Each answer informs the next. Outputs a CONTEXT.md with all locked decisions, ready to feed `cre:post-writer --from-context` or `cre:prompt-leverage`.

## When to use

- Before planning any content piece (social post, blog, article, profile update)
- To refine a discovered angle (from `cre:angle-discovery`)
- To explore cross-character dynamics or profile updates
- When you want a structured decision trail before writing

## Flags

| Flag | Effect |
|------|--------|
| (topic) | Start exploration with given topic (optional) |
| `--resume` | Continue from last CONTEXT.md (same or fresh questions) |
| `--reset` | Discard current CONTEXT.md, start completely fresh |

## What it does NOT do

- **Not generative** — doesn't write content (that's `cre:post-writer`)
- **Not automatic** — requires your answers; one question per turn
- **Not a profile modifier** — reads profiles read-only, never writes to them
- **Not a planner** — explores content intent, doesn't create implementation plans
- **Not skippable** — all decisions must be locked; no shortcuts

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)
- Related: `cre:post-writer --from-context`, `cre:prompt-leverage`, `cre:angle-discovery`
- Rules: Rule 03 (content pipeline), Rule 09 (confidentiality)

---

## Tiếng Việt

**Công dụng:** Hướng dẫn bạn thông qua 7 câu hỏi (nhân vật, loại nội dung, góc nhìn, nền tảng, giọng điệu, khung lâm sàng, ràng buộc) từng cái một. Mỗi câu trả lời thông báo cho câu tiếp theo. Xuất ra CONTEXT.md với tất cả các quyết định bị khóa, sẵn sàng cung cấp cho `cre:post-writer --from-context` hoặc `cre:prompt-leverage`.

**Khi nào sử dụng:**
- Trước khi lên kế hoạch cho bất kỳ phần nội dung nào (bài đăng trên mạng xã hội, blog, bài viết, cập nhật hồ sơ)
- Để tinh chỉnh một góc nhìn được phát hiện (từ `cre:angle-discovery`)
- Để khám phá động lực xuyên nhân vật hoặc cập nhật hồ sơ
- Khi bạn muốn một dấu vết quyết định có cấu trúc trước khi viết

**Điều nó KHÔNG làm:**
- Không sinh ra — không viết nội dung
- Không tự động — yêu cầu câu trả lời của bạn; một câu hỏi mỗi lượt
- Không sửa đổi hồ sơ — đọc hồ sơ chỉ đọc, không bao giờ viết cho chúng
- Không lập kế hoạch — khám phá ý định nội dung, không tạo kế hoạch triển khai
