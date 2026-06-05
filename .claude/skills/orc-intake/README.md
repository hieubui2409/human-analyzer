# orc:intake

> Classify work type and route to optimal skill chain.

## What it does

Analyzes incoming task descriptions to determine work type (content creation, profile update, arc development, research, material ingestion, consistency audit, reference management, maintenance, multi-platform, growth analysis). Outputs recommended skill chain for that work type. Use at start of any new task before planning or implementation.

## When to use

- **New task arrives** — determine what kind of work it is
- **Unclear workflow** — get routing recommendations
- **Planning skill sequence** — see what should run in what order
- Trigger phrases: "intake", "new task", "what should I do", "route this"

## Flags

| Flag | Effect |
|------|--------|
| (positional) | Task description text |
| `--auto` | Auto-classify from git diff + branch, skip user prompt |

## What it does NOT do

- Does NOT execute the recommended skills—only suggests the sequence.
- Does NOT modify files—read-only classification.
- Does NOT enforce order—you decide which skills to actually run.

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

### Nó làm gì

Phân tích các mô tả nhiệm vụ đến để xác định loại công việc (tạo nội dung, cập nhật hồ sơ, phát triển cung, nghiên cứu, nạp vào tài liệu, kiểm tra tính nhất quán, quản lý tham chiếu, bảo trì, đa nền tảng, phân tích tăng trưởng). Xuất ra chuỗi kỹ năng được khuyến nghị cho loại công việc đó. Sử dụng ở đầu bất kỳ nhiệm vụ mới nào trước khi lập kế hoạch hoặc triển khai.

### Khi nào dùng

- **Nhiệm vụ mới đến** — xác định loại công việc nó
- **Quy trình không rõ** — nhận được khuyến nghị định tuyến
- **Lập kế hoạch chuỗi kỹ năng** — xem những gì nên chạy theo thứ tự nào
- Cụm từ kích hoạt: "intake", "new task", "what should I do", "route this"

### Không làm gì

- **Không thực hiện** các kỹ năng được khuyến nghị—chỉ gợi ý chuỗi.
- **Không sửa đổi** tệp—chỉ phân loại.
- **Không thực thi** thứ tự—bạn quyết định những kỹ năng nào thực sự chạy.
