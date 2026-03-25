# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

ALWAYS activate `claude-code` skill before starting any implementation.

## ⚠️ CRITICAL: Current Project Directory & Structure

**KIT ABSOLUTE PATH:**

When current user is "duynguyen" (macOS):

```
/Users/duynguyen/www/claudekit-marketing/.claude
```

When current user is "bnqtoan" (macOS):

```
/Applications/MAMP/htdocs/claudekit-marketing/claudekit-marketing/.claude
```

When current user is "admin" (Windows):

```
D:\www\claudekit\claudekit-marketing\.claude
```

When current user is "hieubt" (Linux):

```
/home/hieubt/Documents/ck-marketing/.claude
```

**Structure:**

```
claudekit-marketing/
├── .claude/                    ← KIT OUTPUT (what we're building)
│   ├── agents/                 ← Marketing subagents
│   ├── commands/               ← Slash commands (e.g., /brand:update)
│   ├── skills/                 ← Domain knowledge & scripts
│   ├── workflows/              ← Process definitions
│   └── hooks/                  ← Automation hooks
├── docs/                       ← Project docs + Character profiles
│   ├── character-a/         ← Character profile: Nhân vật A
│   ├── character-b/         ← Character profile: Nhân vật B
│   └── materials/              ← Research materials, screenshots, analysis
├── assets/                     ← Example assets (for testing)
├── plans/                      ← Implementation plans
└── CLAUDE.md                   ← This file
```

**REMEMBER:**

- **All new skills, agents, commands → go to `.claude/`**
- **docs/ contains character profiles and research materials**
- **Scripts must be dynamic** - read from user's `docs/`, never hardcode values

---

## Related Projects & Directories

- `claudekit` - Website of ClaudeKit
  - Directory: `../claudekit`
  - Design guidelines: `../claudekit/docs/design-guidelines.md`
  - Repo: https://github.com/claudekit/claudekit
- `claudekit-marketing` - Marketing Kit repository
  - Directory: `.` (current project)
  - Repo: https://github.com/claudekit/claudekit-marketing
- `claudekit-engineer` - Engineer Kit repository
  - Directory: `../claudekit-engineer`
  - Repo: https://github.com/claudekit/claudekit-engineer
- `claudekit-cli` - CLI tool for quick project setup via `ck` command
  - Directory: `../claudekit-cli`
  - Repo: https://github.com/mrgoonie/claudekit-cli
- `claudekit-docs` - Public documentation repository: https://docs.claudekit.cc
  - Directory: `../claudekit-docs`
  - Repo: https://github.com/claudekit/claudekit-docs

---

## Project Overview

ClaudeKit Marketing is a comprehensive toolkit for sales and marketing automation using Claude Code subagent orchestration. This toolkit enables autonomous marketing workflows for content creation, campaign management, SEO optimization, and lead generation.

**Target Users:** Indie hackers, small marketing teams, SMB marketing managers

## What We're Building (CRITICAL)

**The deliverable is the `.claude/` folder itself** - a reusable kit users install in THEIR projects.

```
OUTPUT: ./claudekit-marketing/.claude/
        ├── agents/      # Marketing subagents
        ├── commands/    # Slash commands
        ├── skills/      # Domain knowledge
        ├── workflows/   # Process definitions
        └── hooks/       # Automation hooks
```

**NOT building:** A specific marketing project with hardcoded brand values.

### Key Principle: Dynamic Context

All commands/skills must read from USER's project, never hardcode values:

| Wrong                       | Right                                       |
| --------------------------- | ------------------------------------------- |
| `colors: #6366F1` hardcoded | Read from user's `docs/brand-guidelines.md` |
| `font: Inter` hardcoded     | Extract via `inject-brand-context.cjs`      |
| Specific company voice      | Parse user's brand voice docs               |

### Brand Injection Pattern

```
User runs command → inject-brand-context.cjs → user's docs/ → dynamic prompt
```

**Script:** `.claude/skills/brand-guidelines/scripts/inject-brand-context.cjs`

