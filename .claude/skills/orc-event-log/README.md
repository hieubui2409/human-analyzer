# orc:event-log

> Persistent event logging and audit trail for cross-domain ORC events.

## What it does

Appends framework events (MAT.integrated, PSY.refresh, CRE.recalibrate, etc.) to 6 framework-partitioned JSONL streams. Query with filters (event type, character, date, skill). Provides audit trail for all domain cascades. Read-only for queries; append-only for events.

## When to use

- **After domain events fire** — log the event for audit trail
- **Debugging event chains** — query which events happened when
- **Event audit** — who triggered what, when
- Trigger phrases: "log event", "event history", "audit trail", "show events"

## Flags

| Flag | Effect |
|------|--------|
| `--append --event-type <type>` | Append an event to log |
| `--query` | Query events (default) |
| `--event-type <type>` | Filter by event type |
| `--character <name>` | Filter by character |
| `--since <date>` | Events after this date |
| `--source <skill>` | Filter by originating skill |
| `--limit <N>` | Max results (default: 20) |
| `--json` | JSON output |

## What it does NOT do

- Does NOT execute skills—only logs events.
- Does NOT modify files—log is append-only.
- Does NOT auto-clean old events—all are kept for history.

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

### Nó làm gì

Ghi thêm các sự kiện khung (MAT.integrated, PSY.refresh, CRE.recalibrate, v.v.) vào 6 luồng JSONL được phân vùng khung. Truy vấn với bộ lọc (loại sự kiện, nhân vật, ngày, kỹ năng). Cung cấp dấu vết kiểm tra cho tất cả các tầng miền. Chỉ đọc cho truy vấn; chỉ ghi thêm cho các sự kiện.

### Khi nào dùng

- **Sau khi các sự kiện miền kích hoạt** — ghi lại sự kiện cho dấu vết kiểm tra
- **Gỡ lỗi chuỗi sự kiện** — truy vấn những sự kiện nào xảy ra khi nào
- **Kiểm tra sự kiện** — ai kích hoạt cái gì, khi nào
- Cụm từ kích hoạt: "log event", "event history", "audit trail", "show events"

### Không làm gì

- **Không thực hiện** kỹ năng—chỉ ghi lại sự kiện.
- **Không sửa đổi** tệp—nhật ký chỉ ghi thêm.
- **Không tự động làm sạch** các sự kiện cũ—tất cả được giữ để có lịch sử.
