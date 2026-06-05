# orc:observe

> Emit cross-framework observation signals for passive telemetry and learning.

## What it does

Framework skills emit signals when they notice patterns worth recording: defense mechanisms, CRAAP scores, voice drift, competency changes, PII matches. Read-only framework utility. Signals accrete in observation stream for `orc:compounding` to mine into instincts. Distinct from event-log (which routes cascades); observations are passive signals, not cascade triggers.

## When to use

- **At end of framework skill work** — skill noticed something worth remembering
- **Pattern observation checkpoints** — psychology detected a defense pattern
- **Content quality signals** — voice drift or evidence violations
- **Growth tracking** — competency deltas observed
- Trigger phrases: "observe", "emit signal", "note observation", "record signal"

## Flags

| Flag | Effect |
|------|--------|
| `--framework <fw>` | Framework: psy, mat, cre, gro, orc, com |
| `--signal <type>` | Signal type (e.g., defense-pattern, low-craap, voice-drift) |
| `--payload <json>` | Signal data as JSON (max 2 KB) |
| `--source <skill>` | Originating skill name |
| `--json` | JSON output |

## What it does NOT do

- Does NOT trigger cascades—observations are passive, not routing events.
- Does NOT modify files—signals are appended to observation stream only.
- Does NOT delete observations—all are kept for analysis.

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

### Nó làm gì

Các kỹ năng khung phát hành tín hiệu khi chúng nhận thấy các mẫu đáng ghi lại: các cơ chế phòng vệ, điểm CRAAP, drift giọng, thay đổi năng lực, trận đấu PII. Công cụ khung chỉ đọc. Tín hiệu tích lũy trong luồng quan sát để `orc:compounding` khai thác thành các bản năng. Khác biệt với event-log (định tuyến tầng); quan sát là tín hiệu thụ động, không phải kích hoạt tầng.

### Khi nào dùng

- **Ở cuối công việc kỹ năng khung** — kỹ năng nhận thấy điều gì đó đáng nhớ
- **Các điểm kiểm tra quan sát mẫu** — tâm lý học phát hiện một mẫu phòng vệ
- **Tín hiệu chất lượng nội dung** — drift giọng hoặc vi phạm bằng chứng
- **Theo dõi tăng trưởng** — quan sát các delta năng lực
- Cụm từ kích hoạt: "observe", "emit signal", "note observation", "record signal"

### Không làm gì

- **Không kích hoạt** tầng—quan sát là thụ động, không định tuyến sự kiện.
- **Không sửa đổi** tệp—tín hiệu chỉ được ghi vào luồng quan sát.
- **Không xóa** quan sát—tất cả được giữ để phân tích.