- Reads: `docs/brand-guidelines.md` (user's file)
- Outputs: Brand context for prompt injection
- Fallback: Graceful message if no brand docs exist

### When Building Kit Components

1. **Commands**: Use `inject-brand-context.cjs` for brand-aware features
2. **Skills**: Reference patterns, not specific values.
   - When scripts got errors, analyze and fix them.
   - When SKILL.md or references got outdated, use `research` and `docs-seeker` skills to research and update them.
3. **Agents**: Activate skills that read user context
4. **Templates**: Use `{{placeholders}}` not hardcoded values

---

## Character Profiles

This project contains detailed character profiles for content creation and storytelling:

### Nhân vật A (`docs/character-a/`)

| File              | Content                                  |
| ----------------- | ---------------------------------------- |
| INDEX.md          | Quick reference, links to all modules    |
| IDENTITY.md       | Basic info, education, career, family    |
| SOUL.md           | Inner essence, wounds, coping mechanisms |
| CHARACTERISTIC.md | Personality traits, behavioral patterns  |
| TIMELINE.md       | Full chronological events 1997-2026      |
| RELATIONSHIPS.md  | Family tree, relationship descriptions   |
| DARKNESS.md       | Trauma documentation, trigger warnings   |
| LIGHT.md          | Sources of hope, cho-nhận philosophy     |
| MILESTONES.md     | Trauma/growth/internal milestones        |
| ACHIEVEMENTS.md   | Academic, scholarships, awards           |
| MEDIA-COVERAGE.md | Press timeline, accuracy corrections     |
| WRITING-VOICE.md  | Tone, themes, narrative patterns         |
| INSPIRATION.md    | Inspirational story, transformation arc  |

### Nhân vật B (`docs/character-b/`)

| File              | Content                             |
| ----------------- | ----------------------------------- |
| INDEX.md          | Quick reference                     |
| IDENTITY.md       | Basic info, family, education       |
| SOUL.md           | Inner wounds, psychological traits  |
| CHARACTERISTIC.md | Personality, behavioral patterns    |
| TIMELINE.md       | Chronological events                |
| RELATIONSHIPS.md  | Family tree, relationship with Nhân vật A |
| DARKNESS.md       | Trauma, self-destructive behaviors  |
| LIGHT.md          | Sources of hope, growth signs       |
| MILESTONES.md     | Key milestones                      |
| CONVERSATION.md   | Extracted Messenger conversations   |

### Research Materials (`docs/materials/`)

- `Phân tích Nhân vật B + Nhân vật A - GEMINI.md` - Psychological analysis
- `Phân tích Nhân vật B + Nhân vật A - GG AI STUDIO.md` - Detailed relationship analysis
- `Tin nhắn hoà/` - Screenshot images of Messenger conversations

---

## Role & Responsibilities

Your role is to analyze user marketing requirements, delegate tasks to appropriate marketing-focused sub-agents, and ensure cohesive delivery of marketing assets and campaigns that meet brand guidelines and conversion goals.

## Workflows

- Primary workflow: `./.claude/workflows/primary-workflow.md`
- Development rules: `./.claude/workflows/development-rules.md`
- Orchestration protocols: `./.claude/workflows/orchestration-protocol.md`
- Documentation management: `./.claude/workflows/documentation-management.md`
- And other workflows: `./.claude/workflows/*`

**IMPORTANT:** Analyze the skills catalog and activate the skills that are needed for the task during the process.
**IMPORTANT:** You must follow strictly the development rules in `./.claude/workflows/development-rules.md` file.
**IMPORTANT:** Before you plan or proceed any implementation, always read the `./README.md` file first to get context.
**IMPORTANT:** Sacrifice grammar for the sake of concision when writing reports.
**IMPORTANT:** In reports, list any unresolved questions at the end, if any.
**IMPORTANT**: Date format is configured in `.ck.json` and injected by session hooks via `$CK_PLAN_DATE_FORMAT` env var. Use this format for plan/report naming.

## Documentation Management

We keep all important docs in `./docs` folder and keep updating them, structure like below:

```
./docs
├── project-overview-pdr.md
├── marketing-overview.md
├── brand-guidelines.md
├── design-guidelines.md
├── agent-catalog.md
├── skill-catalog.md
├── command-catalog.md
├── codebase-summary.md
├── system-architecture.md
├── project-roadmap.md
├── character-a/          ← Character profiles
├── character-b/          ← Character profiles
└── materials/               ← Research materials
```

**IMPORTANT:** _MUST READ_ and _MUST COMPLY_ all _INSTRUCTIONS_ in project `./CLAUDE.md`, especially _WORKFLOWS_ section is _CRITICALLY IMPORTANT_, this rule is _MANDATORY. NON-NEGOTIABLE. NO EXCEPTIONS. MUST REMEMBER AT ALL TIMES!!!_
