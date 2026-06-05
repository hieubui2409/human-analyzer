# psy:arc-tracker

> Track character growth arcs — compare hypothesis predictions vs actual profile evolution, verify milestones, document trajectory.

## What it does

Extracts growth indicators from profiles (coping evolution, crisis reduction, protective-factors strengthening, timeline patterns). Maps to growth trajectory (GROWTH/PLATEAU/REGRESSION). Optionally compares past `psy:hypothesis` predictions against current profile state to score prediction accuracy. Reviews milestone achievement (ACHIEVED/IN_PROGRESS/NOT_STARTED/REGRESSED). Outputs arc analysis with confidence levels.

## When to use

- Periodic arc review (monthly/quarterly): "Where is this character now?"
- Post-major-event: "Did they respond as predicted?"
- Content strategy: "What growth stage are they in?"
- Trigger phrases: arc tracker, growth tracking, character development, milestone check, arc review, character progress

## Flags

| Flag                          | Effect |
|-------------------------------|--------|
| `--character <name>`          | Target character (required) |
| `--trajectory`                | Growth trajectory analysis (default) |
| `--milestones`                | Review milestone progress |
| `--compare <hypothesis-date>` | Compare prediction vs reality |
| `--report`                    | Save report to plans/reports/ |

## What it does NOT do

- Does NOT modify profiles (read-only analysis)
- Does NOT diagnose real growth (narrative assessment only)
- Does NOT predict future (that's psy:hypothesis)
- Does NOT replace clinical judgment (observational tool)

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

**Theo dõi cung điểm tăng trưởng nhân vật** — so sánh dự đoán giả thuyết so với sự phát triển hồ sơ thực tế, xác minh các cột mốc.

**Khi nào sử dụng:** Xem xét cung điểm định kỳ, sau sự kiện lớn, hoặc lập kế hoạch nội dung.
