# mat:archive — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

Over time, your materials directory fills up. Some files are old, confidential, or low-quality. Rather than accumulating clutter, you want to mark them as archived—out of the active pipeline, but still auditable because files are never deleted. mat:archive lets you apply smart filters (old dates, low tiers, specific characters, stalled status) and bulk-mark matching files. You always get a dry-run preview first, so you never accidentally archive the wrong thing.

## 2. Core concepts (the mental model)

**Archived is not deleted.** When you archive a material, its `processing_status` becomes "archived"—it's marked as inactive, but the file stays in `docs/materials/` forever. This maintains an audit trail: you can see what existed when and why it was archived.

**Filters are AND logic.** If you say `--character hieu --before-date 2024-12-31 --tier T5`, the script finds files where ALL three conditions are true: Nhân vật A's materials, from before 2024-12-31, AND tier T5. It doesn't match Nhân vật A's T1 files from 2025, or pre-2024 T3 files from other characters.

**Dry-run is default.** Every archive command defaults to `--dry-run`, showing you what would be archived without actually changing anything. To make changes real, you must explicitly remove `--dry-run` from your command (or it's implied if you explicitly write without that flag after reviewing the preview).

**You control the threshold.** mat:archive doesn't decide what to archive; you do. It just applies your filters. You might archive old materials to reduce noise, or confidential ones to prevent accidental exposure, or low-CRAAP items to focus on high-quality evidence.

## 3. Learning path

1. **First run:** `mat:archive` with no filters — see all materials that could theoretically be archived (dry-run mode only).
2. **Filter by character:** `mat:archive --character hieu --dry-run` — what would happen if you archived only Nhân vật A's materials?
3. **Filter by age:** `mat:archive --before-date 2024-06-01 --dry-run` — archive pre-June 2024 materials (old stuff).
4. **Combine filters:** `mat:archive --character hoa --tier T5 --dry-run` — Hoà's low-tier materials only.
5. **Execute:** Once you trust the preview, drop `--dry-run` to actually archive.

## 4. Use cases

### Use case: Clean up old raw files
> **You:** "I have transcripts from 2024 that I never finished ingesting. They're taking up mental space. Let's archive them."
> 
> **Skill:** `mat:archive --before-date 2024-12-31 --status raw --dry-run`:
> ```
> Archive Preview
> | File | Character | Tier | Status | Date |
> | transcript-2024-01.md | hieu | T3 | raw | 2024-01-10 |
> | letter-2024-03.md | hoa | T5 | raw | 2024-03-15 |
> Total: 5 files would be archived
> ```
> You review the list, it looks good, then you run the same command **without** `--dry-run`:
> - All 5 files now have `processing_status: archived` in their frontmatter
> - They disappear from active pipeline lists (like `mat:loader --status`)
> - They're still there if you need to un-archive later

### Use case: Archive low-confidence materials
> **You:** "We have a lot of T5 (theoretical) materials. We should focus on T1–T3 evidence. Archive all the T5 stuff."
> 
> **Skill:** `mat:archive --tier T5 --dry-run`:
> - Lists all materials assigned tier T5 across all characters
> - Shows count: e.g., 12 files would be archived
> - You confirm, drop `--dry-run`, done

### Use case: Character-specific archival
> **You:** "Hoà's profile is complete. I don't need to add more evidence for her. Archive all her validated materials to clean the workspace."
> 
> **Skill:** `mat:archive --character hoa --status validated --dry-run`:
> - Shows all of Hoà's materials that are "validated" (completed Stage 4)
> - You see: 18 files
> - Once archived, they still exist but won't clutter `mat:loader --list` output

### Use case: Confidentiality cleanup (if tagging system expands)
> **You:** "Some materials are confidential. I don't want them showing up in content creation. Archive them."
> 
> **Skill:** (In future, if confidentiality flags are indexed):
> `mat:archive --confidentiality restricted --dry-run`
> - Shows all materials tagged as restricted
> - You archive them, and `cre:privacy-guard` won't consider them (domain boundaries respected)

## 5. Important caveats

**Think before you archive.** Once archived, a material is marked as out-of-scope. If it contains the only evidence for a key claim, archiving it means losing that evidence from the active profile. Review dependencies before committing.

**Dry-run is your safety net.** Always run with `--dry-run` first. If the preview looks wrong, just don't execute the un-dry-run version. There's no penalty for a failed dry-run.

**Archived is not forgetting.** Archiving is not deletion. The file stays in git history, frontmatter is updated, and if later you need to resurrect a material, you can manually change `processing_status: archived` back to `validated` or whatever is appropriate.

**Filters don't cascade.** Archiving a material doesn't update profiles or trigger any downstream events. If a material was supporting a key claim in the profile, archiving it doesn't update the profile. You manage that separately.

**No recovery without git.** If you accidentally archive the wrong file and want to undo, you can either (a) manually edit the YAML frontmatter, or (b) revert the git commit. There's no built-in "unarchive" command.

**Bulk operations are powerful but risky.** Archiving 20 files at once is fast. Make sure your filters are right before you execute.
