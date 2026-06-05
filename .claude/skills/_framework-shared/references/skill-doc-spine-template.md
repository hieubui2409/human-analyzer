# Skill doc spine — the 4-doc standard per framework skill

Every framework skill (`.claude/skills/{fw}-{skill}/`) ships a **4-doc spine** (cleanmatic standard):

| Doc | Audience | Owns |
|-----|----------|------|
| `SKILL.md` | LLM | the operating CONTRACT (triggers, flags, scripts, events) — **authoritative**, already present |
| `README.md` | human + LLM | who/what, when-to-use, flags, "what it does NOT do", links to SKILL + guides |
| `GUIDE-EN.md` | human | mental model + learning path + per-use-case sample conversation + caveats (English) |
| `GUIDE-VI.md` | human | faithful Vietnamese translation (prose only — IDs/keys/flags stay English) |

**Source of truth:** `SKILL.md`. The guides DESCRIBE; they never re-specify. If a guide claims something the
SKILL.md contract doesn't grant, the guide is wrong (fix the guide). A CI drift check asserts guide claims ⊆
SKILL contract.

**Bilingual rule:** frontmatter keys, skill IDs (`psy:crossref`), flag names, event names stay English always.
Prose + examples localize. Vietnamese must carry full diacritics (never ASCII-fold: "Hồ sơ" not "Ho so").

---

## README.md template

```markdown
# {fw}:{skill}

> One-line purpose (verb-first). Bilingual: English below, Tiếng Việt cuối file.

## What it does
2–4 sentences. The job, the input, the output.

## When to use
- Trigger phrases (from SKILL.md `Triggers:`).
- The workflow position (what runs before / after).

## Flags
| Flag | Effect |
|------|--------|
| `--x` | … |

## What it does NOT do
- Boundary 1 (cite the rule, e.g. Rule 12 / Rule 09).
- Boundary 2.

## See also
- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt
{Vietnamese mirror of What-it-does / When-to-use / NOT-list}
```

## GUIDE-EN.md template

```markdown
# {fw}:{skill} — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you
Plain-language framing (a short scenario).

## 2. Core concepts (the mental model)
The 2–4 ideas that explain WHY it behaves the way it does (e.g. script-gathers / LLM-judges; evidence tiers;
confidentiality gates). Hold these and the rest clicks.

## 3. Learning path
First run → next → as-you-grow. The thin slice that teaches the whole skill.

## 4. Use cases (each = a sample conversation)
### Use case: {name}
> You: "{natural-language ask}"
> Skill: {what it does, which script runs, what it returns}
Repeat per primary flag/intent.

## 5. Important caveats
What it will NOT do; where it over-flags by design; safety gates.
```

## GUIDE-VI.md template
Same structure, Vietnamese prose. IDs/flags/keys English. Native-quality diacritics.

---

## Per-framework ownership (Phase 10 parallel build)
| Framework | Skills | Owner agent |
|-----------|--------|-------------|
| ORC | 17 | agent-orc |
| PSY | 16 | agent-psy |
| CRE | 9 | agent-cre |
| GRO | 8 | agent-gro |
| MAT | 4 | agent-mat |
| COM | 4 | agent-com |

Each agent owns ONLY its framework's skill dirs (`.claude/skills/{fw}-*/`) — strict, non-overlapping.
