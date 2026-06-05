# psy:ref-create

> Create new clinical psychological theory reference files following mandatory schema (bilingual, citation-backed, Vietnamese cultural context, case study).

## What it does

Scaffolds a new theory reference file at `docs/references/{theory-name}.md` with mandatory sections: definition, origin, mechanism, Vietnamese cultural context, accessible language mapping, project case study. Requires scientific backing (DSM-5/ICD-11 or peer-reviewed literature). Updates `docs/references/INDEX.md` with new entry. Optional `--from-behavior` reverse-engineers behavior description into theory hypothesis.

## When to use

- `psy:ref-audit --discover` flags missing theories
- Character profile describes a pattern but no theory covers it
- Material evidence suggests a new clinical concept
- Trigger phrases: new reference, create theory, add reference, new theory, blind spot, missing theory

## Flags

| Flag                       | Effect |
|----------------------------|--------|
| `<theory-name>`            | Theory name (English, kebab-case) |
| `--character <name>`       | Pre-fill case study section |
| `--quick`                  | Minimal scaffold (definition + mechanism only) |
| `--from-behavior '<desc>'` | Reverse-engineer: behavior → theory |

## What it does NOT do

- Does NOT create speculative theories without scientific backing
- Does NOT modify profiles (linking is separate step)
- Does NOT validate clinical correctness (expert review required)
- Does NOT replace clinical supervision (narrative tool only)

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)
- Rule 10: [`docs/rules/10-reference-library-standard.md`](../../rules/10-reference-library-standard.md)

---

## Tiếng Việt

**Tạo các tệp tài liệu tham khảo lý thuyết tâm lý lâm sàn mới** theo lược đồ bắt buộc (song ngữ, được trích dẫn, bối cảnh văn hóa Việt Nam, nghiên cứu trường hợp).

**Khi nào sử dụng:** Khi psy:ref-audit phát hiện ra các lý thuyết bị mất, mô tả hành vi mà không có lý thuyết nào bao gồm, hoặc bằng chứng vật liệu gợi ý một khái niệm lâm sàn mới.
