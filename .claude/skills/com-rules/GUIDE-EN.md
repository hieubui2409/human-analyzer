# com:rules — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You've edited character profiles, created content, or modified materials. Before you commit, you want to make sure everything follows the project rules — missing frontmatter fields, broken links, evidence-tier leaks. com:rules runs a check, tells you what's wrong, and suggests fixes. No surprises when code review happens.

## 2. Core concepts (the mental model)

**16 modular rules:** Each rule owns one concern (profile structure, references, confidentiality, evidence tiers, etc.). Rules don't overlap — they compartmentalize.

**Smart routing:** Different rules need different validators. Some are checked inline (frontmatter presence), others delegate to specialized skills (`psy:ref-audit`, `cre:privacy-guard`). com:rules orchestrates.

**File classification:** The skill looks at your file path and decides which rules apply. Edit `docs/profiles/*/psychology/`? Rules 01, 02, 05, 08 apply. Edit `assets/`? Rules 03, 09, 14 apply.

**Report, don't fix:** This is a read-only audit. It flags issues and suggests what to do; you make the changes.

## 3. Learning path

**First run:** Edit a profile file, then run `com:rules`. See what rules apply and which ones report violations.

**Next:** Try `com:rules --list` to see all 16 rules and their statuses. Gives you a project health snapshot.

**As you grow:** Use `--check 02` to validate references in isolation; use `--scope all` to audit the entire project; use `--scope docs/materials/` to validate a specific folder.

## 4. Use cases (each = a sample conversation)

### Use case: Validate changes before commit

> You: "check rules"
> Skill: Scans git diff, finds 2 files changed. Runs rules 01, 02, 08 (profile rules). Reports: "Rule 01 ✅ | Rule 02 ⚠️ missing citation in line 45 | Rule 08 ✅". You fix line 45, then commit.

### Use case: List all rules and their status

> You: "show me all the rules"
> Skill: `com:rules --list`. Prints all 16 rules with brief descriptions and whether they passed/failed on the project. Gives you the rule landscape.

### Use case: Deep-check a specific rule

> You: "validate rule 09 (confidentiality)"
> Skill: `com:rules --check 09`. Scans all assets/ files for privacy violations (real names, contact info, etc.). Reports each instance with line numbers.

### Use case: Audit everything (pre-release)

> You: "full compliance audit"
> Skill: `com:rules --scope all`. Checks all tracked .md files against all applicable rules. Gives you a full-project report. Good before a release.

### Use case: Validate a folder

> You: "check rules in materials"
> Skill: `com:rules --scope docs/materials/`. Runs rules 04, 11 on all material files. Checks evidence tiers and processing status.

## 5. Important caveats

**Delegated validators need context.** If rule 02 (references) flags an issue, com:rules calls `psy:ref-audit` under the hood. That skill needs the right context to run. If it fails, you see the error and must handle it manually.

**Process rules are skipped.** Rules 06 (crisis-protocol) and 13 (workflow) are process rules, not file rules. They describe steps/events, not frontmatter/schema. Not validated here.

**Schema != logic.** com:rules checks that frontmatter fields exist and are formatted correctly. It does NOT check if the *content* is truthful or consistent. That's a job for semantic validators like `psy:crossref`.

**Report is read-only.** You get recommendations; you apply them. The skill never modifies your files.

**Scope matters.** The `--scope` flag determines whether you validate only changes (uncommitted), all files (all), or a specific path (path). Pick the right scope or waste time checking unrelated files.
