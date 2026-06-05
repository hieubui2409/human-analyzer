# orc:domain-router

> Route domain events to downstream skills based on git diff or explicit event.

## What it does

Detects domain changes from git diffs or accepts explicit events, then maps downstream skill recommendations. Reads from hardcoded EVENT_ROUTING table to show what should execute next across MAT, PSY, CRE, GRO, COM, ORC. Read-only orchestration utility—doesn't execute, only recommends.

## When to use

- **After git changes** — see what domains were touched and what should run next
- **Planning cascades** — understand event routing without executing
- **Debugging workflow** — trace what event triggered what skill chain
- Trigger phrases: "route events", "domain routing", "what should run next"

## Flags

| Flag | Effect |
|------|--------|
| `--event <EVENT>` | Route a specific named event (e.g., `MAT.integrated`) |
| `--from-diff` | Detect changed files via git diff |
| `--ref <REF>` | Git ref to diff against (default: HEAD~1) |
| `--json` | JSON output |
| `--dry-run` | Show routing without executing |

## What it does NOT do

- Does NOT execute skills—only recommends what should run.
- Does NOT modify files—read-only analysis.
- Does NOT change routing—rules are hardcoded, not configurable per-session.

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

### Nó làm gì

Phát hiện các thay đổi miền từ diffs git hoặc chấp nhận các sự kiện rõ ràng, sau đó lập bản đồ các khuyến nghị kỹ năng tầng dưới. Đọc từ bảng EVENT_ROUTING được mã hóa cứng để hiển thị những gì nên thực hiện tiếp theo trên MAT, PSY, CRE, GRO, COM, ORC. Công cụ điều phối chỉ đọc—không thực hiện, chỉ khuyến nghị.

### Khi nào dùng

- **Sau các thay đổi git** — xem những miền nào được chạm tới và những gì nên chạy tiếp theo
- **Lập kế hoạch tầng** — hiểu định tuyến sự kiện mà không thực hiện
- **Gỡ lỗi quy trình** — truy tìm sự kiện nào kích hoạt chuỗi kỹ năng nào
- Cụm từ kích hoạt: "route events", "domain routing", "what should run next"

### Không làm gì

- **Không thực hiện** kỹ năng—chỉ khuyến nghị những gì nên chạy.
- **Không sửa đổi** tệp—chỉ phân tích.
- **Không thay đổi** định tuyến—quy tắc được mã hóa cứng, không thể cấu hình cho mỗi phiên.
