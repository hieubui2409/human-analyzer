# com:health-check

> Monitor Claude Code session health — detect stalls, API errors, process death.

## What it does

Polls session state (JSONL mtime, content, process liveness) at regular intervals. Emits notifications (Monitor tool) when stalls, API errors, or process death are detected. Watches main agent, subagents, or team sessions independently.

## When to use

- User says "monitor health", "watch session", "health check"
- After spawning long-running subagents or teams
- Typical position: run concurrently with work (background task)

## Flags

| Flag            | Effect                                    |
| --------------- | ----------------------------------------- |
| `--target`      | main / subagent / team / all              |
| `--soft`        | Soft stall threshold in seconds (warn)    |
| `--hard`        | Hard stall threshold in seconds (error)   |
| `--verbosity`   | error / warn / info / debug               |
| `--poll`        | Poll interval in seconds                  |
| `--include-429` | Report 429 rate-limit errors              |

## What it does NOT do

- **Does not auto-retry failed subagents** — reports errors, user/orchestrator decides retry
- **Does not parse session transcripts for semantic meaning** — checks only mtime + process state
- **Does not fix stalls** — alerts; investigation/remediation is manual
- **Does not modify session files** — read-only monitoring
- **Does not predict future errors** — reactive, not predictive

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

Thăm dò trạng thái phiên (JSONL mtime, nội dung, liveness của quy trình) ở những khoảng thời gian đều đặn. Phát hành thông báo (Monitor tool) khi phát hiện sự trì hoãn, lỗi API hoặc chết của quy trình. Theo dõi các phiên tác nhân chính, tác nhân phụ hoặc nhóm một cách độc lập.

**Khi sử dụng:** người dùng nói "monitor health", "watch session", "health check" — thường chạy đồng thời với công việc.

**Không làm gì:**
- Không tự động thử lại tác nhân phụ bị lỗi
- Không phân tích siêu dữ liệu ngữ nghĩa
- Không khắc phục các sự trì hoãn
- Không sửa đổi các tệp phiên
- Không dự đoán lỗi trong tương lai
