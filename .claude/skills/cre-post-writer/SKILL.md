---
name: cre:post-writer
description: "End-to-end post creation pipeline. Select character + platform → load profile (lite) → apply voice + clinical framing → generate draft → output to assets/. Wraps bootstrap, prompt-leverage, and content creation into single flow. Use for any social media post, blog, or content piece. Triggers: 'write post', 'create post', 'draft post', 'new post', 'write content', 'content for linkedin/facebook/instagram/tiktok/youtube'."
argument-hint: "[topic] [--character <name>] [--platform <name>] [--type fiction|reality|analysis|letter]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "content"
  position: "execution"
  dependencies:
    [
      "psy:profile-lite",
      "cre:prompt-leverage",
      "orc:bootstrap",
      "cre:privacy-guard",
      "cre:voice-audit",
    ]
---

# Post Writer — End-to-End Content Creation

Single command: character + platform + topic → published-ready draft in assets/.

## Default (No Arguments)

Interactive mode — ask character, platform, topic via `AskUserQuestion`.

## Flags

| Flag                 | Purpose                                                               |
| -------------------- | --------------------------------------------------------------------- |
| (topic)              | Topic/angle for the post                                              |
| `--character <name>` | Which character to write about/as                                     |
| `--platform <name>`  | Target: linkedin, facebook, instagram, tiktok, youtube, twitter, blog |
| `--type <type>`      | Content type: fiction, reality, analysis, letter                      |
| `--from-context`     | Use existing CONTEXT.md from cre:exploring                            |
| `--quick`            | Skip profile loading (use session context)                            |

## Content Types

| Type       | Description                                        | Voice                    | Examples                                            |
| ---------- | -------------------------------------------------- | ------------------------ | --------------------------------------------------- |
| `reality`  | Real events, reflections, personal sharing         | First-person authentic   | LinkedIn vulnerability posts, Facebook life updates |
| `fiction`  | Fictionalized narrative inspired by real events    | Third-person or literary | Blog stories, creative writing                      |
| `analysis` | Psychological or behavioral analysis               | Reflective, educational  | LinkedIn insight posts, analytical threads          |
| `letter`   | Epistolary format — letter to someone/from someone | Intimate, direct address | "Thư gửi..." format, blog letters                   |

## Pipeline

### Phase 0: Stale Voice Gate (MANDATORY)

Before any content generation, check freshness:

1. Read `last_psy_refresh` and `last_material_integration` from session state (`.claude/session-state/state.json`)
2. If `last_material_integration` > `last_psy_refresh` → voice data is STALE
   - **BLOCK** content generation
   - Run `cre:voice-audit --character <name>` first
   - If voice-audit finds HIGH drift → require `PSY.refresh` before proceeding
   - If voice-audit finds LOW/MEDIUM drift → proceed with warning
3. If timestamps unavailable → proceed with warning "freshness unknown"

### Phase 1: Context Loading (5 seconds)

1. Load character lite profile (`psy:profile-lite --character <name>`)
   - If --quick: skip, use whatever context is already loaded
2. Read `identity/writing-voice.md` for target character. Extract `## Voice Profile (Structured)` section — inject as VOICE PROFILE context block into prompt.
3. Read `psychology/formulation.md` for 5P context (informs content angle)
4. Read `psychology/defense-mechanisms.md` for voice authenticity
5. Load session state for current arc context + active domain

### Phase 2: Prompt Strengthening (auto)

Apply `cre:prompt-leverage` layers internally:

1. Character voice lock
2. Clinical accuracy guard (if psychological content)
3. Platform formatting constraints
4. Profile cross-reference facts
5. Sensitivity scan

### Phase 3: Draft Generation

Based on type + platform, generate draft following structure:

#### LinkedIn Post Structure

```
[Hook — 1-2 lines that stop scrolling]

[Story/Setup — 3-5 short paragraphs]

[Insight/Turn — the realization or lesson]

[Call to reflection — not CTA, but invitation to think]

---
[Optional: context note about character/topic]
```

#### Facebook Post Structure

