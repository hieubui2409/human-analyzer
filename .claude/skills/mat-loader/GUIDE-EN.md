# mat:loader — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You have a stack of new interview transcripts, letters, and news clippings about your characters. Before they can feed psychology analysis or content creation, they need standardized metadata, quality scoring, and classification. mat:loader automates that: you point it at a file, it detects what it is, who it's about, runs a CRAAP quality check, stamps it with evidence tier (T1–T5), and puts it in the right place.

## 2. Core concepts (the mental model)

**Evidence tiers (T1–T5):** Your materials have reliability levels. T1 is the character's own word (highest); T5 is theoretical framework (lowest). The tier determines what claims can fuel psychology work and what can appear in published content.

**CRAAP scoring (1–5 per dimension):** Currency, Relevance, Authority, Accuracy, Purpose. A score of 15/25 is the minimum gate for stage-3 integration; below that, the material is flagged for manual review.

**Processing status (pipeline states):** raw → extracted → analyzed → validated → integrated → archived. mat:loader sets **raw**; subsequent skills move materials downstream. You can see the whole pipeline at a glance with `--status`.

**Domain boundary:** mat:loader never touches profiles or references — only `docs/materials/` exists in its world. Psychology analysis happens downstream.

## 3. Learning path

1. **First run:** `mat:loader --list` — see what you already have. Get a feel for material types and tiers.
2. **Add new material:** `mat:loader --ingest ~/my-new-transcript.md` — walk through a full ingest (detect type, character, date, CRAAP, tier).
3. **Check the pipeline:** `mat:loader --status` — see where materials are bottlenecking (e.g., 5 files stuck at "raw").
4. **Extract facts:** `mat:loader --extract "gambling"` — quick search across all materials for a specific topic.

## 4. Use cases

### Use case: Initial material intake
> **You:** "I have a conversation log with Character C that I transcribed. Please load it."
> 
> **Skill:** Runs `--ingest` on the transcript:
> - Detects type: conversation_log
> - Extracts character: character-c
> - Scans for dates
> - Runs CRAAP test (Currency=4, Relevance=5, Authority=3, Accuracy=4, Purpose=4 → **20/25**)
> - Assigns evidence tier: **T2** (corroborated observation)
> - Injects YAML frontmatter with all fields
> - Moves file to `docs/materials/character-c/` with standardized name
> - Shows you a summary table: type, tier, CRAAP score, next step (mat:indexer)

### Use case: Pipeline status check
> **You:** "What's the state of all our materials right now?"
> 
> **Skill:** Runs `--status`:
> ```
> Status   Count  Files
> raw      5      transcript-jan.md, letter-undated.md, ...
> extracted 12     (files in flight)
> validated 18     (ready for integration)
> integrated 3      (already fed to psychology)
> ```
> You see: 5 files stuck at "raw" — you need to either finish ingesting them or review why they got stuck.

### Use case: Character-specific inventory
> **You:** "Show me all materials for Hoà."
> 
> **Skill:** Runs `--character character-b`:
> - Lists all files with Hoà's character slug
> - Groups by type (conversation_log, letter, news_article, etc.)
> - Shows tier distribution, CRAAP scores, processing status
> - Counts lines, modified date
> - Suggests bottlenecks or coverage gaps

### Use case: Quick fact search
> **You:** "Did we capture anything about Hồ's anxiety symptoms?"
> 
> **Skill:** Runs `--extract "anxiety"` across all materials:
> - Searches text content + frontmatter tags
> - Returns matching lines with source file + evidence tier
> - Helps you see if that claim is already backed by evidence

## 5. Important caveats

**CRAAP is a gate, not a diagnosis.** A low CRAAP score (e.g., 10/25) doesn't mean the material is wrong — it may be a second-hand account or outdated. Depending on your threshold, you may still ingest it; the score flags it for human review.

**Evidence tier is not the same as source quality.** A T1 (character's own statement) can be unreliable if the character is lying or confused. A T2 (corroborated observation) from a therapist is more trustworthy. Tier captures *source type*, not *truth*.

**Processing status is not automatic.** mat:loader sets status to "raw" on ingest. Moving it to "extracted", "analyzed", "validated", or "integrated" requires explicit action (usually LLM judgment after mat:indexer or manual review).

**No integration without mat:indexer.** Loaded materials are inert — they don't feed psychology analysis until they pass Stage 3–4 (mat:indexer). This gate is in place to catch contradictions early (Rule 11).

**Dry runs before you write.** Use `--dry-run` or review preview tables before archiving or batch-updating materials. Once a file is marked archived, it's out of the active pipeline.
