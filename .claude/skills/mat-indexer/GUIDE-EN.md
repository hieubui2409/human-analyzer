# mat:indexer — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You've loaded a stack of materials — transcripts, letters, observations. Before they can shape your character profiles, you need to know: Does this material contradict what's already in the profile? Does it support existing claims or add new details? Are there gaps in what the profile says that this material could fill? mat:indexer answers all three questions at once: it finds contradictions (and how serious they are), maps evidence coverage across the profile, and flags materials that have been sitting in the pipeline too long.

## 2. Core concepts (the mental model)

**The integration gate:** Loaded materials don't automatically feed analysis. Stage 3 (mat:indexer scripts) gathers contradictions and coverage data; Stage 4 (LLM judgment) decides whether each material is safe to integrate. If contradictions are minor or resolved, the material moves to "integrated" and the event `MAT.integrated` fires, triggering PSY analysis. If contradictions are high-severity, the material is flagged for human review instead.

**Contradiction severity:** Not all conflicts are equal. A date off by a few days is LOW. A description of an event disagreeing with the profile is MEDIUM. A safety-critical claim (e.g., suicidal ideation level mismatch) is CRITICAL and stops the gate entirely.

**Coverage vs. gaps:** Profiles have 21 standard sections per character. Some sections (e.g., psychology/formulation) may have 10+ materials backing them; others (e.g., light/strengths-hope) may have zero. Gaps don't mean your profile is wrong — they flag where you need more evidence if you want higher confidence.

**Processing status moves forward:** After Stage 3 validation, LLM updates `processing_status` from "raw" or "extracted" to either "validated" (pass gate) or stays at "analyzed" (needs human review). Only "validated" materials can become "integrated."

## 3. Learning path

1. **First run:** `mat:indexer --all` — do a full cross-reference. Look at the contradiction table (sorted by severity) and the coverage matrix.
2. **Understand your gaps:** `mat:indexer --coverage` — see which profile sections are under-evidenced.
3. **Find pain points:** `mat:indexer --contradictions` — see if any materials are conflicting with the profile.
4. **Check for stale materials:** `mat:indexer --stale` — find materials stuck in the pipeline and decide whether to finish them or archive.
5. **Single character:** `mat:indexer --character <name>` — zoom in on one person's material vs. profile.

## 4. Use cases

### Use case: First validation after bulk load
> **You:** "I just loaded 30 materials for all three characters. Are there any contradictions?"
> 
> **Skill:** Runs `--all`:
> - Scans all materials for factual claims (events, relationships, emotional states)
> - Compares each claim to the corresponding profile section
> - Returns contradiction table:
>   ```
>   # | Material | Claims | Profile Says | Severity | File
>   1 | letter-01 | "Nhân vật A anxious Jan 2024" | "anxiety emerged Jun 2024" | MEDIUM | ...
>   2 | news-02 | "crisis hospitalization" | "no psychiatric admission" | CRITICAL | ...
>   ```
> - You see: 1 CRITICAL (stop — needs immediate review), 2 MEDIUM (flag for human judgment)

### Use case: Coverage map for a character
> **You:** "What evidence do we have for Nhân vật C's profile? Where are the gaps?"
> 
> **Skill:** Runs `--character chien --coverage`:
> - Lists all 21 profile sections
> - For each, counts how many materials reference it + what tiers
>   ```
>   | Profile Section | Materials Supporting | Tier | Gap? |
>   | psychology/formulation | 5 files (T1×2, T2×3) | Strong | No |
>   | light/strengths-hope | 0 files | — | YES |
>   ```
> - You see: strengths/hope section has zero evidence. You may want to add interviews or conversations that show resilience.

### Use case: Stale material cleanup
> **You:** "I have some materials that have been in 'raw' for weeks. What do I do?"
> 
> **Skill:** Runs `--stale`:
> - Finds all materials with `processing_status: raw` or `extracted` older than 7 days
> - Shows file, status, how long stuck
> - Suggests: re-run `mat:loader --ingest` to finish them, or use `mat:archive` to remove them
> - Helps you declutter the pipeline

### Use case: Contradiction deep-dive
> **You:** "Just contradictions — no coverage analysis, I'm in a hurry."
> 
> **Skill:** Runs `--contradictions` only:
> - Fast output: only the contradiction table
> - Sorted by severity (CRITICAL first)
> - Saves time if you just need to triage conflicts

## 5. Important caveats

**Contradiction doesn't mean error.** If material says "Nhân vật A was anxious in January" and profile says "anxiety emerged in June," that's a genuine contradiction. But maybe the profile is incomplete (anxiety was latent), or the material is misremembered, or both are true (different types of anxiety). The contradiction is flagged; the LLM decides what it means.

**Coverage gaps are information, not problems.** Some profile sections are inherently harder to evidence. Strengths (light/strengths-hope.md) may have fewer materials than traumas. That's okay — it doesn't invalidate your profile, just signals where you might want more input.

**LLM judges integration, not the script.** mat:indexer scripts gather contradictions and coverage; they don't emit events. Only the LLM, after reviewing the output, decides whether a material is "validated" (passes Stage 4) and whether to emit `MAT.integrated` or flag it for human review.

**Stale doesn't mean bad.** A material stuck at "raw" for 2 months might be perfectly good — you just haven't finished ingesting it. The `--stale` flag is a nudge to either finish it or archive it, not a condemnation.

**Never modify profiles from mat:indexer.** If a contradiction is real, the profile is likely incomplete or wrong. But mat:indexer never writes to profiles — you review the flag, then update the profile separately via PSY domain skills.
