# com:git

> Smart commit and push with conventional commit format. No forced pushes to protected branches.

## What it does

Analyzes changed files, selects related ones intelligently, stages changes, commits with conventional commit messages, and pushes with automatic rebase handling. Excludes secrets (.env, credentials) and supports preview/confirmation before committing.

## When to use

- User says "commit", "push", "save changes", "commit my work"
- Typical workflow position: after implementing features or fixing bugs, before starting new work

## Flags

| Flag       | Effect                                                    |
| ---------- | --------------------------------------------------------- |
| `--commit` | Analyze, select files, preview, and commit (no push)      |
| `--push`   | Push to remote with automatic rebase on conflict          |
| `--sync`   | Pull and rebase from remote                               |
| `--auto`   | Skip confirmation; commit and push fully automatically    |
| `--all`    | Commit ALL changed files (still excludes secrets)         |
| `--dry-run`| Preview what would be committed without executing        |
| `-m "msg"` | Custom commit message body                                |

## What it does NOT do

- **Never force-pushes** to any branch (Rule 12 — orchestration boundaries; user approval required)
- **Never commits secrets** like `.env`, `credentials`, `*.key`, `*.pem` — automatically excluded
- **Does not auto-resolve rebase conflicts** — reports to user and stops
- **Does not work on detached HEAD** — requires a branch
- **Does not handle merge conflicts from pull** — user must resolve manually

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

Phân tích các tệp đã thay đổi, chọn những tệp liên quan một cách thông minh, ghi sơ đồ các thay đổi, xác nhận bằng thông điệp commit thông thường, và đẩy với xử lý rebase tự động. Loại trừ các bí mật (.env, credentials) và hỗ trợ xem trước/xác nhận trước khi commit.

**Khi sử dụng:** người dùng nói "commit", "push", "lưu changes", "commit công việc của tôi" — thường sau khi hoàn thành tính năng hoặc sửa lỗi.

**Không làm gì:**
- Không bao giờ force-push đến bất kỳ nhánh nào
- Không bao giờ commit các bí mật như `.env`, `credentials`
- Không tự động giải quyết xung đột rebase
