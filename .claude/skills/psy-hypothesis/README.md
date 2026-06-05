# psy:hypothesis

> Predict character behavior given hypothetical events using psychological profile patterns and clinical reference theories.

## What it does

Analyzes a character's profile (SOUL, DARKNESS, LIGHT, core wounds, defense mechanisms, triggers, attachment style) against a hypothetical scenario. Outputs behavioral predictions at shallow/deep/clinical depth. Traces triggers, coping mechanisms, defense patterns, attachment responses. Optionally analyzes cascading impact on related characters (--multi flag).

## When to use

- Planning future story arcs: "How would Nhân vật B react if his father returned?"
- Content ideation: "What would Nhân vật C post if he got the scholarship?"
- Crisis prevention: "If Nhân vật A burns out, what's the risk?"
- Understanding dynamics: "How do their patterns interact when X happens?"

## Flags

| Flag                              | Effect |
|-----------------------------------|--------|
| `--character <name>`              | Target character (required) |
| `--scenario '<desc>'`             | Hypothetical event (required) |
| `--depth shallow\|deep\|clinical` | Analysis depth (default: deep) |
| `--multi`                         | Cascade to related characters |

## What it does NOT do

- Does NOT make real clinical predictions — narrative tool only
- Does NOT modify profiles (read-only analysis)
- Does NOT replace crisis assessment (if scenario involves crisis, run psy:crisis-assess separately)
- Does NOT provide therapy guidance

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

**Dự đoán hành vi nhân vật** dựa trên các mẫu hồ sơ tâm lý và lý thuyết tham chiếu lâm sàn.

**Khi nào sử dụng:** Lập kế hoạch các cung điểm câu chuyện trong tương lai, sáng tạo nội dung, hoặc hiểu rõ hơn về động lực.
