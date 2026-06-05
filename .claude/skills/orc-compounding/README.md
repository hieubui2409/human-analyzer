# orc:compounding

> Extract durable learnings after content or profile work.

## What it does

Analyzes recent work (git diffs, session state) to extract lasting insights about character psychology, writing patterns, audience resonance, clinical accuracy, growth development, and process improvements. Writes learnings to project memory and instinct store for future sessions to benefit from.

## When to use

- **After completing content creation** — extract what worked in writing
- **After profile updates** — capture new psychology insights
- **After arc development** — record character growth patterns
- **Session end** — consolidate learnings before archiving
- Trigger phrases: "compound", "extract learnings", "what did we learn", "capture insights"

## Flags

| Flag | Effect |
|------|--------|
| (none) | `--session` mode: extract from current session (default) |
| `--session` | Extract from current session work |
| `--auto` | Auto-extract + write to memory, no confirmation |
| `--character <name>` | Extract character-specific insights only |
| `--content` | Extract content creation patterns from recent assets |
| `--instincts-only` | Extract instincts without writing to memory |

## What it does NOT do

- Does NOT modify profile or content files—only reads from them.
- Does NOT delete or prune memories—only appends new ones.
- Does NOT execute domain skills—it only extracts learnings.

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

### Nó làm gì

Phân tích công việc gần đây (diffs git, trạng thái phiên) để trích xuất các kiến thức bền vững về tâm lý nhân vật, mẫu viết, cộng hưởng khán giả, độ chính xác lâm sàng, phát triển tăng trưởng, và cải tiến quy trình. Ghi learnings vào bộ nhớ dự án và kho bản năng để các phiên tương lai được hưởng lợi.

### Khi nào dùng

- **Sau hoàn thành tạo nội dung** — trích xuất những gì hoạt động trong viết
- **Sau cập nhật hồ sơ** — ghi lại các kiến thức tâm lý mới
- **Sau phát triển cung** — ghi lại các mẫu phát triển nhân vật
- **Kết thúc phiên** — hợp nhất learnings trước khi lưu trữ
- Cụm từ kích hoạt: "compound", "extract learnings", "what did we learn", "capture insights"

### Không làm gì

- **Không sửa đổi** tệp hồ sơ hoặc nội dung—chỉ đọc từ chúng.
- **Không xóa** hoặc cắt tỉa memories—chỉ ghi lại những cái mới.
- **Không thực hiện** các kỹ năng miền—nó chỉ trích xuất learnings.
