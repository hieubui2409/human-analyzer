# psy:ref-create — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

`psy:ref-audit --discover` flags: "Nhân vật A's profile describes 'always sacrificing for others, ignoring own needs' — this is a pattern, but we don't have a theory file for it." You could link to general "savior complex," but the nuance is exhaustion from benevolence. This skill scaffolds a new reference file (`benevolence-fatigue.md`), researches it in DSM-5/ICD-11/literature, writes the mandatory sections (definition, origin, mechanism, Vietnamese context, case study), and integrates it into the library.

## 2. Core concepts (the mental model)

- **Mandatory schema**: Every ref file has 6 sections. No shortcuts. This ensures consistency and prevents half-baked theories.
- **Scientific backing is non-negotiable**: Every theory MUST cite DSM-5, ICD-11, or peer-reviewed literature. No original theories; we're documenting clinical reality, not inventing.
- **Vietnamese cultural context is required**: How does this theory manifest in Vietnamese family dynamics? Cultural factors matter (Nhịn, filial piety, face-saving).
- **Case study ties theory to our project**: Shows how this theory applies to a real character in our corpus.

## 3. Learning path

**Quick scaffold:** `psy:ref-create attachment-trauma --quick` — minimal file, fill in later.

**Full creation:** `psy:ref-create benevolence-fatigue --character hieu` — comprehensive with case study.

**Reverse engineering:** `psy:ref-create --from-behavior "Always helping others, never asking for help, eventual burnout"` — describe behavior, skill proposes theory.

## 4. Use cases (each = a sample conversation)

### Use case: Fill discovered gap

> You: "`psy:ref-audit --discover` found: 'Nhân vật A shows exhaustion from caretaking but no theory covers burnout from benevolence.' Create ref?"
> Skill: `psy:ref-create benevolence-fatigue --character hieu --quick`
> → Scaffolds ref file with definition + mechanism. Marks sections 4–6 (Vietnamese context, case study, etc.) as TODO for later expansion.

### Use case: Reverse-engineer from behavior

> You: "I see a pattern: Nhân vật C avoids commitment because he expects abandonment. What theory is this?"
> Skill: `psy:ref-create --from-behavior "Nhân vật C avoids commitment, expects abandonment, preemptively withdraws"`
> → Searches literature, proposes "fearful-avoidant attachment" (already exists) or suggests new theory if no match. User confirms.

### Use case: Full reference with case study

> You: "We need a full reference on 'sincere misbelief' (believing false narrative one has constructed). Create it."
> Skill: `psy:ref-create sincere-misbelief --character chiến`
> → Creates file with all 6 sections. Definition + Freud/Jung citations. Case study: Nhân vật C's stepmother narrative. Updates INDEX.md. Ready to use.

## 5. Important caveats

- **Requires research**: Don't create empty scaffolds. The skill assumes you'll research the theory (or it will guide you). DSM-5 ISBN, ICD-11 code, author names matter.
- **Vietnamese context is not optional**: Every theory must explain how it shows up in Vietnamese culture. Not "Anglo-centric psychology."
- **Case study should be evidence-backed**: If the ref describes "abandonment trauma," the case study must trace evidence from materials (P{N} priority), not speculation.
- **INDEX.md update is automatic**: The skill updates the reference index. You don't need to do it manually, but verify it's correct.
- **Linking comes later**: Creating a ref doesn't auto-link it to profiles. After creation, manually add `[link](../../references/{theory}.md)` where applicable, then run `psy:ref-scan --theory {name}` to verify coverage.
