---
name: psy:profile-lite
description: "Compress full character profiles into token-efficient summaries (~100-150 lines per character vs ~700-1000 lines full). Caches to .claude/profile-cache/. Auto-invalidates when source profiles change via git. Use when context budget is tight or loading all 3 characters. Triggers: 'lite profile', 'compress profile', 'compact profile', 'profile summary', 'light load'."
argument-hint: "[--character <name>|--all|--refresh|--stats]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "optimization"
  position: "utility"
  dependencies: ["mpc:bootstrap"]
---

# Profile Lite — Token-Efficient Character Summaries

Compress ~7400 lines of profiles → ~400 lines total (3 characters). Cached, git-aware invalidation.

## Problem

| Load mode         | Lines | Est. tokens | Context % |
| ----------------- | ----- | ----------- | --------- |
| Full 3 characters | ~7400 | ~25,000     | ~25%      |
| Lite 3 characters | ~400  | ~1,400      | ~1.4%     |
| INDEX.md × 3      | ~190  | ~650        | <1%       |

Full load burns 25% of context before any work starts. Lite mode gives 95% reduction while preserving actionable information.

## Default (No Arguments)

`--all` — generate/load lite profiles for all 3 characters.

## Flags

| Flag                 | Purpose                               |
| -------------------- | ------------------------------------- |
| `--all`              | All 3 characters (default)            |
| `--character <name>` | One character only                    |
| `--refresh`          | Force regeneration (ignore cache)     |
| `--stats`            | Show cache status and size comparison |

## Cache Location

`.claude/profile-cache/{character-slug}-lite.md`

Files:

- `character-a-lite.md`
- `character-b-lite.md`
- `character-c-lite.md`
- `cache-metadata.json` — git hashes for invalidation

## Cache Invalidation

```json
// .claude/profile-cache/cache-metadata.json
{
  "character-a": {
    "source_hash": "{git hash of docs/profiles/character-a/}",
    "generated": "2026-05-13T10:00:00Z",
    "lines": 130
  },
  ...
}
```

Check: `git log -1 --format=%H -- docs/profiles/{character}/` vs stored hash.
If different → regenerate. If same → serve from cache.

## Lite Profile Structure (~120-150 lines per character)

```markdown
# {Character Name} — Lite Profile

**Generated:** {date} | **Source hash:** {short hash}

## Identity (5 lines)

- DOB, age, location, occupation/education
- Key family members (one line each)
- Current life status

## Psychological Core (20 lines)

- Primary wound (2-3 sentences)
- Core defense mechanisms (list)
- Attachment style + manifestation
- Savior/victim/rescuer dynamics (if applicable)
- Current psychological state

## Key Relationships (15 lines)

- {Person}: {nature}, {current state}, {key dynamic}
- (one paragraph per significant relationship)

## Active Arc (10 lines)

- Current narrative direction
- Recent developments (last 3 months from TIMELINE)
- Unresolved tensions
- Growth trajectory

## Behavioral Patterns (10 lines)

- Communication style
- Stress responses
- Decision-making patterns
- Social presentation vs inner state

## Clinical Anchors (10 lines)

- Primary theories that explain this character
- Key refs: {theory} → {how it manifests}
- Vietnamese cultural context factors

## Content Guidelines (10 lines)

- Voice/tone when writing as/about this character
- Topics that resonate with audience
- Sensitivity boundaries
- Platform preferences

## Quick Facts (10 lines)

- Timeline of 5-7 most important events
- Key dates to remember
- Factual anchors (verified, non-contradictory)
```

## Workflow

### --all / --character

1. Check cache validity via git hash comparison
2. If valid → read and output cached lite profile
3. If stale or missing → regenerate:
   a. Read ALL profile files for character
   b. Compress into lite structure above
   c. Preserve factual accuracy — no embellishment
   d. Prioritize actionable info for content creation
   e. Write to cache
   f. Update cache-metadata.json
4. Output lite profile(s) to conversation

### --refresh

Force regeneration regardless of cache state. Useful after major profile overhaul.

**Pre-regeneration check:** Before regenerating, verify source profiles are internally consistent:

1. Run `psy:crossref --character <name> --quick` (if available) to catch contradictions
2. If CRITICAL inconsistencies found → warn user before compressing stale/conflicting data into lite
3. Rationale: lite profiles amplify errors — a wrong fact compressed into 1 line is harder to spot than in full context

### --stats

```
## Profile Cache Status

| Character | Full lines | Lite lines | Reduction | Cache valid | Age |
|-----------|-----------|------------|-----------|-------------|-----|
| Nhân vật A      | 2957      | 135        | 95.4%     | ✓           | 2d  |
| Nhân vật B       | 2187      | 120        | 94.5%     | ✗ (stale)   | 7d  |
| Nhân vật C     | 2299      | 128        | 94.4%     | ✓           | 2d  |
| Total     | 7443      | 383        | 94.9%     |             |     |
```

## Compression Rules

1. **Preserve facts** — dates, names, relationships must be exact
2. **Compress narrative** — multi-paragraph backstory → 2-3 sentences
3. **Prioritize recency** — recent timeline events over old ones
4. **Keep clinical anchors** — theory names + how they apply, drop lengthy explanations
5. **Maintain voice cues** — enough to write in character, not full WRITING-VOICE.md
6. **Flag contradictions** — if source has inconsistencies, note them explicitly
7. **Include cross-refs** — mark where characters intersect

## Integration

- `mpc:bootstrap --quick` can use lite profiles instead of INDEX.md for richer context at low token cost
- `cre:post-writer` should load lite profile by default, full only if needed
- `cre:exploring` can reference lite profile during Q3 (angle selection)

## Safety

- Lite profiles are DERIVED — never edit them directly
- If a lite profile seems wrong, fix the SOURCE profile files
- Cache auto-invalidates when sources change
- Scope: profile compression for ck-marketing. Does NOT modify source profiles.

## Examples

```bash
/psy:profile-lite                               # load all 3 lite
/psy:profile-lite --character hòa               # Nhân vật B only
/psy:profile-lite --refresh                     # force regeneration
/psy:profile-lite --stats                       # cache status
```

## See Also

- `/mpc:bootstrap` — context loading (uses lite profiles when available)
- `/cre:post-writer` — content creation (loads lite by default)
- `/psy:crossref` — needs full profiles for deep validation
