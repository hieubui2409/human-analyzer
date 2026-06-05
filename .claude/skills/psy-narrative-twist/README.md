# psy:narrative-twist

> Handle revealed falsehoods and narrative corrections. Apply strikethrough + ⚠️ TWIST markers and cascade updates across all affected files and cross-character profiles.

## What it does

Applies narrative twist protocol when new source data invalidates a previously established "fact". Finds all occurrences (exact + fuzzy match), applies strikethrough + TWIST marker with source/date. Updates timeline, cross-character relationship files symmetrically, psychology files if twist affects core wound. Validates symmetry with psy:crossref.

## When to use

- New source invalidates old "fact": "We thought X happened, but actually Y"
- Character's public story is revealed as fabricated
- Relationship's true nature disclosed
- Auto-triggered by psy:wave Wave 2 when contradictions detected

## Flags

| Flag                 | Effect |
|----------------------|--------|
| `--character <name>` | Target character |
| `--fact '<old>'`     | Invalidated fact (quoted) |
| `--truth '<new>'`    | Revealed truth (quoted) |
| `--source '<src>'`   | Source: priority level + date |
| `--scan`             | Scan all profiles for unresolved twists |
| `--list`             | List existing ⚠️ TWIST markers |

## What it does NOT do

- Does NOT delete old narrative (strikethrough only, preserves history)
- Does NOT skip cross-character validation (mandatory psy:crossref after)
- Does NOT hide twist details (transparency in annotations)
- Does NOT treat twists casually (safety gate: requires source attribution)

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

**Xử lý các sự thật bị tiết lộ và các sửa chữa kêu gọi câu chuyện.** Áp dụng gạch bỏ + ⚠️ ký hiệu TWIST và cập nhật xếp tầng trên tất cả các tệp được ảnh hưởng.

**Khi nào sử dụng:** Khi dữ liệu nguồn mới làm vô hiệu hóa một "sự thật" đã được thiết lập trước đó, câu chuyện công cộng được tiết lộ là giả mạo, hoặc bản chất thực sự của mối quan hệ được tiết lộ.
