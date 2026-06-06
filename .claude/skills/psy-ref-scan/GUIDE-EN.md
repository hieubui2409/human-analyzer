# psy:ref-scan — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You created a new reference file on "repetition compulsion" (repeating trauma patterns unconsciously). Now you want to know: Do our character profiles already describe this pattern? If so, which ones should cite this theory? This skill reads the repetition-compulsion.md file, extracts concepts ("repeat past trauma," "unconscious reenactment"), then scans all profiles for those patterns. Output: "Character A ★★★ (directly mentioned), Character C ★★ (behavioral match), Character B ★ (potential fit)." You can then decide where to add explicit citations.

## 2. Core concepts (the mental model)

- **Reverse of psy:ref-audit**: Audit goes profile→ref ("Is this term referenced?"). Scan goes ref→profile ("Where does this theory apply?").
- **Three-star rating**: ★★★ = theory explicitly mentioned in profile. ★★ = behavioral pattern matches theory indicators. ★ = potential fit, needs judgment.
- **Enrichment opportunity**: If Character C shows ★★ match to repetition-compulsion but the profile doesn't cite it, that's an enrichment opportunity: add the citation + explain the pattern.

## 3. Learning path

**Full map:** `psy:ref-scan --map` — see all 60+ theories mapped to all 3 characters.

**One theory:** `psy:ref-scan --theory "attachment theory"` — deep scan for one theory.

**New theories:** `psy:ref-scan --new` — scan theories added in the last commit.

**Unused theories:** `psy:ref-scan --gaps` — which theories have zero profile connections?

## 4. Use cases (each = a sample conversation)

### Use case: New reference application

> You: "Just created parentification.md ref. Where does it apply?"
> Skill: `psy:ref-scan --theory parentification`
> → Character A ★★★ (directly: "took on parental role"), Character C ★★ (behavioral: caring for younger siblings, emotional burden), Character B ★ (potential: family responsibility mentioned). Enrichment suggestion: add parentification citation to Character C's psychology/formulation.md.

### Use case: Full mapping

> You: "I need to understand which theories back which characters."
> Skill: `psy:ref-scan --map`
> → Table: 60+ theories × 3 characters. Shows coverage. Example findings: "Attachment Theory: Character A ★★★, Character B ★★★, Character C ★★" (all 3 covered), vs "Existential-Void: Character C ★★★ only" (niche).

### Use case: Recently added theories

> You: "Last week we added 3 new refs. Where should they be applied?"
> Skill: `psy:ref-scan --new`
> → Scans refs committed in last 7 days. For each: shows character matches. Suggests profile updates.

### Use case: Unused theories

> You: "Are there theories in our library that don't apply to any character?"
> Skill: `psy:ref-scan --gaps`
> → Theories with zero connections: cognitive-dissonance.md, existential-void.md (only Character C at ★ level). Evaluation: archive or keep for future use?

## 5. Important caveats

- **Star rating is heuristic**: ★★★ (direct mention) is objective. ★★ and ★ involve pattern-matching, which can have false positives/negatives. Always review.
- **Behavioral matches are contextual**: A theory might describe behavior that appears in a profile but in a different context than expected. Manual review essential.
- **Recent ref scan depends on git**: `--new` looks at recent commits. Untracked new files might not be scanned. Commit first, then scan.
- **Enrichment is optional**: Just because a theory matches a character doesn't mean the profile MUST cite it. The skill flags opportunities; you decide.
- **Reverse of psy:ref-audit**: If psy:ref-audit says "Clinical term unreferenced," psy:ref-scan says "This reference is applicable here." They're complementary — use both.
