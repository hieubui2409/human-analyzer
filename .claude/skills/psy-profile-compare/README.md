# psy:profile-compare

> Side-by-side character profile comparison — extract a specific dimension from 2+ characters and output structured comparison table.

## What it does

Extracts a named profile section (defense-mechanisms, attachment-style, core-wounds, formulation, traumas, strengths-hope, family, writing-voice, timeline, etc.) from multiple characters. Renders side-by-side markdown table with key findings. Highlights contrasts, overlaps, and interaction dynamics.

## When to use

- Understand character contrasts: "How do Nhân vật A and Nhân vật B's defense mechanisms differ?"
- Spot complementary patterns: "Do their attachment styles create stable or volatile dynamics?"
- Identify enrichment opportunities: "What growth theories apply to Nhân vật C but not the others?"

## Flags

| Flag                       | Effect |
|----------------------------|--------|
| `--dimension <name>`       | Section to compare (required) |
| `--characters <c1,c2,...>` | Which characters (default: all) |
| `--json`                   | Output as JSON |

## What it does NOT do

- Does NOT modify profiles (read-only comparison only)
- Does NOT validate consistency (that's psy:crossref)
- Does NOT assess quality of content (that's psy:health-check)
- Does NOT assess clinical accuracy (that's psy:ref-audit)

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

**So sánh hồ sơ nhân vật song song** — trích xuất một chiều cụ thể từ 2+ nhân vật và đầu ra bảng so sánh có cấu trúc.

**Khi nào sử dụng:** Hiểu những điểm tương phản của nhân vật, chỉ ra những mẫu bổ sung, hoặc xác định cơ hội làm giàu.
