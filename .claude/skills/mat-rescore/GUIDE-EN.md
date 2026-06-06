# mat:rescore — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

When you load materials into the MAT pipeline, each one gets a CRAAP score (Currency, Relevance, Authority, Accuracy, Purpose). But files get loaded in a hurry, and some might have missing fields, partial scores, or math errors (e.g., total = 5+4+3+2+1 = 15, but the frontmatter says 14). mat:rescore audits all your materials and surfaces ones that need fixing. It doesn't fix them—you decide which ones to re-run through `mat:loader --ingest` to get fresh scores.

## 2. Core concepts (the mental model)

**CRAAP is a quality gate, not a label.** A score below 15/25 can still be useful evidence; it just means the material is borderline quality and requires more review. Rescore identifies which materials are missing scores entirely or have incomplete ones—the audit itself is neutral.

**Rescore triggers (when to rescore):**
- File has no `craap_score` key at all (never scored).
- One or more fields (currency, relevance, authority, accuracy, purpose) is null or missing.
- The `total` field doesn't match the sum of individual fields (math error).
- File is still at `processing_status: raw` (never moved past ingestion).
- File has no YAML frontmatter at all (not MAT-compliant).

**Script gathers; you judge.** mat:rescore's job is pure audit: find and list. It doesn't recommend archiving, doesn't rate quality, doesn't decide integration. It just says "these N files need scores." You then decide whether to re-ingest them, leave them as-is (if you accept the risk), or archive them.

**Character-scoped audit:** By default, mat:rescore checks all characters. You can narrow it to one with `--character <name>` if you're doing targeted cleanup.

## 3. Learning path

1. **Full audit:** `mat:rescore` — see all materials needing rescore across all characters.
2. **See the summary:** Scan the "Materials Needing Rescore" table and "Summary by Character" breakdowns.
3. **Narrow by character:** `mat:rescore --character character-a` — just Character A's issues.
4. **Focus on critical gaps:** `mat:rescore --missing-only` — only files with zero CRAAP at all (highest priority).
5. **Focus on raw status:** `mat:rescore --raw-only` — only files stuck at "raw" (never processed).
6. **Act:** For flagged files, run `mat:loader --ingest <file>` to re-score them.

## 4. Use cases

### Use case: Initial audit after batch load
> **You:** "I just loaded 50 materials. Are they all scored correctly?"
> 
> **Skill:** `mat:rescore`:
> ```
> Materials Needing Rescore
> | File | Character | Reason | Current Status | Current Score |
> | transcript-jan.md | hieu | missing craap_score | raw | — |
> | letter-old.md | hoa | partial (authority=null) | extracted | 12/25 |
> | interview-2025.md | chien | total ≠ sum (says 20, is 19) | validated | 20/25 |
> Total: 12 materials need rescore
> ```
> You see: 12 files with issues. 1 is completely missing a score, 1 has a partial score, 1 has a math error.

### Use case: Summary by character
> **You:** "Which character's materials are least complete?"
> 
> **Skill:** `mat:rescore` produces a summary:
> ```
> | Character | Total | Needs Rescore | % Clean |
> | hieu | 20 | 3 | 85% |
> | hoa | 18 | 8 | 56% |
> | chien | 25 | 1 | 96% |
> ```
> You see: Hoà's materials are only 56% clean. You might prioritize rescoring Hoà's files.

### Use case: Find critical gaps
> **You:** "Show me only the materials that were never scored at all."
> 
> **Skill:** `mat:rescore --missing-only`:
> ```
> | File | Character | Reason | Status |
> | transcript-undated.md | hieu | missing craap_score | raw |
> | conversation-log.md | hoa | missing craap_score | extracted |
> Total: 2 materials have zero CRAAP
> ```
> You see: 2 files with complete scoring gaps. These are highest priority because there's no quality info at all.

### Use case: Clean up raw materials
> **You:** "I have old materials stuck at 'raw' status. Do they have complete CRAAP scores?"
> 
> **Skill:** `mat:rescore --raw-only`:
> - Lists all materials with `processing_status: raw`
> - Flags which ones have incomplete or missing CRAAP
> - Suggests: either finish rescoring them with `mat:loader --ingest`, or use `mat:archive --status raw` to remove them

### Use case: JSON export for tooling
> **You:** "I want to integrate rescore results into a custom dashboard. JSON please."
> 
> **Skill:** `mat:rescore --json`:
> ```json
> {
>   "materials_needing_rescore": [
>     {
>       "file": "transcript-jan.md",
>       "character": "hieu",
>       "reason": "missing craap_score",
>       "current_status": "raw",
>       "current_score": null
>     }
>   ],
>   "summary_by_character": [ ... ]
> }
> ```
> You pipe this to your own scripts.

## 5. Important caveats

**Rescore flags work, not failure.** A file needing rescore isn't broken—it just needs attention. Some cases are trivial (math error in the total field); others require re-reading the material and re-running CRAAP. Not all flagged files need immediate action.

**Missing score ≠ bad material.** If a file has no CRAAP score, it might be brand new (not yet scored) or uploaded before the scoring system was mandatory. It's not automatically low-quality; it just hasn't been evaluated formally. You decide whether to score it, leave it unscored, or archive it.

**Partial scores are salvageable.** If a file has 4 of 5 CRAAP fields but is missing "authority," you can often re-ingest it with `mat:loader --ingest` to fill in the gap, rather than treating the file as unusable.

**Rescore is non-destructive.** Running `mat:rescore` never changes your materials. It's pure reporting. Even if you see 30 files flagged, you can ignore them and keep working—no automatic consequences.

**Rescore doesn't replace human judgment.** Some materials might have low CRAAP scores but be incredibly valuable for context. Others might have high scores but turn out to be unreliable. Scores are an audit tool, not the final word.
