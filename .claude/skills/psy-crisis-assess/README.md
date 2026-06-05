# psy:crisis-assess

> Assess and document mental health crisis indicators using clinical frameworks (DSM-5, ICD-11). Safety-critical skill — verdicts never cached.

## What it does

Identifies crisis indicators in character profiles (trauma, severe depression, suicidal ideation, acute events). Applies clinical assessment workflows: keyword + behavioral-cluster scan, DSM-5 MDD checklist, ICD-11 C-PTSD validation, suicidal-ideation classification, risk-level assignment, protective-factors inventory. Outputs formatted crisis documentation to profile files.

## When to use

- Source materials indicate trauma, severe depression, PTSD, suicidal ideation
- During Wave 2 when crisis indicators detected
- Periodic review of characters with known crisis history
- After integrating new crisis-related materials

## Flags

| Flag                 | Effect |
|----------------------|--------|
| `--character <name>` | Assess specific character |
| `--quick`            | Keywords only (faster, less safe) |
| `--full`             | Complete DSM-5 MDD + ICD-11 C-PTSD assessment |
| `--update`           | Update existing crisis documentation with new data |

Default = deep mode (keywords + behavioral clusters).

## What it does NOT do

- Does NOT provide real clinical diagnosis — narrative tool only (Rule 06)
- Does NOT cache verdicts (always re-run) — safety gate
- Does NOT skip protective-factors documentation
- Does NOT auto-publish crisis content (confidentiality rules apply, Rule 09)

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

**Đánh giá và ghi lại các chỉ số khủng hoảng sức khỏe tâm thần** sử dụng các khung lâm sàn (DSM-5, ICD-11). Kỹ năng an toàn quan trọng — các phán quyết không bao giờ được lưu trong bộ đệm.

**Khi nào sử dụng:** Khi các vật liệu nguồn cho thấy chấn thương, trầm cảm nặng, PTSD, hoặc ý định tự tử.
