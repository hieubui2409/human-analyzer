# psy:profile-lite — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

Full profiles are rich (~7,400 lines total for 3 characters = ~25,000 tokens). But when you're just sketching content angles or quickly orienting to a character, that's overkill and burns context. Lite profiles compress each character to 120–150 lines while keeping what matters: core wound, defense mechanisms, key relationships, active arc, behavioral patterns, clinical anchors, voice tone, quick facts. Load all 3 in ~1,400 tokens instead of 25,000. And the cache remembers: if you haven't edited the source profile since last lite generation, it reuses the old lite version (no re-computation).

## 2. Core concepts (the mental model)

- **Git-aware invalidation**: the lite cache is keyed on the source profile's git commit hash AND a working-tree dirty check. Any edit — committed or not — invalidates the cache, so the skill regenerates. No manual cache-clearing needed.
- **Compression rules**: Facts stay accurate; narrative gets compressed 3x. Theories are mentioned by name (not explained); recent timeline events prioritized over old ones; voice is preserved at sentence level, not full sections.
- **Pre-consistency check**: Before compressing, the skill can optionally run `psy:crossref --quick` to warn if source profiles have contradictions. Compress-first-ask-questions-later is risky.

## 3. Learning path

**First use:** `psy:profile-lite --character character-a` — see one lite profile, understand the format.

**Check cache:** `psy:profile-lite --stats` — see all three status + size savings.

**Refresh after edits:** `psy:profile-lite --refresh` — force regeneration if you manually edited profiles without committing.

## 4. Use cases (each = a sample conversation)

### Use case: Context-budget crunch

> You: "I need to load all 3 characters but have limited tokens left."
> Skill: `psy:profile-lite --all`
> → Returns ~400 lines total (3 lite profiles). Loads in 1.4% of context instead of 25%. Fast content-angle thinking enabled.

### Use case: Cache status check

> You: "Are my lite profiles fresh, or do I need to regenerate?"
> Skill: `psy:profile-lite --stats`
> → Character A: valid (2d old), Character B: stale (7d, source changed), Character C: valid (1d). Recommendation: refresh Character B.

### Use case: Post-edit refresh

> You: "I just manually edited psychology/formulation.md for Character A. Do I need to refresh lite?"
> Skill: `psy:profile-lite --character character-a --refresh`
> → Regenerates Character A lite from current files. Updates cache. Done.

### Use case: Cre workflow integration

> You: "I'm about to write content. Load all 3 characters efficiently."
> Workflow: `cre:exploring --lite` or similar (cre skills call psy:profile-lite internally)
> → Lite profiles loaded automatically. Content ideation proceeds with 1% context overhead.

## 5. Important caveats

- **Lite ≠ full**: A lite profile is a tool for quick orientation, not deep validation. If you need to verify clinical accuracy or cross-character consistency, use full profiles + psy:crossref.
- **Compression can hide nuance**: A thin-file psychology/formulation.md becomes 2 lines in lite. If a pattern is subtle, it might get lost. Check `--stats` to see line counts; if a source file is < 50 lines, lite will compress it heavily.
- **Manual source edits without commit break cache**: If you edit a profile file without committing, git commit hash (with uncommitted-edit check) doesn't change, cache stays stale. Commit or use `--refresh` to force.
- **Pre-regeneration check optional**: The skill can warn if source profiles contradict (via internal `psy:crossref --quick`). If you skip this, a stale/contradictory source compresses into a stale/contradictory lite. User's call.
