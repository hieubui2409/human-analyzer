# psy:ref-maintain — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

Over time, you create reference files. Some get used heavily (attachment-theory cited in Nhân vật A + Nhân vật B + Nhân vật C profiles). Others end up unused (you created dissociation.md once, but it doesn't appear in any character's psychology files). This skill scans the entire reference library, counts citations per theory, and tells you: "These 5 theories are orphaned (zero citations). Are they truly not applicable, or should we link them? These 3 theories are in INDEX.md but their files don't exist." It's a health check to keep the library in good shape.

## 2. Core concepts (the mental model)

- **Citation counting**: For each ref file, the skill scans all profile files looking for the theory name. If found N times → cited. If found 0 times → orphan.
- **Index consistency**: Is every theory in `docs/references/INDEX.md` actually present as a file? Reverse: do all ref files appear in INDEX.md?
- **Schema compliance**: Each ref file should have mandatory sections (definition, origin, mechanism, Vietnamese context, case study, citations). Missing sections = schema breach.
- **Coverage gaps**: Should all 3 characters reference at least one theory per category (defense, attachment, trauma)? If Nhân vật C lacks "trauma theory," flag it.

## 3. Learning path

**Full health check:** `psy:ref-maintain` — see the complete audit.

**Orphans only:** `psy:ref-maintain --orphans-only` — focus on unused theories.

**Gaps only:** `psy:ref-maintain --gaps-only` — see which characters need more theory coverage.

**JSON for tooling:** `psy:ref-maintain --json` — parse for automated cleanup workflows.

## 4. Use cases (each = a sample conversation)

### Use case: Periodic library audit

> You: "It's been 3 months since we added theories. Is the library healthy?"
> Skill: `psy:ref-maintain`
> → Total theories: 62. Active (3+ citations): 42. Used (1-2 citations): 15. Orphans: 5. Index gaps: 2 theories missing from INDEX.md. Schema breaches: 3 files missing Vietnamese context section. Recommendations: link orphans if applicable, archive if not, fix INDEX.md, complete schema for 3 files.

### Use case: Find orphaned theories

> You: "Which theories did we create but never used?"
> Skill: `psy:ref-maintain --orphans-only`
> → cognitive-dissonance.md (0 citations), existential-void.md (0), learned-helplessness.md (0), role-confusion.md (0), shame-based-identity.md (0). Recommendations: Review each. Some may be niche (applicable to Nhân vật C only if profile is updated). Some should be archived.

### Use case: Coverage gaps (before validation)

> You: "Before running psy:crossref, do we have sufficient theory coverage?"
> Skill: `psy:ref-maintain --gaps-only`
> → Nhân vật A: Defense mechanisms ✓, Attachment ✓, Trauma ✓, Big Five ✗. Nhân vật B: All covered ✓. Nhân vật C: Defense mechanisms ✗, Trauma ✓, Attachment ✓. Recommendations: Add Big Five ref for Nhân vật A, defense mechanisms ref for Nhân vật C.

## 5. Important caveats

- **Orphans don't always mean delete**: A theory may be niche, applicable only if a character changes. Instead of deleting, tag it or note why it exists.
- **INDEX.md manually maintained**: The skill audits it but doesn't auto-fix. You review and manually add missing entries.
- **Citation counting is exact-match only**: If a theory is mentioned indirectly ("similar to attachment theory") it might not count. Manual review recommended for borderline cases.
- **Schema breaches need human judgment**: If a file is missing the Vietnamese cultural context section, it's flagged, but you decide if it's truly missing or just needs expansion.
- **Coverage gaps are guidance, not law**: A character might not need explicit "Big Five" reference if psychological formulation covers personality implicitly. Flag is informational.
