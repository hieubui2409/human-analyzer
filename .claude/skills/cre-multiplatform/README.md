# cre:multiplatform

> Generate N platform-native content variants simultaneously from one source/angle — LinkedIn/Facebook/Instagram/TikTok/YouTube/Twitter/blog. Each is written native to its platform (not reformatted cross-posts), gated per-variant by evidence tier, voice consistency, and privacy threshold.

## What it does

Takes one angle, CONTEXT.md, or existing post. Scaffolds native briefs for N platforms (LinkedIn, Facebook, Instagram, TikTok, YouTube, Twitter, blog — or active subset). LLM writes a distinct native post per platform (not watermarked rewrites). Per-variant gates: evidence-scanner, voice-audit, privacy-guard. Variants that fail gates are HELD, not published. Emits `CRE.published` event per written variant.

## When to use

- Generating from one discovered angle to multiple platforms (batch creation)
- Feeding `cre:angle-discovery --top N --json` output → loop per angle
- Cross-platform distribution of a single concept (multiplatform campaign)
- When you need native structure per platform, not copy-paste reformatting

## Flags

| Flag | Effect |
|------|--------|
| `--source <path\|angle>` | Angle JSON, CONTEXT.md path, or existing post path (required) |
| `--slug <slug>` | Asset naming slug (e.g., 260526-mentorship-arc) (required) |
| `--platforms <list>` | active (default) \| all \| linkedin,tiktok,facebook (comma-list) |
| `--character <slug>` | Link variants to character voice profile (improves voice audit) |
| `--dry-run` | Preview dirs + briefs, no writes |

## What it does NOT do

- **Not a reformat tool** — each platform gets a NATIVE post written from scratch, not a reformatted master copy
- **Not a bypass** — per-variant gates can block; blocked variants are HELD, reported, never forced through
- **Not a single-publish** — each platform gets its own event (`CRE.published` per variant), not one bulk event
- **Not a DRY violation** — platform rules live in one place (`platform_constraints.py`); shared with `cre:repurpose`
- **Not faster than serial** — actually slower to write N natives vs. one master, but engagement 2-3× higher

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)
- Related: `cre:angle-discovery`, `cre:post-writer` (single platform), `cre:repurpose` (1→1 post-publish)
- Rules: Rule 03 (content pipeline), Rule 14 (CRE evidence + events)

---

## Tiếng Việt

**Công dụng:** Lấy một góc nhìn, CONTEXT.md, hoặc bài đăng hiện tại. Lập kế hoạch cho các bài viết gốc cho N nền tảng. LLM viết một bài gốc riêng biệt trên mỗi nền tảng. Các cổng cách ly cạnh tranh: quét bằng chứng, kiểm toán giọng điệu, bảo vệ quyền riêng tư.

**Khi nào sử dụng:**
- Tạo từ một góc nhìn được khám phá cho nhiều nền tảng (tạo hàng loạt)
- Phân phối đa nền tảng của một khái niệm duy nhất (chiến dịch đa nền tảng)
- Khi bạn cần cấu trúc gốc trên mỗi nền tảng, không phải sao chép dán

**Điều nó KHÔNG làm:**
- Không phải công cụ định dạng lại — mỗi nền tảng nhận được bài gốc được viết từ đầu
- Không phải bỏ qua — các cổng cách ly cạnh tranh có thể chặn
- Không phải một lần công bố — mỗi nền tảng nhận được sự kiện của nó
