# cre:multiplatform — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You discover an angle: "Nhân vật A's mentoring consistency breakthrough." You want that on LinkedIn (professional), TikTok (hook-driven), and Facebook (emotional). But not as "same text, different format." LinkedIn should be text-first with a question close. TikTok should be a 9:16 script with a <1s hook. Facebook should be narrative-heavy. This skill writes 3 completely different natives from one concept, validates each per platform (evidence tier, voice, privacy threshold), and publishes only the ones that pass.

## 2. Core concepts (the mental model)

**1→N native generation (not reformat):**

Scripts scaffold per-platform briefs (native structure + constraints + source angle). LLM reads brief + voice profile → writes native post (not master-reformatted). Each platform gets its own artifact, tone, hook model, length.

**Per-variant gates:**

After generation, each variant runs through 3 gates:
1. `cre:evidence-scanner` — claims backed by T1-T2? (FAIL if T4-T5 or leak)
2. `cre:voice-audit` — tone match character's voice? (FAIL if HIGH drift)
3. `cre:privacy-guard` — PII/clinical leak, per platform's privacy_threshold? (FAIL if yes)

Any variant that fails is HELD (not written). Others still ship. Platform-specific thresholds mean LinkedIn (strict: no colleague names) is stricter than blog (permissive).

**DRY constraint source:** Platform rules (length, hook, hashtags, aspect ratio, privacy_threshold) live once in `.claude/scripts/platform_lib/platform_constraints.py`, imported by this skill and `cre:repurpose`.

## 3. Learning path

**First run:** Feed one angle from `cre:angle-discovery`:
```bash
.claude/skills/.venv/bin/python3 .claude/skills/cre-multiplatform/scripts/generate-native-variants-for-platforms.py \
  --source "Nhân vật A's mentoring consistency" --slug 260526-mentorship --platforms linkedin,tiktok,facebook --dry-run
```
See the scaffolded briefs: LinkedIn brief (text-first, 3000 chars, professional tone). TikTok brief (script, 9:16, conversational). Facebook brief (narrative, 6000 chars, emotional).

**As you grow:** Try `--platforms all` (7 platforms) when you want maximum reach. Use `--character hieu` to lock voice profile, improving voice-audit accuracy.

**Standard flow:** Discover angle → `cre:multiplatform --source <angle> --platforms active` → LLM writes → gates run → variants publish.

## 4. Use cases (each = a sample conversation)

### Use case: Batch multiplatform from discovery

> **You:** `cre:angle-discovery --character hieu --top 3 --json` returns 3 angles.
>
> **You:** Loop: per angle, `cre:multiplatform --source <angle> --platforms linkedin,tiktok,facebook --slug {dated-slug}`.
>
> **Skill:** Writes 3 natives per angle (9 posts total), gates each. 7 pass, 2 held (evidence FAIL on one platform, voice drift on another).
>
> **You:** Publish the 7 pass; investigate the 2 held.

### Use case: Active platforms only

> **You:** `cre:multiplatform --source context.md --slug 260526-pivot --platforms active --character hieu`
>
> **Skill:** Default `active` = platforms with existing asset dirs (blog, facebook, linkedin). Writes only to those.
>
> **You:** Publishes to the platforms you actually use.

### Use case: All platforms, strict gatekeeping

> **You:** `cre:multiplatform --source "https://linkedin.com/..." --slug 260526-repost --platforms all --character hieu`
>
> **Skill:** Scaffolds 7 natives. Evidence scanner, voice audit, privacy guard run. If any fails, that variant is HELD, reported with reason.
>
> **You:** Fix high-severity failures, re-run the variant (lower effort than full generation).

## 5. Important caveats

- **Native ≠ reformat:** Each platform gets a fresh write, not a reformatted copy. This is slower but earns 2-3× engagement and avoids algorithm suppression.
- **Gates can block:** A variant that fails any gate is HELD. You don't override it or force-publish. Investigate why it failed.
- **Privacy thresholds differ:** LinkedIn is strict (no colleague names even if mentioned positively). Blog is permissive (can discuss family stories). The same claim may PASS on blog, FAIL on LinkedIn.
- **Platform constraints live once:** Don't hardcode platform rules in prompts. Use `platform_constraints.py` (shared with `cre:repurpose`).
- **Held variants are not wasted:** You can investigate, fix the underlying issue (evidence tier, voice), and re-run generation for that platform only.

## See also

- [`SKILL.md`](./SKILL.md) for technical contract
- `cre:angle-discovery` — supplies angles for this skill
- `cre:post-writer` — single-platform full pipeline (this fans out to N)
- `cre:repurpose` — 1→1 post-publish (shares platform_constraints.py)
- `cre:evidence-scanner`, `cre:voice-audit`, `cre:privacy-guard` — per-variant gates
- Rule 03 (content pipeline), Rule 14 (CRE events)
