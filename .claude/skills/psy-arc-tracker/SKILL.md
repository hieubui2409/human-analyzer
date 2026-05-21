---
name: psy:arc-tracker
description: "Track character growth arcs over time — compare hypothesis predictions vs actual profile evolution, verify milestones reached, and document character development trajectory. Use for arc planning reviews, content strategy informed by character progress, or periodic growth assessments. Triggers: 'arc tracker', 'growth tracking', 'character development', 'milestone check', 'arc review', 'did prediction come true', 'character progress'."
argument-hint: "--character <name> [--compare <hypothesis-date>|--milestones|--trajectory|--report]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "analysis"
  position: "periodic"
  dependencies: ["orc:bootstrap", "psy:hypothesis"]
---

# Character Arc Tracker

Track character growth trajectories. Compare predictions vs reality. Verify milestone achievement.

## When to Use

- Periodic arc review (monthly/quarterly)
- After major life events — did character respond as predicted?
- Content strategy: what growth stage is character in now?
- Close the hypothesis→reality loop (psy:hypothesis made predictions — did they come true?)

## Flags

| Flag                          | Purpose                                              |
| ----------------------------- | ---------------------------------------------------- |
| `--character <name>`          | Target character (required)                          |
| `--compare <hypothesis-date>` | Compare hypothesis from date against current profile |
| `--milestones`                | Review `milestones.md` progress against growth model |
| `--trajectory`                | Generate growth trajectory analysis                  |
| `--report`                    | Save report to plans/reports/                        |

## Workflow

### --trajectory (Default)

1. Load character profile via `orc:bootstrap --character {name} --intent psychology`
2. Extract growth indicators from:
   - `psychology/formulation.md`: coping mechanism evolution (less/more adaptive over time?)
   - `darkness/traumas.md`: are crisis patterns reducing in frequency/severity?
   - `light/strengths-hope.md`: are protective factors strengthening?
   - `timeline/overview.md`: event pattern trajectory (escalation vs stabilization)
   - `milestones.md`: milestones achieved, timing
3. Map to growth model:

   ```
   ## Growth Trajectory: {Character}

   ### Current Stage
   {stage description based on profile analysis}

   ### Growth Indicators (Positive)
   - {indicator}: {evidence from profile, with file:line}

   ### Stagnation Indicators (Neutral)
   - {indicator}: {evidence}

   ### Regression Indicators (Negative)
   - {indicator}: {evidence}

   ### Trajectory Direction
   {GROWTH / PLATEAU / REGRESSION} — confidence: {HIGH/MED/LOW}

   ### Timeline
   {ASCII timeline showing key inflection points}
   ```

### --milestones

1. Read `milestones.md` for character
2. For each milestone:
   - Status: ACHIEVED / IN_PROGRESS / NOT_STARTED / REGRESSED
   - Date achieved (if applicable)
   - Evidence from other profile files
3. Identify next expected milestones based on growth trajectory

### --compare `<hypothesis-date>`

1. Search `plans/reports/` for hypothesis reports matching character + date
2. Load the prediction
3. Compare predicted behaviors/outcomes against current profile state
4. Score prediction accuracy:

   ```
   ## Hypothesis vs Reality: {Character}

   ### Original Prediction ({date})
   {summary of hypothesis}

   ### Actual Outcome
   | Predicted | Actual | Match? |
   |-----------|--------|--------|

   ### Prediction Accuracy: {X}%
   ### Insights
   - What the model got right and why
   - What surprised and what it reveals about character
   ```

## Output

Report with growth trajectory, milestone status, and (optionally) hypothesis comparison.

If `--report` → save to `plans/reports/arc-tracker-{YYYYMMDD}-{character}.md`

## Scripts

| Script                                                    | Purpose                                                     |
| --------------------------------------------------------- | ----------------------------------------------------------- |
| `scripts/extract-growth-indicators-from-profile.py`       | Extract positive/negative growth signals from profile files |
| `scripts/compare-hypothesis-report-vs-current-profile.py` | Diff hypothesis predictions against current profile state   |

## Safety

- READ-ONLY — does not modify profiles, milestones, or content
- Writes only to stdout or plans/reports/ (with --report)
- Scope: character growth analysis and arc tracking. Does NOT modify profiles, create content, or provide clinical advice.

## See Also

psy:hypothesis, psy:crossref, cre:post-writer
