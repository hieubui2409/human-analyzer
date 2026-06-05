# psy:profile-compare — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You want to understand the trio: Why do Nhân vật A and Nhân vật B work as a dyad, but Nhân vật C feels like an outsider? You read all three attachment-style files separately, but side-by-side is clearer. This skill pulls attachment-style from all three, renders a table, and shows: Nhân vật A = secure (grounds Nhân vật B), Nhân vật B = anxious (needs grounding), Nhân vật C = fearful-avoidant (pushes and pulls). That pattern explains their dynamics.

## 2. Core concepts (the mental model)

- **One dimension, all characters**: You pick a section (core-wounds, defense-mechanisms, etc.), the skill extracts it from all targets, and renders them side-by-side so you see patterns, contrasts, overlaps.
- **Table-based output**: Markdown table with key findings per row. Clean, scannable, easy to reference in content planning.
- **Dimension discovery**: Available dimensions map to actual files (`defense-mechanisms` → `psychology/defense-mechanisms.md`; `relationships/hieu` → `relationships/hieu.md`).

## 3. Learning path

**First run:** `psy:profile-compare --dimension defense-mechanisms` — see all three, spot patterns.

**Specific pair:** `psy:profile-compare --dimension attachment-style --characters hieu,hoa` — narrow focus.

**Complex dimension:** `psy:profile-compare --dimension formulation --characters hieu,hoa,chien` — deepest psychological patterns.

## 4. Use cases (each = a sample conversation)

### Use case: Dyadic pattern analysis

> You: "Why do Nhân vật A and Nhân vật B's relationship work, but Nhân vật C feels left out?"
> Skill: `psy:profile-compare --dimension attachment-style`
> → Table shows: Nhân vật A (secure), Nhân vật B (anxious-preoccupied), Nhân vật C (fearful-avoidant). Insight: secure + anxious often stabilize; fearful-avoidant = unpredictable. Suggests: Nhân vật C's fear of abandonment triggers when he feels excluded.

### Use case: Defense mechanism contrast

> You: "How do they cope with stress differently?"
> Skill: `psy:profile-compare --dimension defense-mechanisms --characters hieu,hoa,chien`
> → Nhân vật A: sublimation, humor, caretaking. Nhân vật B: projection, rationalization. Nhân vật C: dissociation, self-blame. Output: table + insight on why conflicts escalate (misunderstanding each other's coping).

### Use case: Relationship file comparison

> You: "How does each character perceive their relationship with Nhân vật A?"
> Skill: `psy:profile-compare --dimension relationships/hieu`
> → Pulls `relationships/hieu.md` from Nhân vật B and Nhân vật C's profiles. Compares how each describes the relationship. Highlights concordances and discordances.

## 5. Important caveats

- **Thin files = thin comparison**: If a dimension file is sparse (10 lines), the comparison will be summary. Run psy:health-check first to gauge file richness.
- **Cross-character relationship files are discovered dynamically**: If you ask for `relationships/hieu`, the skill finds it in other characters' directories automatically.
- **Not a consistency check**: This is observational (what are the differences?) not validational (is this consistent?). For validation, use psy:crossref.
- **JSON output is machine-friendly**: If you're piping to other tools, use `--json` for structured output.
