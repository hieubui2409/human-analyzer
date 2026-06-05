# orc:bootstrap

> Systematically load character profiles and session context at the start of work.

## What it does

Loads project context on demand: character profiles (INDEX + selective deep-dive), recent git history, and session state. Default mode is quick (INDEX for all 3 characters + recent changes). Use flags to load lite profiles (~400 lines vs full ~7400), focus on one character, or load only files relevant to your stated intent.

## When to use

- **Session start** (after `/orc:classify` or at any point you feel context-stale)
- **Character focus shift** (switching from Nhân vật A work to Nhân vật B work)
- **Context is old** (after a long gap, before high-risk work)
- Trigger phrases: "bootstrap", "load context", "refresh context", "catch me up"

## Flags

| Flag | Effect |
|------|--------|
| (none) | `--quick` mode: INDEX for all 3 characters + recent git changes (default) |
| `--quick` | Same as default |
| `--full` | Load all profile files for all characters + references + rules |
| `--character <name>` | Deep-load one character's full profile + related materials |
| `--recent` | Last 7 days git activity only (commits + file changes) |
| `--lite` | Cached lite profiles (~120-150 lines each, ~400 total vs ~7400 full) |
| `--intent <task>` | Task-aware loading—only load files relevant to your stated intent |

## What it does NOT do

- Does NOT modify profiles, content, or any files—strictly read-only (Rule 12 / domain boundary: ORC reads, does not write profile/material data).
- Does NOT parse clinical theories—just loads references/INDEX.md as context pointer, not deep analysis.
- Does NOT emit domain events—`orc:bootstrap` is pre-work context load, not a cascade trigger.

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

### Nó làm gì

Tải ngữ cảnh dự án khi cần thiết: hồ sơ nhân vật (INDEX + tải sâu lựa chọn), lịch sử git gần đây, và trạng thái phiên. Chế độ mặc định là nhanh (INDEX cho cả 3 nhân vật + các thay đổi gần đây). Dùng flag để tải hồ sơ lite (~400 dòng so với đầy đủ ~7400), tập trung vào một nhân vật, hoặc chỉ tải những tệp liên quan đến ý định của bạn.

### Khi nào dùng

- **Bắt đầu phiên** (sau `/orc:classify` hoặc bất cứ khi nào bạn cảm thấy ngữ cảnh cũ)
- **Chuyển tiêu điểm nhân vật** (từ công việc Nhân vật A sang công việc Nhân vật B)
- **Ngữ cảnh đã cũ** (sau một khoảng thời gian dài, trước công việc rủi ro cao)
- Cụm từ kích hoạt: "bootstrap", "tải ngữ cảnh", "làm mới ngữ cảnh", "cập nhật tôi"

### Không làm gì

- **Không sửa đổi** hồ sơ, nội dung hoặc bất kỳ tệp nào—chỉ đọc (Rule 12 / ranh giới miền: ORC đọc, không ghi dữ liệu hồ sơ/tài liệu).
- **Không phân tích** sâu các lý thuyết lâm sàng—chỉ tải references/INDEX.md như một con trỏ ngữ cảnh.
- **Không phát hành sự kiện miền**—`orc:bootstrap` là tải ngữ cảnh trước công việc, không phải kích hoạt tầng.
