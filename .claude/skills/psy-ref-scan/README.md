# psy:ref-scan

> Reference-to-profile mapping — start from clinical theories and find where they apply in character profiles. Discovers enrichment opportunities.

## What it does

Reads reference library (`docs/references/`), extracts key concepts from each theory, then scans all character profiles looking for behavioral indicators matching those concepts. Outputs theory-to-profile mapping table showing relevance per character (★★★ direct, ★★ behavioral match, ★ potential). Identifies enrichment gaps: "Theory X is relevant to Character Y but not cited in their profile yet."

## When to use

- After adding new references: "Where should this theory apply in the profiles?"
- Coverage mapping: "Which theories are missing from our profiles?"
- Content ideation: "What psychology theories back this character's behavior?"
- Trigger phrases: scan refs, where does this theory apply, reference scan, theory mapping, enrich profiles

## Flags

| Flag              | Effect |
|-------------------|--------|
| `--map`           | Full theory-profile mapping (default) |
| `--theory <name>` | One theory across all profiles |
| `--new`           | Scan recently added references |
| `--gaps`          | Theories with zero profile connections |

## What it does NOT do

- Does NOT modify profiles (read-only discovery only)
- Does NOT validate clinical accuracy (that's psy:ref-audit)
- Does NOT create new theories (that's psy:ref-create)
- Does NOT measure profile quality (that's psy:health-check)

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

**Ánh xạ tham chiếu-để-hồ sơ** — bắt đầu từ các lý thuyết lâm sàn và tìm nơi chúng áp dụng trong các hồ sơ nhân vật.

**Khi nào sử dụng:** Sau khi thêm tài liệu tham khảo mới, ánh xạ phạm vi, hoặc khám phá nơi các lý thuyết nên áp dụng.
