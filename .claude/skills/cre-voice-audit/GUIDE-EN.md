# cre:voice-audit — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You've published 5 posts about Character A over the past month. Reading them back, one post feels off — more formal, more clinical, than his usual voice. This skill reads his `identity/writing-voice.md` (the structured voice profile), then audits each of your 5 posts against it. Result: flagged which posts drift, what type of drift (tone break, vocabulary mismatch, implicit clinical language), severity. No rewrites — just clarity on where consistency slipped.

## 2. Core concepts (the mental model)

**Voice profile dimensions (from identity/writing-voice.md):**

Character A's profile lists: sentence rhythm (medium, varied), compression (moderate), emotional register (analytical default, range narrow), imagery bank (psychology + growth), hard bans (never says X, Y), defense gates (intellectualization manifests as dense, detailed), growth modifiers (recent arcs shift voice).

**Drift detection:**

1. **Tone break:** Post uses formal when voice is conversational (or vice versa) — HIGH severity
2. **Vocabulary mismatch:** Post uses words character would never use (hard bans violated) — MEDIUM
3. **Persona break:** Content contradicts character's established perspective — HIGH
4. **Platform over-adaptation:** Repurposed content lost original voice — MEDIUM
5. **Clinical leak:** Raw clinical terms in character-voiced content — HIGH

**Verdict cache:** Per-asset voice verdicts keyed on content hash. Unchanged assets = no re-judge (token efficiency). `--fresh` forces re-judge.

## 3. Learning path

**First run:**
```bash
.claude/skills/.venv/bin/python3 .claude/skills/cre-voice-audit/scripts/audit-published-content-for-voice-drift.py \
  --character character-a
```
Output: audit report. 5 posts scanned. Post 3 (LinkedIn mentoring) flagged: "Tone too formal (vs. conversational default). Vocabulary: 'pedagogical framework' — Character A avoids formal edu terminology." Severity: MEDIUM.

**As you grow:** Try `--report` to generate a full report saved to `plans/reports/`. Use `--fresh` when you've edited a post and want to re-audit.

**Standard flow:** Publish post → voice-audit auto-runs (via post-writer Phase 5) → if PASS, done; if HIGH drift, author re-edits.

## 4. Use cases (each = a sample conversation)

### Use case: Batch consistency check

> **You:** "I published 10 posts this month. Verify they all sound like Character A."
>
> **Skill:** `--character character-a` → scans all Character A posts in assets/ → "9 PASS (consistent), 1 MEDIUM (tone too formal on post_5)."
>
> **You:** Review post_5, maybe rewrite opening to match voice.

### Use case: Cross-platform voice check

> **You:** "Posts on LinkedIn sound different from TikTok. Is that platform adaptation or voice drift?"
>
> **Skill:** `--platform linkedin` → checks LinkedIn only. `--platform tiktok` → checks TikTok only. Compares reports.
>
> **You:** If LinkedIn is PASS and TikTok is WARN (tone mismatch), the TikTok post needs voice realignment.

### Use case: Single post audit

> **You:** "I just repurposed a LinkedIn post to blog. Check if voice held."
>
> **Skill:** `--file assets/blog/260526-repurposed-post` → audits that single post.
>
> **Skill:** "PASS — voice consistent with LinkedIn source + blog conversational tone allowed."

### Use case: Fresh re-audit after edit

> **You:** "I edited post_5 (flagged as MEDIUM drift). Re-audit to confirm fix."
>
> **Skill:** `--file assets/linkedin/post_5 --fresh` → ignores cached verdict, re-judges.
>
> **Skill:** "PASS — tone normalized. Vocabulary corrected."

## 5. Important caveats

- **Verdict cache is content-based:** Same asset = no re-judge. If you edit the post, verdict is stale (use `--fresh`).
- **Drift is heuristic, not absolute:** Voice audit is LLM-based; borderline cases require human judgment.
- **Severity is advisory:** HIGH drift doesn't auto-block; author decides action.
- **Platform-aware:** TikTok conversational tone is expected (not drift); LinkedIn conversational tone might be drift (depends on character profile).
- **Defense mechanisms matter:** Character's active defenses shape voice (e.g., Character A's intellectualization → dense, detailed language is NOT drift; it's authentic).

## See also

- [`SKILL.md`](./SKILL.md) for technical contract
- Verdict cache: [`verdict-cache-contract.md`](../_framework-shared/references/verdict-cache-contract.md)
- `cre:post-writer` (calls this auto in Phase 5)
- `cre:repurpose`, `cre:multiplatform` (use this for per-variant validation)
- Rule 02 (clinical reference show-don't-tell), Rule 03 (content pipeline)
