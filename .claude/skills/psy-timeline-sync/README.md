# psy:timeline-sync

> Timeline date validation and consistency check — extract dates from all profiles, cross-compare shared events, report mismatches with suggested fixes.

## What it does

Parses `timeline/overview.md`, `timeline/state-timeline.md`, and `milestones.md` for all characters. Extracts event-date pairs. Identifies events mentioning other characters. Cross-compares: does "kết nghĩa Sep 2025" appear in both Nhân vật A and Nhân vật B's timelines? If dates differ or event missing from one side, flags as MISMATCH. Outputs detailed sync report with recommendations (which file to update, suggested date).

## When to use

- Post-profile-update: "Did I sync dates across characters?"
- Before psy:crossref: "Are shared events date-aligned?"
- Periodic audit: "Are timelines consistent across the corpus?"
- Trigger phrases: sync timelines, timeline consistency, date mismatch, check dates, timeline audit

## Flags

| Flag                 | Effect |
|----------------------|--------|
| `--character <name>` | Check one character's timeline only |
| `--all`              | Cross-check all characters (default) |
| `--json`             | Output as JSON |

## What it does NOT do

- Does NOT modify profiles (read-only audit)
- Does NOT validate event accuracy (that's psy:crossref Dimension 4)
- Does NOT check psychological consistency (that's psy:crossref Dimension 3)
- Does NOT assess content quality (that's psy:health-check)

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

**Xác thực và kiểm tra tính nhất quán của dòng thời gian** — trích xuất ngày từ tất cả các hồ sơ, so sánh chéo các sự kiện chung, báo cáo không phù hợp với các bản sửa được đề xuất.

**Khi nào sử dụng:** Sau khi cập nhật hồ sơ, trước khi psy:crossref, hoặc kiểm tra định kỳ.
