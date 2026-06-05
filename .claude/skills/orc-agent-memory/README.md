# orc:agent-memory

> Manage persistent learning memory for domain-specific agents (psychologist, content-strategist, growth-analyst).

## What it does

Stores and retrieves domain-specific insights learned by custom agents working on character profiles. Agents read their memory before starting work, append learnings after completing tasks. Use to view current agent learnings, seed memory from active profiles, or reset memory if needed.

## When to use

- **After domain work** — agent appends new character insights, patterns, or anti-patterns to memory
- **Before starting a session** — agent reads relevant memory files to apply learned patterns
- **Periodic review** — check what each agent has learned about each character
- **Memory reset** — clear memory if inconsistencies accumulate or to start fresh
- Trigger phrases: "agent memory", "what has the agent learned", "agent learnings", "reset agent memory"

## Flags

| Flag | Effect |
|------|--------|
| (none) | `--show` mode: display all agent memories with instinct stats (default) |
| `--show` | Show current agent memories (default) |
| `--seed` | Initialize agent memory from profiles + instincts |
| `--reset` | Clear agent memory with backup |
| `--agent <name>` | Filter to one agent: `psychologist`, `content-strategist`, or `growth-analyst` |
| `--instinct-feed <name>` | Show only instinct-relevant data for an agent |

## What it does NOT do

- Does NOT edit profile files—only reads from them to seed initial memory.
- Does NOT execute domain work—agents invoke this skill before/after their own work (Rule 12).
- Does NOT auto-trigger—manual invocation only; agents must decide when to read/write memory.

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

### Nó làm gì

Lưu trữ và truy xuất kiến thức cụ thể miền được học bởi các tác nhân tùy chỉnh làm việc trên hồ sơ nhân vật. Các tác nhân đọc bộ nhớ của họ trước khi bắt đầu công việc, ghi lại những học tập sau khi hoàn thành nhiệm vụ. Dùng để xem kiến thức hiện tại của tác nhân, khởi tạo bộ nhớ từ hồ sơ hoạt động, hoặc đặt lại bộ nhớ nếu cần.

### Khi nào dùng

- **Sau công việc miền** — tác nhân ghi lại những điểm sáng về nhân vật, các mẫu, hoặc anti-pattern mới
- **Trước khi bắt đầu phiên** — tác nhân đọc các tệp bộ nhớ liên quan để áp dụng các mẫu đã học
- **Kiểm tra định kỳ** — xem từng tác nhân đã học gì về từng nhân vật
- **Đặt lại bộ nhớ** — xóa bộ nhớ nếu không nhất quán tích tụ hoặc để bắt đầu lại
- Cụm từ kích hoạt: "agent memory", "what has the agent learned", "agent learnings", "reset agent memory"

### Không làm gì

- **Không sửa đổi** các tệp hồ sơ—chỉ đọc từ chúng để khởi tạo bộ nhớ ban đầu.
- **Không thực hiện** công việc miền—các tác nhân gọi kỹ năng này trước/sau công việc của họ (Rule 12).
- **Không tự động kích hoạt**—chỉ gọi thủ công; các tác nhân phải quyết định khi nào đọc/ghi bộ nhớ.
