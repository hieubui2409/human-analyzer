# orc:classify

> Classify task risk level and determine workflow ceremony before implementation.

## What it does

Analyzes incoming work and rates it as tiny, normal, or high_risk based on hard gates and flag counts. Outputs required ceremony steps, proof strategy, and recommendations. Writes classification to session state. Use before starting any implementation work.

## When to use

- **At start of any new task** — before `/ck:plan` or implementation
- **Profile updates** — before editing psychology/, relationships/, timeline/
- **Content creation** — before writing posts or scripts
- **Cross-character work** — when changes affect multiple characters
- Trigger phrases: "classify", "what's the risk", "is this risky", "ceremony needed"

## Flags

| Flag | Effect |
|------|--------|
| (positional) | Task description text |
| `--auto` | Auto-classify from git diff + branch, skip user prompt |
| `--show` | Show current classification from state.json without re-classifying |

## What it does NOT do

- Does NOT execute implementation—only assesses risk and recommends ceremony.
- Does NOT modify profiles or content—read-only analysis only.
- Does NOT enforce ceremony—it recommends; you decide whether to follow.

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

### Nó làm gì

Phân tích công việc đến và xếp hạng nó là tiny, normal, hoặc high_risk dựa trên các cổng cứng và số lượng cờ. Xuất ra các bước lễ nghi cần thiết, chiến lược chứng minh, và khuyến nghị. Ghi phân loại vào trạng thái phiên. Sử dụng trước khi bắt đầu bất kỳ công việc triển khai nào.

### Khi nào dùng

- **Ở bắt đầu bất kỳ nhiệm vụ mới nào** — trước `/ck:plan` hoặc triển khai
- **Cập nhật hồ sơ** — trước khi chỉnh sửa psychology/, relationships/, timeline/
- **Tạo nội dung** — trước khi viết bài hoặc kịch bản
- **Công việc đa nhân vật** — khi thay đổi ảnh hưởng đến nhiều nhân vật
- Cụm từ kích hoạt: "classify", "what's the risk", "is this risky", "ceremony needed"

### Không làm gì

- **Không thực hiện** triển khai—chỉ đánh giá rủi ro và khuyến nghị lễ nghi.
- **Không sửa đổi** hồ sơ hoặc nội dung—chỉ phân tích chỉ đọc.
- **Không thực thi** lễ nghi—nó khuyến nghị; bạn quyết định có tuân theo hay không.
