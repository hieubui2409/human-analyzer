# Clinical Reference Usage Rules

How to use psychological theories from `docs/references/` in profiles and content.

## Core Principle: Show, Don't Tell

> "Ẩn giấu các lý thuyết phân tâm học dưới dạng văn phong đại chúng, thay vì bê nguyên y khoa lên MXH."

## Usage Contexts

### In Profile Files (docs/profiles/)

Clinical terms ARE allowed in profiles — they're internal documentation:

- Use precise clinical terminology
- Always link to reference file: `(See: docs/references/{theory}.md)`
- Explain how theory manifests in THIS character specifically
- Distinguish between confirmed patterns and hypotheses
- File locations use new nested schema (e.g., `psychology/attachment-style.md`)

Example:

```markdown
## Attachment Style

Nhân vật B exhibits **anxious-avoidant attachment** (See: `docs/references/anxious-attachment.md`):

- Craves connection but withdraws when it deepens
- Tests relationships through push-pull behavior
- Gambling crisis = attachment protest behavior
```

### In Social Media Content (assets/)

Clinical terms MUST NOT appear directly:

- Replace jargon with accessible language
- Describe behaviors, not diagnoses
- Use metaphor and narrative to convey psychological insights

| Clinical Term      | Social Media Alternative                     |
| ------------------ | -------------------------------------------- |
| Parentification    | "Phải làm người lớn khi còn là đứa trẻ"      |
| Anxious attachment | "Luôn sợ mất đi người mình yêu thương"       |
| Defense mechanism  | "Cách tự bảo vệ bản thân"                    |
| Savior complex     | "Cứu người khác để quên nỗi đau của mình"    |
| Hypervigilance     | "Lúc nào cũng cảnh giác, không dám thả lỏng" |
| Dissociation       | "Cảm giác tách rời khỏi chính mình"          |
| Trauma bonding     | "Gắn kết qua nỗi đau chung"                  |

### In Materials (docs/materials/)

Raw materials may contain clinical language from sources:

- Preserve original language (don't sanitize)
- Tag clinical terms for future reference indexing
- Note which reference file applies

## Reference Library Standards

### Creating New References

Each file in `docs/references/` must include:

1. **Theory name** and originator
2. **Core concept** (2-3 sentences)
3. **Behavioral indicators** — observable signs
4. **Application to characters** — which characters, how
5. **Vietnamese cultural context** — how theory manifests in Vietnamese family dynamics
6. **Accessible language mapping** — clinical → colloquial translations

### Reference Index

`docs/references/INDEX.md` must be updated when adding new references:

- Alphabetical listing
- One-line description per theory
- Character applicability tags

## Mandatory Clinical Referencing

See `10-reference-library-standard.md` for full NGUYÊN TẮC TỐI THƯỢNG rules:

1. **Trích dẫn bắt buộc** — Every psychological analysis MUST link to `docs/references/`
2. **Xóa vùng mù** — Unknown patterns → create reference FIRST, then apply to profile
3. **Tính khoa học** — All theories must cite DSM-5, ICD-11, or peer-reviewed sources

## Validation

- `psy:ref-audit` checks profile clinical accuracy
- `psy:ref-scan` maps theories to profile applications
- `psy:ref-audit --discover` finds clinical terms in materials/assets not yet in library
- Content review must verify "show don't tell" compliance before publishing
