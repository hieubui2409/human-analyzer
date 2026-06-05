# orc:observe — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

Framework skills notice things: "Nhân vật B uses intellectualization when conflicted," "LinkedIn posts with vulnerability hooks get 2x engagement," "Nhân vật A's competency gap in delegation." These observations are worth remembering. Observe lets skills emit signals that get recorded in an observation stream. Later, `orc:compounding` mines those signals into learnings.

## 2. Core concepts (the mental model)

**Two observation sources:** Automatic (framework edits trigger `*-touched` signals) and semantic (skill judges something notable and emits a signal). Both feed the observation stream.

**Signal vocabulary is bounded.** Defense-pattern, low-craap, voice-drift, competency-delta, etc. Not arbitrary; signals must be in the allowed vocabulary.

**Observations are passive.** Unlike events (which trigger cascades), observations accrete for later mining. A signal doesn't cause anything to run.

## 3. Learning path

**Automatic signals:** Skills don't call observe; the framework hook auto-emits when data is edited.

**Semantic signals:** At end of skill work, if something notable surfaced, the skill calls observe to record it.

**Mining signals:** `orc:compounding` reads observation stream and extracts learnings.

## 4. Use cases (each = a sample conversation)

### Use case: Framework skill emits a defense-pattern signal

> Skill (psy:crossref) finishes work and notices: "Nhân vật B intellectualizes under conflict." Calls: `orc:observe --framework psy --signal defense-pattern --payload '{"character":"hoa","mechanism":"intellectualization","trigger":"conflict"}' --source psy:crossref`. Signal recorded.

### Use case: Content skill observes voice drift

> Skill (cre:voice-audit) finishes and notices: "Recent posts diverge from writing-voice.md (too clinical, should be personal)." Calls: `orc:observe --framework cre --signal voice-drift --payload '{"character":"hieu","issue":"too clinical","expected":"personal"}' --source cre:voice-audit`. Signal recorded.

### Use case: Compounding mines observations into learnings

> Later, `orc:compounding --session` reads observation stream, finds 5 defense-pattern signals, 2 voice-drift signals. Proposes extracting: "Nhân vật B intellectualizes under conflict (reinforced 5x)" as a learning worth remembering.

## 5. Important caveats

- **Observations are optional.** Skills can work without emitting signals; automatic hooks ensure baseline tracking.
- **Signals are pointers, not dumps.** Keep payload ≤2 KB; signals point to patterns, not exhaustive data.
- **Semantic signals require judgment.** Only emit when genuinely notable (not every observation).
- **Observation ≠ Action.** Recording "Nhân vật B avoids conflict" doesn't change behavior; it's a note for future reference.
