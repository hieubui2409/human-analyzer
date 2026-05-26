---
name: cre:multiplatform
description: "Generate N platform-NATIVE content variants from one source/angle simultaneously (1→N) — LinkedIn/Facebook/Instagram/TikTok/YouTube/Twitter/blog. Each variant is written native to its platform (not a watermarked cross-post; research: native earns 2-3× engagement, platforms suppress recycled content), gated per-variant by cre:evidence-scanner + cre:voice-audit + cre:privacy-guard before write, with a per-platform privacy threshold. Distinct from cre:repurpose (1→1 post-publish adaptation). Triggers: 'multiplatform', 'all platforms', 'native variants', 'post everywhere', 'generate for all', '1 to many', 'cross-platform native'."
argument-hint: "--source <path|angle> --slug <slug> [--platforms active|all|<list>] [--character <slug>] [--dry-run]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "cre-framework"
  position: "generation"
  dependencies: ["cre:evidence-scanner", "cre:voice-audit", "cre:privacy-guard"]
---

# cre:multiplatform — 1→N Platform-Native Generation

`cre:repurpose` adapts **one existing post → one other platform** (1→1, post-publish).
This skill generates **one source/angle → N native drafts** (1→N, simultaneous). Each
variant is written *native* to its platform — a TikTok 9:16 script with a <1s hook is a
different artifact from a LinkedIn text-first post with a question close, not the same copy
reformatted. Research: platform-native content earns 2-3× engagement; TikTok/Instagram
algorithmically suppress watermarked/recycled cross-posts; audiences detect off-platform tone.

Feed it a `cre:angle-discovery` (B7) or `psy:relation-intelligence` (B9) angle, a CONTEXT.md,
or an existing post path.

## Determinism Split (GOLDEN RULE #4)

| Layer    | Owner                                          | Does                                                                                                                                  |
| -------- | ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Scaffold | `generate-native-variants-for-platforms.py`    | Resolve platforms, create each `assets/{platform}/{slug}/` package, emit per-platform `brief.json` (native structure + constraints + privacy threshold + source). Deterministic. |
| Write    | **LLM**                                        | Write the NATIVE `post.md` per platform FROM the brief + VOICE PROFILE + PSY defense gates. Heuristic. NOT a reformat of one master.   |
| Gate     | `cre:evidence-scanner` + `cre:voice-audit` + `cre:privacy-guard` | Per variant, before publish-ready write. Any FAIL → variant HELD (not written), reported. |

## Usage

```bash
PY=$HOME/.claude/skills/.venv/bin/python3
SK=.claude/skills/cre-multiplatform/scripts

# 1. scaffold native briefs (deterministic) — default = active platforms
$PY $SK/generate-native-variants-for-platforms.py \
    --source "<angle title or path or angle.json>" --slug 260526-my-slug \
    --platforms active --character hieu --json
#   → assets/{linkedin,facebook,blog}/260526-my-slug/{brief.json, post.md placeholder, images/}

# 2. LLM writes a NATIVE post.md per platform FROM each brief.json
# 3. per variant: run the 3 gates; on all-pass, write publish-ready post.txt + emit CRE.published
```

`--platforms`: `active` (default — only `assets/` dirs that exist: blog/facebook/linkedin),
`all` (7 platforms), or a comma list (`"linkedin,tiktok"`). `--dry-run` previews dirs + briefs
without writing. Default scope = **active only** so generation isn't wasted on unused channels.

## Per-Variant Gates (FAIL → HELD)

Each variant must pass **all three** before its publish-ready copy is written:

1. `cre:evidence-scanner` — per-claim tier gate (T4/T5 or Rule-09 leak → FAIL).
2. `cre:voice-audit` — native structure didn't drift the character voice.
3. `cre:privacy-guard` — PII / privacy-tag / clinical-term leak, at the platform's
   `privacy_threshold` (LinkedIn **strict** — employer/colleague names; blog **permissive**).

A variant that fails any gate is **HELD** (not written) and reported — the other variants
still ship. No partial leak slips through because one platform is laxer.

## Single Source of Platform Rules (DRY)

Platform constraints (length, hook model, hashtags, aspect ratio, native_structure,
privacy_threshold) live once in `.claude/scripts/platform_lib/platform_constraints.py`,
imported by **both** this skill and `cre:repurpose`. No duplicate platform table.

## Events

Emits **`CRE.published`** → `content-events.jsonl` per written variant:

```bash
$PY .claude/skills/orc-event-log/scripts/append-event-to-log.py \
  --event-type CRE.published --source cre:multiplatform \
  --character <slug> --reason "platform=<p> slug=<slug> gates=pass"
```

## Boundaries (C3 stocktake will verify)

- **vs `cre:repurpose`** — repurpose = adapt an *existing published* post 1→1 (post-publish);
  multiplatform = generate *native* drafts 1→N from a source/angle (generation). Both share
  `platform_constraints.py` but have distinct entry points and scope.
- **vs `cre:post-writer`** — post-writer = one platform, full interactive pipeline; this fans
  out to N platforms and delegates per-variant writing to the same voice/gate machinery.

## See Also

- `cre:angle-discovery` (B7) — `--source <angle>` feeds this skill.
- `cre:repurpose` — 1→1 post-publish adaptation (shares platform_constraints).
- `cre:post-writer` — single-platform full pipeline.
- `cre:evidence-scanner` / `cre:voice-audit` / `cre:privacy-guard` — per-variant gates.
- Rule 03 (`content-creation-pipeline`) — platform guidelines (source of the constraints).
- Rule 14 (`cre-evidence-and-events`) — CRE events + evidence-tier permissions.
