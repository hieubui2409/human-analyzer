# psy:ref-audit

> Audit clinical psychology references bidirectionally: profile→ref accuracy, ref→ref cross-linkage, discover missing theories. Scripts gather, LLM judges clinical relevance.

## What it does

Scans profiles for clinical terms, compares against reference library, flags unreferenced terms, misapplied concepts, and implicit psychology patterns. Reverse-scans: finds theories mentioned in profiles but missing from refs. Ref-to-ref scan: finds theories mentioned inside ref files that lack their own file. Outputs detailed audit with recommendations.

## When to use

- After profile updates: "Are clinical terms properly referenced?"
- Periodically: "What psychological concepts are in profiles but not in our ref library?"
- Trigger phrases: audit refs, check clinical accuracy, ref audit, psychology check, validate references, missing theories

## Flags

| Flag                 | Effect |
|----------------------|--------|
| `--all`              | Audit all characters (default) |
| `--character <name>` | Audit one character |
| `--deep`             | Add behavioral cluster scan alongside terms |
| `--term <term>`      | Search specific term across all profiles |
| `--discover`         | Bidirectional blind-spot detection |
| `--cross-ref`        | Inter-reference linkage audit only |
| `--report`           | Save report to plans/reports/ |

## What it does NOT do

- Does NOT modify profiles or references (read-only audit)
- Does NOT guarantee clinical accuracy (human judgment required)
- Does NOT replace psy:ref-scan (that goes ref→profile; this is profile→ref)
- Does NOT create references (recommend psy:ref-create for gaps)

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

**Kiểm tra tài liệu tham khảo tâm lý lâm sàn hai chiều** — độ chính xác profile→ref, liên kết chéo ref→ref, khám phá các lý thuyết bị mất.

**Khi nào sử dụng:** Sau khi cập nhật hồ sơ, định kỳ, khi thêm tài liệu tham khảo mới.
