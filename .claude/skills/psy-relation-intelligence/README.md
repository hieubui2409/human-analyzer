# psy:relation-intelligence

> Proactively mine cross-character relationship graph for ranked, evidence-backed, consent-gated publishable content angles.

## What it does

Reads dyad graph (`docs/graph/relational-dynamics.md`) + relationship files + GRO mentoring data. Extracts facts with evidence tiers, scans for Rule-09 confidentiality tags and crisis markers. LLM synthesizes candidate angles (title, hook, supporting facts, coherence score). Script ranks by evidence strength + consent status. Tags each angle with primary_character + consent_status (OPEN/REVIEW/BLOCKED). Hands ranked angles to cre:post-writer.

## When to use

- Content ideation: "What story angles exist between Nhân vật A and Nhân vật B?"
- Proactive discovery: "Mine all dyads for ranked angles"
- Before cre:post-writer: Load top angles into content pipeline
- Trigger phrases: relation intelligence, content angles, mine relationships, dyad angles, relationship content ideas

## Flags

| Flag                  | Effect |
|-----------------------|--------|
| `--dyad <c1> <c2>`    | Specific pair (required) |
| `--all`               | All dyads (Nhân vật A-Nhân vật B, Nhân vật A-Nhân vật C, Nhân vật B-Nhân vật C) |
| `--character <main>`  | Override primary_character hint |
| `--graph-signal`      | Include KG graph signals (if available) |
| `--json`              | Output as JSON |
| `--report`            | Save report to plans/reports/ |

## What it does NOT do

- Does NOT read or leak darkness/traumas.md (trauma detail excluded)
- Does NOT auto-publish (cre:privacy-guard re-checks at draft time)
- Does NOT replace psy:crossref (validation vs discovery)
- Does NOT replace psy:propagate (cascade vs angle mining)

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)
- Verdict cache: [`verdict-cache-contract.md`](../_framework-shared/references/verdict-cache-contract.md)
- Rule 09: [`docs/rules/09-confidentiality-protocol.md`](../../rules/09-confidentiality-protocol.md)

---

## Tiếng Việt

**Khai thác biểu đồ quan hệ qua các nhân vật một cách chủ động** để khám phá các góc độ nội dung có thể xuất bản được xếp hạng, được hỗ trợ bằng bằng chứng, và được gated bởi sự đồng ý.

**Khi nào sử dụng:** Sáng tạo nội dung, khám phá chủ động, hoặc trước khi cre:post-writer.
