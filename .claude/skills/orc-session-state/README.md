# orc:session-state

> Track session state across conversations for context persistence.

## What it does

Manages persistent session state in `.claude/session-state/state.json`: mode, phase, profiles touched, content created, decisions made, harness changes, pending events. Use to view current state, archive sessions, reset if corrupted, or write compact digests before context windows compress.

## When to use

- **Session start** — check state from last session
- **Session end** — archive state before stopping
- **Debugging** — see what's in current state
- **Context persistence** — write compact digest before `/compact`
- Trigger phrases: "session state", "what did we do", "session recap", "archive session"

## Flags

| Flag | Effect |
|------|--------|
| (none) | `--show` mode: print current state (default) |
| `--show` | Print current session state |
| `--archive` | Archive current state to timestamped markdown |
| `--reset` | Reset state to defaults (keep archive) |
| `--compact-digest` | Write bounded per-framework delta before `/compact` |

## What it does NOT do

- Does NOT modify profiles or content—only tracks metadata.
- Does NOT auto-archive—only on explicit `--archive`.
- Does NOT delete archives—only appends to session history.

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

### Nó làm gì

Quản lý trạng thái phiên liên tục trong `.claude/session-state/state.json`: chế độ, giai đoạn, hồ sơ được chạm tới, nội dung được tạo, quyết định được thực hiện, thay đổi harness, các sự kiện đang chờ. Dùng để xem trạng thái hiện tại, lưu trữ phiên, đặt lại nếu bị hỏng, hoặc ghi các tóm tắt nhỏ gọn trước khi các cửa sổ ngữ cảnh nén.

### Khi nào dùng

- **Bắt đầu phiên** — kiểm tra trạng thái từ phiên cuối cùng
- **Kết thúc phiên** — lưu trữ trạng thái trước khi dừng
- **Gỡ lỗi** — xem những gì trong trạng thái hiện tại
- **Sự liên tục ngữ cảnh** — ghi tóm tắt nhỏ gọn trước `/compact`
- Cụm từ kích hoạt: "session state", "what did we do", "session recap", "archive session"

### Không làm gì

- **Không sửa đổi** hồ sơ hoặc nội dung—chỉ theo dõi siêu dữ liệu.
- **Không tự động lưu trữ**—chỉ khi rõ ràng `--archive`.
- **Không xóa** lưu trữ—chỉ ghi thêm vào lịch sử phiên.
