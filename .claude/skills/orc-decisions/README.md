# orc:decisions

> Record and retrieve character arc decisions to prevent re-litigating settled choices.

## What it does

Stores decision records: why X was chosen over Y for character arcs, profile interpretations, content angles. Searchable log prevents rehashing old debates. Use when making character decisions, resolving interpretations, or checking past choices before committing to new ones.

## When to use

- **Before deciding on a major arc** — check if similar decisions exist
- **After resolving a debate** — record why you chose this direction
- **Periodic review** — audit decisions for consistency or conflicts
- **When refactoring** — ensure changes align with past decisions
- Trigger phrases: "decision", "record decision", "why did we choose", "check decision log"

## Flags

| Flag | Effect |
|------|--------|
| (none) | `--list` mode: show recent 20 decisions (default) |
| `--record` | Record a new decision (interactive) |
| `--search <query>` | Search decisions by keyword |
| `--list` | List recent decisions (default) |
| `--review` | Review decisions for a specific character |

## What it does NOT do

- Does NOT enforce decisions—records them for reference only.
- Does NOT modify files—read-only recording and retrieval.
- Does NOT auto-prune old decisions—all are kept for historical context.

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

### Nó làm gì

Lưu trữ hồ sơ quyết định: tại sao X được chọn hơn Y cho cung nhân vật, cách giải thích hồ sơ, các góc nội dung. Nhật ký có thể tìm kiếm ngăn chặn sơ vấn lại các cuộc tranh luận cũ. Dùng khi đưa ra quyết định nhân vật, giải quyết cách giải thích, hoặc kiểm tra các lựa chọn quá khứ trước khi cam kết với những lựa chọn mới.

### Khi nào dùng

- **Trước khi quyết định về một cung chính** — kiểm tra xem quyết định tương tự có tồn tại không
- **Sau khi giải quyết một cuộc tranh luận** — ghi lại tại sao bạn chọn hướng này
- **Kiểm tra định kỳ** — kiểm toán quyết định để tìm sự nhất quán hoặc xung đột
- **Khi tái cấu trúc** — đảm bảo các thay đổi phù hợp với các quyết định quá khứ
- Cụm từ kích hoạt: "decision", "record decision", "why did we choose", "check decision log"

### Không làm gì

- **Không thực thi** quyết định—chỉ ghi lại để tham khảo.
- **Không sửa đổi** tệp—chỉ ghi lại và truy xuất.
- **Không tự động xóa** các quyết định cũ—tất cả đều được lưu để có bối cảnh lịch sử.
