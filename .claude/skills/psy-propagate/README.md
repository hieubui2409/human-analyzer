# psy:propagate

> Cross-character cascade analysis — when a profile section changes, detect which connected characters need review.

## What it does

After updating one character's profile, reads the knowledge graph (`docs/graph/relational-dynamics.md`) to find all connected characters. Maps changed section (e.g., relationships/family.md) to affected sections in neighbors (e.g., relationships/{char}.md, timeline/overview.md). Outputs prioritized targets for review + recommended actions. Reuses verdict cache inheritance (downstream cost optimization, never safety decision).

## When to use

- Just updated Nhân vật A's profile: "Which other files need sync?"
- Changed relationship dynamics: "Who else is affected?"
- Cascading updates across dyads: Track dependencies before manual updates

## Flags

| Flag                  | Effect |
|----------------------|--------|
| `--character <name>` | Source character (required) |
| `--section <section>` | Specific section (optional) |
| `--json`              | Output as JSON |

## What it does NOT do

- Does NOT modify profiles (read-only detection only)
- Does NOT force updates (recommends, user decides)
- Does NOT validate consistency (that's psy:crossref)
- Does NOT replace manual cross-checks (detection aid only)

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)
- Verdict cache: [`verdict-cache-contract.md`](../_framework-shared/references/verdict-cache-contract.md)

---

## Tiếng Việt

**Phân tích xếp tầng qua các nhân vật** — khi một phần hồ sơ thay đổi, phát hiện các nhân vật được kết nối nào cần xem xét.

**Khi nào sử dụng:** Sau khi cập nhật hồ sơ, thay đổi động lực quan hệ, hoặc cập nhật xếp tầng qua các dyad.