```
[Emotional hook]

[Extended narrative — can be longer, storytelling-focused]

[Emotional resolution]

[Community prompt — question for comments]
```

#### Blog Post Structure

```
# Title

[Opening scene or hook]

## Sections with subheadings

[Deep narrative with clinical backing where relevant]

## Closing

[Resolution or open question]
```

#### Instagram Caption

```
[First line hook — visible before "more"]

[Short, punchy paragraphs]

[Emotional close]

.
.
.
[Hashtags — 15-20 relevant]
```

### Phase 4: Output

1. Create asset directory: `assets/{platform}/{YYMMDD}-{slug}/`
2. Write `post.md` — markdown formatted draft
3. Write `post.txt` — plain text version (for direct copy-paste to platform)
4. Write `prompt.txt` — the strengthened prompt used (for reproducibility)
5. If image needed: write `image-prompts.txt` with AI image generation prompts
6. Print summary with file paths

### Phase 5: Mandatory Validation Gates

Before reporting complete, run these automated checks:

1. **Privacy scan** — `cre:privacy-guard --file {post_path}` (BLOCKS if violations found)
2. **Voice audit** — `cre:voice-audit --file {post_path}` (BLOCKS if HIGH drift)
3. **Clinical leak check** — if post contains clinical terms, `psy:ref-audit --term {term}` to verify accuracy

### Phase 6: Profile→Content Alignment Check

After automated gates pass, verify content doesn't contradict profiles:

1. **Factual alignment** — cross-check claims against `timeline/state-timeline.md`, `identity/core.md` (dates, events, relationships)
2. **Psychological alignment** — verify emotional framing matches `psychology/formulation.md`, `psychology/defense-mechanisms.md` (no contradictory coping portrayals)
3. **Relationship alignment** — if post mentions cross-character dynamics, verify against `relationships/family.md`, cross-character files (e.g. `relationships/character-b.md`, discovered via `list_relationship_files()`), and `docs/graph/{dyad}.md`
4. **Evidence alignment** — verify claims are backed by T1-T3 evidence (MAT framework). T4-T5 claims must be explicitly qualified
5. If ANY contradiction found → fix before output, don't just flag

### Phase 7: Quality Checklist

Final manual checks:

- [ ] Platform constraints met (length, format)?
- [ ] Sensitivity boundaries respected?
- [ ] Image prompts don't produce recognizable real faces?

## Interactive Mode (no args)

```
Q1: Character? → Nhân vật A / Nhân vật B / Nhân vật C / Cross-character / General
Q2: Platform? → LinkedIn / Facebook / Instagram / TikTok / YouTube / Twitter / Blog
Q3: Type? → Reality / Fiction / Analysis / Letter
Q4: Topic? → [free text]
Q5: Any specific angle or reference? → [free text or "no"]
```

## --from-context

1. Read most recent CONTEXT.md (from cre:exploring)
2. Extract all locked decisions
3. Skip interactive questions — go straight to Phase 1
4. Use exploration decisions as pipeline inputs

## Safety

- Generated content saved to assets/ — never overwrites existing files
- Uses slugified dates to prevent naming conflicts
- Sensitive content flagged before output
- Never auto-publishes — user must manually post
- Scope: content generation for ck-marketing. Writes to assets/ only.

## Examples

```bash
/cre:post-writer                                               # interactive
/cre:post-writer Mentoring journey --character hieu --platform linkedin --type reality
/cre:post-writer Nhân vật B's growth story --character hòa --platform facebook --type fiction
/cre:post-writer --from-context                                # from exploration
/cre:post-writer Letter to Nhân vật C --character chien --platform blog --type letter
```

## See Also

- `/cre:exploring` → produces CONTEXT.md → feeds --from-context
- `/cre:prompt-leverage` → called internally for prompt strengthening
- `/psy:profile-lite` → loaded for token-efficient context
- `/orc:classify` → should run before post-writer for risk assessment
- `docs/rules/03-content-creation-pipeline.md` → content pipeline + platform guidelines
- `docs/rules/09-confidentiality-protocol.md` → privacy + content boundaries
