# orc:skill-stocktake — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

Over time, skills accumulate. Some overlap. Some become obsolete. Stocktake audits the catalog: counts per framework, detects overlaps (e.g., two skills that do the same thing), identifies gaps (missing functionality), and assigns verdicts (KEEP this, CONSOLIDATE those, RETIRE that). It's maintenance for the skill system itself.

## 2. Core concepts (the mental model)

**Three audit layers:** Quick Scan (counts + metadata), Full Stocktake (overlap/gaps + LLM verdict), Conformance (code quality + structure).

**Verdicts are advisory.** CONSOLIDATE or RETIRE are recommendations, never auto-executed. You decide.

**New-skill guard.** Skills < 3 commits old are tagged NEW. "No usage" doesn't mean "unused" for new skills; only overlap signals matter.

## 3. Learning path

**First run:** `orc:skill-stocktake --quick` — see skill counts and metadata gaps.

**Deep audit:** `orc:skill-stocktake --full` — overlap/gap analysis + LLM verdicts.

**Conformance check:** `orc:skill-stocktake --conformance` — code size, structure, reference quality.

**Filter by framework:** `orc:skill-stocktake --full --framework orc` — just ORC skills.

## 4. Use cases (each = a sample conversation)

### Use case: Quick catalog health check

> You: "Quick scan the skill catalog for drift."
>
> Skill: Counts: ORC 17, PSY 16, CRE 9, GRO 8, MAT 4, COM 4 (matches CLAUDE.md). Reports: 2 missing `description` frontmatter, 1 orphan reference. You know: catalog is in sync, minor metadata gaps to fix.

### Use case: Full stocktake for overlap detection

> You: "Are any ORC skills duplicates?"
>
> Skill: Analyzes: `orc:domain-router` and `orc:cascade` both handle event routing. Verdict: KEEP both (complementary: router = from-diff detection, cascade = explicit event tracing). You confirm: no consolidation needed.

### Use case: Conformance check before release

> You: "Check skill conformance before shipping."
>
> Skill: Scans all skills: orc-bootstrap is 340 lines (WARN: 200-line threshold), orc-council has nested references (FAIL: split needed). Reports conformance status per skill. You know what to fix before release.

## 5. Important caveats

- **Overlap ≠ duplication.** Skills with similar names may be complementary. LLM verdict is the judgment call.
- **Auto-mode has limits.** Script over-gathers candidate overlaps; LLM filters false positives.
- **New-skill exception.** Skills < 3 commits old are never retired for "no usage."
- **Conformance is advisory.** ENHANCE recommendations are improvements, not blockers.
