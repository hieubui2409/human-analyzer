# orc:cascade

> Resolve multi-step event cascades across all framework domains.

## What it does

Takes a trigger event and maps out its entire downstream cascade chain across MAT, PSY, CRE, GRO domains. Detects circular references, enforces max-depth limits, and outputs an ordered tree of what should execute next. Read-only orchestration utility.

## When to use

- **After domain events fire** — understand the full cascade of downstream work needed
- **Planning a feature impact** — see what other domains get triggered by a change to one
- **Debugging cascades** — find circular references or unexpected depth chains
- Trigger phrases: "cascade", "event chain", "multi-domain", "what happens next"

## Flags

| Flag | Effect |
|------|--------|
| `--trigger <EVENT>` | Starting event (e.g., `MAT.integrated`) |
| `--max-depth <N>` | Maximum cascade depth (default: 5) |
| `--json` | JSON output format |

## What it does NOT do

- Does NOT execute downstream skills—only maps the cascade tree.
- Does NOT modify any files—read-only analysis only.
- Does NOT emit new events—this is planning, not action.

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

### Nó làm gì

Lấy một sự kiện kích hoạt và lập bản đồ toàn bộ chuỗi tầng dưới của nó trên các miền MAT, PSY, CRE, GRO. Phát hiện tham chiếu vòng tròn, thực thi giới hạn độ sâu tối đa, và xuất ra một cây được sắp xếp thứ tự của những gì nên thực hiện tiếp theo. Công cụ điều phối chỉ đọc.

### Khi nào dùng

- **Sau khi các sự kiện miền kích hoạt** — hiểu toàn bộ chuỗi công việc tầng dưới cần thiết
- **Lập kế hoạch tác động tính năng** — xem những miền nào khác được kích hoạt bởi một thay đổi cho một miền
- **Gỡ lỗi chuỗi tầng** — tìm tham chiếu vòng tròn hoặc chuỗi độ sâu không mong đợi
- Cụm từ kích hoạt: "cascade", "event chain", "multi-domain", "what happens next"

### Không làm gì

- **Không thực hiện** các kỹ năng tầng dưới—chỉ lập bản đồ cây tầng.
- **Không sửa đổi** bất kỳ tệp nào—chỉ phân tích chỉ đọc.
- **Không phát hành** sự kiện mới—đây là lập kế hoạch, không phải hành động.
