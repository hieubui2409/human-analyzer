---
name: cre:repurpose
description: "Adapt existing content from one platform to another while respecting platform constraints. Use when you have a published post and need versions for other platforms. Triggers: 'repurpose', 'adapt for', 'convert to', 'cross-post', 'reformat for', 'LinkedIn to TikTok', 'Facebook to Twitter'."
argument-hint: "--from <path-or-platform> --to <platform> [--character <name>|--tone <override>]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "content"
  position: "post-publish"
  dependencies:
    [
      "cre:post-writer",
      "cre:prompt-leverage",
      "cre:privacy-guard",
      "cre:voice-audit",
    ]
---

# Content Repurpose

Adapt **one existing published post → one other platform** (1→1, post-publish) per
`docs/rules/03-content-creation-pipeline.md` platform guidelines.

> **Scope vs `cre:multiplatform` (C1):** repurpose = adapt an *existing* post 1→1;
> `cre:multiplatform` = generate *native* drafts 1→N from a source/angle. Both share the
> single platform-rules module `.claude/scripts/platform_lib/platform_constraints.py`
> (length, hook model, hashtags, aspect ratio, privacy threshold) — no duplicate table.

## Flags

| Flag                      | Purpose                                                |
| ------------------------- | ------------------------------------------------------ |
| `--from <path\|platform>` | Source: file path or platform name to find latest post |
| `--to <platform>`         | Target platform                                        |
| `--character <name>`      | Override POV character                                 |
| `--tone <override>`       | Override tone for target platform                      |

## Platform Adaptation Rules

| Source → Target      | Key adaptations                                                  |
| -------------------- | ---------------------------------------------------------------- |
| LinkedIn → Facebook  | Relax professional tone, allow raw emotion, remove hashtag limit |
| LinkedIn → TikTok    | Extract hook → 60s script, conversational, fast-paced            |
| LinkedIn → Twitter   | Thread format, punchy quotes, 280-char segments                  |
| Facebook → Instagram | Shorten to 2200 chars, visual-first, add 15-20 hashtags          |
| Facebook → LinkedIn  | Professional framing, maintain vulnerability with polish         |
| Any → Blog           | Expand, add clinical backing, deep narrative                     |
| Blog → Any           | Extract core message, compress to platform constraints           |

## Workflow

1. **Read source** content (post.md from specified path/platform)
2. **Load platform constraints** from `.claude/scripts/platform_lib/platform_constraints.py` (`get_constraints(platform)` — single source; mirrors `docs/rules/03-content-creation-pipeline.md`)
3. **Identify core message** — what's the essential insight/story
4. **Adapt**:
   - Adjust length to target constraints
   - Modify hook for target platform's attention model
   - Adjust tone (LinkedIn=professional, TikTok=conversational, etc.)
   - Reformat structure (thread for Twitter, caption for Instagram)
   - Update hashtags per platform norms
5. **Run privacy check** — `cre:privacy-guard --file` on adapted content (MANDATORY)
6. **Run voice audit** — `cre:voice-audit --file` verify tone didn't drift during adaptation
7. **Output** standard package in `assets/{platform}/{YYMMDD}-{slug}/`
8. **Run compounding** — `orc:compounding --content` extract platform adaptation learnings

## Output

Standard 5-file package per `docs/rules/03-content-creation-pipeline.md`:

- `post.md` (adapted source)
- `post.txt` (publish-ready)
- `prompt.txt` (image prompts if visual needed)
- `images/` (directory)
- `README.md` (input parameters + repurpose source reference)

## PSY/MAT Framework Integration

When repurposing content:

- Read `psychology/cultural-formulation.md` — platform adaptation should respect cultural context (e.g., Nhân vật B's Tỉnh X gambling culture references may need contextualization for LinkedIn's professional audience)
- Maintain evidence tier integrity — if original used T1 evidence, adapted version must not downgrade to T5 speculation
- Cross-reference `docs/graph/{dyad}.md` for relationship-focused content — ensure adapted version preserves documented dynamics
- Emit `CRE.published` event after successful repurpose (consumed by ORC orchestration)

## Safety

- MUST preserve clinical accuracy from original — no oversimplification that creates misinformation
- MUST respect privacy boundaries from original (if original has `[PRIVATE]` exclusions, adapted version must too)
- Evidence tier preservation — adapted content must not claim higher confidence than source material supports
- Scope: content adaptation. Does NOT create new content — use `cre:post-writer` for that.

## See Also

cre:post-writer, cre:voice-audit, cre:privacy-guard, cre:multiplatform (1→N native generation)
