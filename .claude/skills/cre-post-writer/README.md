# cre:post-writer

> End-to-end content creation pipeline — character + platform + topic → published-ready draft. Loads voice, applies clinical framing, validates evidence and privacy, outputs to assets/.

## What it does

Interactive or scripted entry point to content creation. Takes character, platform, content type (reality/fiction/analysis/letter), and topic. Loads character lite profile, applies voice constraints + clinical accuracy guards + platform formatting. Generates draft, runs mandatory validation (evidence tier, voice consistency, privacy), outputs 5-file package to `assets/{platform}/{slug}/`.

## When to use

- Creating any social media post, blog article, or long-form content
- When you want guidance (Q1-Q5 interactive mode)
- Consuming CONTEXT.md from `cre:exploring` (`--from-context`)
- Batch workflows with `cre:exploring` → `--from-context`

## Flags

| Flag | Effect |
|------|--------|
| (topic) | Start with given topic (optional) |
| `--character <name>` | Which character (hiếu/hòa/chiến) |
| `--platform <name>` | Target platform (linkedin/facebook/instagram/tiktok/youtube/twitter/blog) |
| `--type <type>` | Content type: reality, fiction, analysis, letter (default: reality) |
| `--from-context` | Use CONTEXT.md from `cre:exploring` (skip interactive) |
| `--quick` | Skip profile loading (use session context) |

## What it does NOT do

- **Not autonomous** — asks for input (interactive mode) or consumes CONTEXT.md (`--from-context`)
- **Not a bypass** — mandatory gates (evidence, voice, privacy) block generation if issues found
- **Not a single-pass writer** — Phase 5-6 validation may require fixes; author re-runs until passing
- **Not multiplatform** — generates one platform per invocation; use `cre:multiplatform` for 1→N
- **Not a publisher** — outputs to assets/, author manually posts

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)
- Related: `cre:exploring`, `cre:prompt-leverage`, `cre:multiplatform`, `cre:evidence-scanner`
- Rules: Rule 03 (content pipeline), Rule 09 (confidentiality), Rule 14 (CRE evidence)

---

## Tiếng Việt

**Công dụng:** Điểm vào đầy đủ để tạo nội dung. Lấy nhân vật, nền tảng, loại nội dung (reality/fiction/analysis/letter) và chủ đề. Tải hồ sơ nhẹ của nhân vật, áp dụng ràng buộc giọng điệu + bảo vệ độ chính xác lâm sàn + định dạng nền tảng. Tạo bản nháp, chạy xác nhận bắt buộc (cấp độ bằng chứng, tính nhất quán giọng điệu, quyền riêng tư), xuất ra gói 5 tệp cho `assets/{platform}/{slug}/`.

**Khi nào sử dụng:**
- Tạo bất kỳ bài đăng trên mạng xã hội, bài viết blog hoặc nội dung dạng dài
- Khi bạn muốn hướng dẫn (chế độ tương tác Q1-Q5)
- Tiêu thụ CONTEXT.md từ `cre:exploring` (`--from-context`)
- Luồng công việc hàng loạt với `cre:exploring` → `--from-context`

**Điều nó KHÔNG làm:**
- Không tự chủ động — yêu cầu đầu vào (chế độ tương tác)
- Không phải bỏ qua — các cổng bắt buộc có thể chặn
- Không phải một lần viết duy nhất — xác nhận Giai đoạn 5-6 có thể yêu cầu sửa chữa
- Không phải multiplatform — tạo một nền tảng cho mỗi lệnh gọi
- Không phải nhà xuất bản — xuất ra assets/
