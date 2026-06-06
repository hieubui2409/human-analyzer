# orc:dream — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

Over weeks, memory accumulates. You notice "Character B avoids under pressure" and separately "Character B deflects with humor"—both true, but scattered. Dream consolidates: merges related insights, removes stale ones (outdated info), strengthens high-confidence patterns, and promotes them into agent memory so domain agents use them. It's maintenance that keeps your learning system sharp.

## 2. Core concepts (the mental model)

**Five consolidation phases:** Scan (inventory), Merge (combine related), Prune (remove stale), Strengthen (fill gaps), Instincts (lifecycle: decay, archive, cluster, promote).

**Memory has signal and noise.** Good instincts (reinforced 3+ times, conf ≥0.80) become agent memory. Weak instincts (1-2 evidence, conf <0.4, 30+ days) get archived. Dream automates this triage.

**Clusters surface hidden patterns.** When instincts cluster (e.g., 4 instincts about Character B's avoidance), dream suggests a core pattern worth documenting explicitly.

## 3. Learning path

**First run:** `orc:dream --scan` — check memory health. How many memories? How old? Any broken links?

**Light cleanup:** `orc:dream --merge` — find and merge overlapping memories.

**Heavy maintenance:** `orc:dream --full` — all phases including instinct lifecycle (decay, archive, promote).

**Instinct focus:** `orc:dream --instincts` — just handle instinct lifecycle, skip memory phases.

## 4. Use cases (each = a sample conversation)

### Use case: Check memory health

> You: "Is our memory system healthy?"
>
> Skill: Runs --scan, reports: 47 memories, oldest from 60 days ago, 3 broken links (theories mentioned but files deleted). You know: memory is getting large, has stale entries, and has inconsistencies to fix.

### Use case: Consolidate overlapping learnings

> You: "Memories feel repetitive. Merge overlapping ones."
>
> Skill: Finds: "character-b-attachment-pattern" + "character-b-avoidance-triggers" both describe Character B's attachment. Proposes merge into "character-b-attachment-avoidance-dynamics". You confirm. Dream merges and updates MEMORY.md index.

### Use case: Full consolidation with instinct promotion

> You: "Full dream maintenance. Clean everything up."
>
> Skill: Scans, merges, prunes stale memories (2+ months old), then runs instinct lifecycle: decays low-confidence instincts, archives very stale ones, clusters active ones, promotes 3 high-confidence instincts to agent memory. Reports summary: merged 5 memories, archived 2, promoted 3 instincts.

## 5. Important caveats

- **Dream proposes; you approve.** It never auto-deletes. You see before/after for every merge and prune.
- **Instinct decay is mathematical.** Confidence gradually declines unless reinforced. If you see a good instinct decaying, reinforce it.
- **Clustering is heuristic.** If clustering finds false patterns (word-overlap but unrelated instincts), ignore the suggestion.
- **Promotion doesn't auto-execute.** Dream suggests promoting instincts to agent memory; you still have to approve and the LLM writes the update.
