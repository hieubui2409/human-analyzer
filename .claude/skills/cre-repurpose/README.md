# cre:repurpose

> Adapt existing content from one platform to another (1→1) while respecting platform constraints — LinkedIn→TikTok, blog→Twitter, etc. Post-publish, not generation. Shares DRY constraint source with `cre:multiplatform`.

## What it does

Takes a published post (from `assets/{platform}/` or external link). Reads it, identifies core message. Adapts to target platform: adjust length, reformat structure, modify tone/hook, update hashtags. Runs privacy check + voice audit before output. Outputs standard 5-file package to `assets/{target-platform}/{slug}/`. Emits `CRE.published` event.

## When to use

- Maximizing reach — one post written, repurposed to N platforms sequentially (1→1 per repurpose invocation)
- Cross-platform distribution (blog → Twitter thread, LinkedIn → Instagram caption)
- Adapting published content to new platforms (e.g., old blog post → current TikTok audience)
- Unlike `cre:multiplatform`: repurpose works 1→1 and is post-publish; multiplatform is 1→N and generation-time

## Flags

| Flag | Effect |
|------|--------|
| `--from <path\|platform>` | Source: file path or platform name to find latest post (required) |
| `--to <platform>` | Target platform (required) |
| `--character <name>` | Character context (improves voice audit) |
| `--tone <override>` | Override tone for target (optional) |

## What it does NOT do

- **Not generative** — adapts existing content, doesn't create new angles
- **Not multiplatform** — one invocation = one output; use `cre:multiplatform` for 1→N
- **Not a reformat tool** — adapts structure per platform conventions, not just length
- **Not a bypass** — mandatory gates (privacy, voice) block if issues found
- **Not a duplicate of platform_constraints** — imports from single source (shared with `cre:multiplatform`)

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)
- Related: `cre:multiplatform` (1→N native generation), `cre:post-writer` (single platform)
- Rules: Rule 03 (content pipeline), Rule 14 (CRE evidence + events)

---

## Tiếng Việt

**Công dụng:** Lấy một bài đăng đã công bố (từ `assets/{platform}/` hoặc liên kết bên ngoài). Đọc nó, xác định thông điệp cốt lõi. Thích ứng với nền tảng đích: điều chỉnh độ dài, định dạng lại cấu trúc, sửa đổi giọng điệu/móc, cập nhật hashtag. Chạy kiểm tra quyền riêng tư + kiểm toán giọng điệu trước khi xuất. Xuất ra gói 5 tệp tiêu chuẩn.

**Khi nào sử dụng:**
- Tối đa hóa reach — một bài viết được viết, được sử dụng lại cho N nền tảng tuần tự
- Phân phối đa nền tảng (blog → Twitter thread, LinkedIn → Instagram caption)
- Thích ứng nội dung đã công bố với các nền tảng mới
- Khác với `cre:multiplatform`: sử dụng lại làm việc 1→1 và sau khi công bố

**Điều nó KHÔNG làm:**
- Không sinh ra — thích ứng nội dung hiện tại, không tạo góc mới
- Không multiplatform — một lệnh gọi = một đầu ra
- Không phải công cụ định dạng lại — thích ứng cấu trúc theo quy ước nền tảng
- Không phải bỏ qua — các cổng bắt buộc có thể chặn
