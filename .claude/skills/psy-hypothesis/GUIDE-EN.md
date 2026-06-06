# psy:hypothesis — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You're planning Character C's arc. If he gets the Scholarship X scholarship, you want to imagine: Would he celebrate? Freeze? Ruminate about "getting lucky"? This skill reads his profile — his core wounds (abandonment), his defense mechanisms (self-doubt, rationalization), his attachment style (anxious), his triggers — and predicts how he'd respond, step by step: immediate 0-24h, short-term coping, long-term trajectory.

## 2. Core concepts (the mental model)

- **Profile-driven**: The prediction anchors in documented patterns from psychology/formulation.md, darkness/traumas.md, light/strengths-hope.md. Not invented — derived.
- **Three depths**: Shallow is 3–5 bullets (fast). Deep includes immediate/short-term/long-term phases + clinical rationale + confidence scoring. Clinical adds DSM-5/ICD-11 implications + risk levels + cultural context.
- **Multi-character**: Scenarios don't exist in isolation. If Character A burns out, how does Character B react? How does Character C feel abandoned again? This skill can trace the cascade.

## 3. Learning path

**First run:** `psy:hypothesis --character character-c --scenario "Character C gets Scholarship X scholarship" --depth shallow` — quick gut check.

**Deep dive:** `psy:hypothesis --character character-a --scenario "Character B's father returns after 10 years" --depth deep` — rich analysis.

**Multi-character:** `psy:hypothesis --character character-a --scenario "Character A admits he can't mentor Character C anymore" --multi` — see cascading impact.

## 4. Use cases (each = a sample conversation)

### Use case: Quick arc planning

> You: "What happens if Character B loses his job tomorrow?"
> Skill: `psy:hypothesis --character character-b --scenario "Character B loses his job" --depth shallow`
> → Immediate: financial panic + identity crisis (job = worth). Coping: gambling or drinking. Attachment: clings to Character A. Confidence: HIGH.

### Use case: Content ideation (what would they write/say?)

> You: "Character A just mentored Character C through an exam pass. What's his vibe?"
> Skill: `psy:hypothesis --character character-a --scenario "Mentoring Character C to exam success" --depth deep`
> → Immediate: relief + savior activation. Short-term: doubles down on mentoring (validation of worth). Long-term: growth but risk of overextension. Clinical note: savior complex energized; monitor for burnout.

### Use case: Cascade impact (multi-character)

> You: "Character B and Character A's relationship breaks. What happens to Character C?"
> Skill: `psy:hypothesis --character character-b --scenario "Sworn brother relationship breaks with Character A" --multi`
> → Character B: devastation + self-blame. Character A: guilt + protective withdrawal. Character C: orphaned mentorship + abandonment retrigger. Recommendation: HIGH crisis risk.

## 5. Important caveats

- **Confidence scoring is heuristic**: HIGH = aligns with 3+ established patterns. MEDIUM = 1–2 patterns, some uncertainty. LOW = novel scenario, limited data. Trust HIGH/MEDIUM more than LOW.
- **Not a guarantee**: Real humans surprise. A prediction with HIGH confidence still might not occur.
- **Clinical predictions need follow-up**: If `--depth clinical` surfaces crisis risk, run `psy:crisis-assess` for formal documentation.
- **Scenario must be specific**: Vague ("something bad happens") produces vague predictions. Specific scenarios ("abandonment by mentor") anchor better predictions.
