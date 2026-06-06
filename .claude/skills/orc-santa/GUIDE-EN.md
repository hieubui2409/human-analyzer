# orc:santa — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

High-risk changes (profile updates, sensitive content) need scrutiny. Two independent reviewers catch issues the other might miss. Reviewer A focuses on domain-specific accuracy. Reviewer B focuses on consistency. They don't see each other's feedback, so neither anchors to the other's view. If both pass, you ship. If either fails, you fix and re-review.

## 2. Core concepts (the mental model)

**Input-level isolation.** Each reviewer gets only the target files + pre-check report. No session history, no other reviewer's output. This prevents anchoring bias.

**Two reviewers, two lenses.** Reviewer A (domain expert) checks accuracy. Reviewer B (consistency expert) checks cross-references and contradictions.

**Max 2 rounds.** Round 1 review → fix issues → round 2 review with fresh agents. If round 2 still has issues, escalate to user.

## 3. Learning path

**First review:** `orc:santa --review docs/profiles/character-b/psychology/ --framework psy --scope full`. Two reviewers examine, output PASS or FAIL.

**Fix issues:** Address all issues from both reviewers.

**Re-review:** Round 2 auto-runs with fresh agents (no memory of round 1). Both must pass.

## 4. Use cases (each = a sample conversation)

### Use case: Review profile edit after high_risk classification

> You: "High_risk classification for Character B's psychology update. Run Santa."
>
> Skill: Reviewer A (Clinical Accuracy): "DSM-5 codes valid? 5P formulation consistent? Attachment patterns match theory?" Reviewer B (Cross-Character Consistency): "Dates match across characters? Relationship dynamics bidirectional? No contradictions?" Both output PASS or list issues. You fix if needed.

### Use case: Round 2 after fixing issues

> You: "I fixed the issues. Re-review please."
>
> Skill: Spawns fresh Reviewer A' + B' (no round 1 context), same pre-checks, review again. If both pass, "SHIP ✅". If either fails again, escalate options shown.

## 5. Important caveats

- **Santa is recommended, not mandatory.** orc:classify suggests it for high_risk; you can skip.
- **Reviews take tokens.** 2 subagents per round × 2 rounds max = 4 subagents. Use for genuinely high-risk.
- **Escalation after round 2.** No auto round 3. If issues persist, user decides: fix manually, override ship, or abandon.
- **Scope affects cost.** `full` = all files (expensive), `changes` = git changes only (cheap), `ref` = changes + cross-refs (medium).
