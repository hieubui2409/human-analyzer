# Narrative Twist Protocol

Rules for handling revealed falsehoods, invalidated facts, and narrative corrections in character profiles.

## Trigger

Apply when new source data invalidates a previously established "fact" in any profile file.

Examples:

- A character's public story is revealed to be fabricated
- New evidence contradicts an established timeline event
- A relationship's true nature is disclosed (e.g., mentor → romantic partner)

## Protocol Steps

### Step 1: Preserve the Old Narrative

**Do NOT delete the old narrative.** Apply strikethrough:

```markdown
~~Nhân vật C chưa từng có người yêu trong suốt thời đại học~~
```

### Step 2: Mark the Twist

Add twist marker immediately after the strikethrough:

```markdown
~~Nhân vật C chưa từng có người yêu trong suốt thời đại học~~
⚠️ TWIST: Nhân vật C đã yêu Huyền (mentor/người giới thiệu Scholarship X) hơn 1 năm, giữ bí mật hoàn toàn. [Source: T1, 30/03/2026]
```

### Step 3: Update Timeline

Add entries showing BOTH:

- When the character believed/presented the old narrative
- When the truth was revealed
- Source and priority level of the new information

```markdown
## 2024 (17 tuổi)

- 2024-XX: Gặp lại Huyền tại Âm Vang Xứ Thanh → bắt đầu yêu [PRIVATE]

## 2026 (18 tuổi)

- 2026-03-30: ~~[previous entry]~~ ⚠️ TWIST: Tiết lộ quan hệ với Huyền cho Nhân vật A
```

### Step 4: Cascade Updates

Check ALL profile files for references to the invalidated fact:

- INDEX.md — update summary
- relationships/family.md or relationships/{character}.md — add/modify relationship card
- psychology/core-wounds.md — update psychological analysis if twist affects core wound
- light/strengths-hope.md / darkness/traumas.md — adjust if protective factors or trauma changed
- milestones.md — add revelation as milestone if significant
- timeline/state-timeline.md — update psychological phase if twist changes current state

### Step 5: Cross-Character Impact

If the twist affects other characters' profiles:

1. Update their `relationships/{character}.md` with the new information
2. Add timeline entries in `timeline/overview.md` for when THEY learned the truth
3. Document psychological impact on them (e.g., Nhân vật A's response to Nhân vật C's revelation)

## Formatting Rules

- Old narrative: `~~strikethrough~~`
- New truth: `⚠️ TWIST: {description}`
- Source: `[Source: T{N}, {date}]`
- If twist is confidential: Add `[PRIVATE]` tag

## Examples from Project

### Nhân vật C's Stepmother Narrative

```markdown
~~Mẹ kế là người chăm sóc, nuôi dưỡng~~
⚠️ TWIST: Mẹ kế bỏ đi khi Nhân vật C 11 tuổi, chiếm đất ông bà [Source: T1]
```

### Nhân vật C-Huyền Relationship

```markdown
~~Huyền = mentor/người viết thư giới thiệu Scholarship X~~ [public narrative]
⚠️ TWIST: Huyền = mentor + người yêu bí mật >1 năm [Source: T1, 30/03/2026]
```
