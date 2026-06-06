# orc:intake — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You get a new task: "Write a post about Character A's mentoring journey." But what skills should run? In what order? Intake analyzes the task, determines it's "content creation," and outputs the optimal skill chain: bootstrap → cre:exploring → orc:classify → cre:prompt-leverage → cre:post-writer → cre:privacy-guard → cre:voice-audit → orc:compounding. You don't have to remember the sequence.

## 2. Core concepts (the mental model)

**10 work types, each with a skill chain.** Content Creation, Profile Update, Arc Development, Research, Material Ingestion, Consistency Audit, Reference Management, Maintenance, Multi-Platform, Growth Analysis. Each has prerequisites, main skills, and post-work steps.

**Intake detects and routes.** Parse task description → match to work type → output chain.

**Auto-mode infers from git.** If you run `--auto`, it looks at git diffs and branch name to guess what you're working on.

## 3. Learning path

**First run:** `orc:intake "write a LinkedIn post about Character A's mentoring"` → sees "write post" → Content Creation → outputs chain.

**Auto-detect:** `orc:intake --auto` → looks at git changes, infers work type.

**Check current:** After intake, you see the chain and decide which steps to actually run.

## 4. Use cases (each = a sample conversation)

### Use case: Classify content creation task

> You: "I'm writing a LinkedIn post about Character A. What's my workflow?"
>
> Skill: Detects "write post" + "LinkedIn" → Content Creation. Outputs: bootstrap → cre:exploring → orc:classify → ... → orc:compounding. You now know the sequence.

### Use case: Auto-classify from git changes

> You: "What should I work on? Auto-detect from recent changes."
>
> Skill: Sees diffs in docs/profiles/character-b/psychology/ → Profile Update work type. Outputs: bootstrap → orc:classify → profile editing → psy:ref-audit → psy:crossref → orc:compounding.

## 5. Important caveats

- **Intake suggests; you decide.** The chain is recommended, not mandatory. Skip steps if they don't fit your workflow.
- **Work types are discrete.** If your task spans multiple types (e.g., "update profile AND write content"), intake may suggest one chain. You may need to run both chains manually.
- **Auto-mode is heuristic.** If git diffs are ambiguous (changes in multiple domains), auto-mode guesses. Be explicit if unsure.
