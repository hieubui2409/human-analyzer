# evl:track

> Show how a character's rubric score changed over time — deterministic diff + event join.

## What it does

Loads the current scorecard and the latest historical snapshot for a character + rubric pair,
computes overall / domain / verdict / coverage deltas (None-safe), and lists profile-change
events from PSY / GRO / MAT streams that fall in the requested time window. Prints a
markdown summary (or `--json`) so the LLM can narrate why the score moved. If there is
no history snapshot, reports that plainly — a first run has nothing to diff against.

## When to use

- **Trigger phrases:** "evl track", "track score over time", "score delta", "how did score change"
- **Workflow position:** after `evl:score` has produced at least two scorecards (current + one history snapshot)
- **Output user:** anyone auditing how a character's assessment evolved across scoring runs

## Flags

| Flag | Effect |
|------|--------|
| `--character <name>` | Character to track (dynamic resolution) |
| `--rubric-id <id>` | Rubric id whose scorecard history is inspected |
| `--since <ISO-Z>` | Filter profile-change events to this timestamp or later |
| `--json` | Machine-readable diff summary |

## What it does NOT do

- **Not a scoring tool:** no LLM judging, no criterion evaluation, no evidence gathering.
- **Not a causal engine:** the script lists events that MIGHT explain a delta; narrating WHY is the LLM's job.
- **Not a writer:** read-only — never modifies scorecards or profile files.

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

**Mục đích:** Tải scorecard hiện tại và snapshot lịch sử mới nhất cho một cặp nhân vật + rubric,
tính delta tổng thể / theo miền / verdict / độ phủ (an toàn với None), và liệt kê các sự kiện
thay đổi hồ sơ từ luồng PSY / GRO / MAT trong cửa sổ thời gian được yêu cầu. Xuất tóm tắt
markdown (hoặc `--json`) để LLM diễn giải lý do điểm thay đổi. Nếu không có snapshot lịch sử,
báo cáo rõ ràng — lần chạy đầu tiên không có gì để so sánh.

**Khi nào dùng:** Sau khi `evl:score` đã tạo ít nhất hai scorecard (hiện tại + một snapshot lịch sử).

**Không làm được:** Không chấm điểm (không có LLM judging). Không suy diễn nguyên nhân (liệt kê sự kiện để LLM diễn giải). Chỉ đọc — không bao giờ sửa scorecard hay hồ sơ.
