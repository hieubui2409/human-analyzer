# psy:crossref

> Cross-character consistency validation — detect timeline conflicts, relationship mismatches, contradictory facts, and validate 10 dimensions (4 automated, 6 LLM-judged).

## What it does

Scans 2+ character profiles for inconsistencies: timeline conflicts, relationship mismatches, contradictory facts, missing cross-references, evidential backing, developmental plausibility, cultural consistency, systemic balance, narrative coherence, and linguistic voice. Validates 10 dimensions (4 core automated scripts, 6 extended LLM judgment). Reuses verdict cache to skip re-judging unchanged profile sections.

## When to use

- After profile updates: "Did I break consistency elsewhere?"
- Periodically: "Are all 3 characters internally aligned?"
- Trigger phrases: cross-reference, crossref, consistency check, validate profiles, check consistency, profile validation

## Flags

| Flag                     | Effect |
|--------------------------|--------|
| `--all`                  | Validate all character pairs (default) |
| `--pair <c1> <c2>`       | Specific pair only |
| `--timeline`             | Timeline checks only |
| `--relationships`        | Relationship checks only |
| `--extended`             | Include all 10 dimensions (default: 4 core) |
| `--dimension <1-10>`     | Run single dimension |
| `--report`               | Save formal report to plans/reports/ |
| `--fresh`                | Bypass verdict cache; re-judge all dimensions |

## What it does NOT do

- Does NOT modify profiles (read-only) — only reports findings
- Does NOT auto-fix inconsistencies (Rule 08 requires human judgment)
- Does NOT skip validation — crisis/narrative-twist verdicts always re-run (never cached)
- Does NOT collapse ambiguities; surfaces contradictions for human review

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

**Xác thực tính nhất quán qua các nhân vật** — phát hiện các xung đột về thời gian, sự không phù hợp của mối quan hệ, những sự kiện mâu thuẫn, và xác thực 10 chiều (4 tự động, 6 đánh giá bởi LLM).

**Khi nào sử dụng:** Sau khi cập nhật hồ sơ, kiểm tra định kỳ, xác thực giữa các nhân vật với nhau.
