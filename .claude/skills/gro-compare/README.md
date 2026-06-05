# gro:compare

> Side-by-side comparison of career, competency, learning, and mentoring data across all 3 characters.

## What it does

Gathers growth data from all characters' 4 GRO files (career-path, competencies, learning-profile, mentoring-map) and generates comparative analysis: career stage differential, skill distribution, learning style compatibility, mentoring network interconnections. Outputs tables and insights.

## When to use

- **Trigger phrases:** "compare careers", "compare growth", "cross-character comparison", "gro compare"
- **Workflow position:** After individual GRO skills (career-path, competency-map, learning-profile, mentoring-track)
- **Output user:** profile builders exploring dyad/triad dynamics

## Flags

| Flag | Effect |
|------|--------|
| `--dimension career` | Career stage only |
| `--dimension competency` | Skill distribution only |
| `--dimension learning` | Learning style only |
| `--dimension mentoring` | Mentoring network only |
| `--dimension all` | All dimensions (default) |
| `--json` | Machine-readable output |

## What it does NOT do

- **Not decision-making:** does not compare decision-making patterns (use career-path --decisions-only for that)
- **Not analytical depth:** surface-level comparison; fine-grained insights require manual review
- **Boundary (Rule 15):** GRO only; no cross-domain (PSY) comparison (use psy:profile-compare for that)

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

**Mục đích:** So sánh dữ liệu lớn (giai đoạn sự nghiệp, kỹ năng, mô hình học tập, mạng lưới cố vấn) trên cả 3 nhân vật.

**Khi nào dùng:** Sau khi chạy các kỹ năng GRO riêng lẻ. Dùng để khám phá động lực dyad/triad.

**Không làm được:** Không so sánh các mô hình ra quyết định. Không so sánh giữa các lĩnh vực (PSY). Chỉ là so sánh bề mặt.
