# psy:ref-audit — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You've written: "Character A shows parentification patterns" and "Character C exhibits anxious attachment." Are those clinical terms properly backed by reference files? Does `docs/references/parentification.md` exist? Does `docs/references/anxious-attachment.md`? This skill scans the profiles for clinical terms (script gathers candidates), then judges whether each term is accurate, referenced, misapplied, or implicit. It also finds the reverse: psychology concepts mentioned in profile descriptions without formal names — e.g., "Character A luôn cố gắng cứu mọi người" implicitly describes savior complex. And it audits the reference library itself: are all mentioned theories actually documented?

## 2. Core concepts (the mental model)

- **Scripts gather, LLM judges**: The script finds term candidates in profiles (regex + keyword search). The LLM reads context and decides: is this term used clinically or casually? Is it accurate? Does a reference back it?
- **Five classification tiers**: ACCURATE (term correct + ref exists), UNREFERENCED (term correct, no ref), MISAPPLIED (term wrong context), INFORMAL (colloquial, OK), IMPLICIT (describes concept without formal name).
- **Bidirectional**: Profile→ref (do concepts in profiles have backing?), Ref→profile (do theories in the ref library apply to any character?), Ref→ref (are all mentioned theories documented?).

## 3. Learning path

**First run:** `psy:ref-audit --character character-a` — see what terms Character A's profile uses.

**Full audit:** `psy:ref-audit --all` — all characters, all directions.

**Discover blind spots:** `psy:ref-audit --discover` — find missing theories everywhere.

**Cross-ref linkage:** `psy:ref-audit --cross-ref` — audit reference library internal links only.

## 4. Use cases (each = a sample conversation)

### Use case: Post-profile-update audit

> You: "I just updated psychology/formulation.md for Character C. Are the clinical terms properly backed?"
> Skill: `psy:ref-audit --character character-c`
> → Finds: "complex-PTSD" (ACCURATE, ref exists), "repetition compulsion" (IMPLICIT — profile describes it but doesn't name it, ref exists), "learned helplessness" (UNREFERENCED — term used, no ref file). Recommendations: link repetition-compulsion explicitly, create learned-helplessness ref or rephrase.

### Use case: Periodic library health

> You: "What psychology concepts are floating around in our profiles but aren't in the reference library?"
> Skill: `psy:ref-audit --discover`
> → Finds implicit concepts: "identity fusion" (described in Character C's profile, no ref), "benevolence fatigue" (in Character A's profile, no ref). Recommends: create refs or add to existing theory files.

### Use case: Reference library audit

> You: "Our references mention 'co-dependency' a lot. Is there a co-dependency.md file?"
> Skill: `psy:ref-audit --cross-ref`
> → Ref→ref scan: "co-dependency" mentioned in savior-complex.md (3x), parentification.md (2x), but no co-dependency.md file. Recommend: create ref or consolidate into existing.

## 5. Important caveats

- **Implicit detection is heuristic**: The skill can flag "Character A always rescues people" as implicitly describing savior complex, but false positives happen. LLM reads context; human confirms.
- **Colloquial vs clinical is a judgment call**: "Attachment to his hometown" is casual; "anxious attachment pattern" is clinical. The LLM makes the call, but you can override.
- **Not a clinical correctness checker**: This audits reference usage, not whether a diagnosis is correct. If a profile claims someone has "ADHD" but the reference says something different, psy:ref-audit flags it as MISAPPLIED, but the fix requires expert judgment.
- **Deep mode adds behavioral scan**: `--deep` finds theories described as behavior patterns (e.g., "always gives in to others" → anxious attachment indicator). Adds complexity; use when you suspect implicit concepts.
