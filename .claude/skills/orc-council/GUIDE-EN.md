# orc:council — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

Some decisions have no single right answer. Is Character B's avoidance rooted in attachment anxiety or avoidant attachment? Should Character A's LinkedIn voice be technical or vulnerable? Should Character C's career go toward grad school or startup? Instead of you flip-flopping, council gathers independent expert opinions and synthesizes. You get clarity.

## 2. Core concepts (the mental model)

**Four independent voices:** Each subagent argues from their role (Advocate for, Skeptic against, Pragmatist practical, Wildcard outside-the-box). No contamination between voices—each sees only the question.

**Anti-anchoring:** By not feeding any context or prior framing, council avoids the trap of everyone defaulting to your initial view. Each voice discovers independently.

**Synthesis is human.** You read all 4 voices and write the synthesized verdict. Scripts handle logistics, you handle judgment.

## 3. Learning path

**First council:** `orc:council --question "Is Character B's core issue avoidance or anxious attachment?" --category psy --character character-b`

**Review the verdict:** Read all 4 responses, then synthesize your takeaway.

**Store the decision:** Council automatically writes the verdict to `.claude/decisions/`.

**Reference later:** Next time you're deciding about Character B's formulation, check the decision log.

## 4. Use cases (each = a sample conversation)

### Use case: Resolve clinical ambiguity

> You: "Character B's behavior looks like both avoidance and anxious attachment. I need clarity."
>
> Skill: Spawns 4 voices, each argues from their angle. Advocate: "It's anxious attachment—she seeks closeness but fears rejection." Skeptic: "No, it's pure avoidance—she distances first." Pragmatist: "Both operate together in cycles." Wildcard: "Maybe it's a trauma response being misread as attachment." You synthesize: "Attachment + avoidance co-occur; she triggers avoidance under academic pressure to protect against rejection."

### Use case: Resolve content direction dispute

> You: "Should Character A's LinkedIn voice be technical or vulnerable? I'm stuck."
>
> Skill: Advocate: "Technical—he's a leader, credibility matters." Skeptic: "No, vulnerability wins engagement." Pragmatist: "Both—tech posts with vulnerability hooks." Wildcard: "What if vulnerability in tech coaching is a whole new angle?" You synthesize: "Technical foundation + vulnerability in mentoring context = unique position."

### Use case: Career path decision for Character C

> You: "Grad school or startup? Both are plausible for him."
>
> Skill: Gathers 4 expert perspectives. After hearing them, you decide based on character psychology, not just practicality.

## 5. Important caveats

- **Council is input, not final word.** You still have to synthesize and decide. The 4 voices aren't correct just because they disagreed.
- **Questions must be focused.** Vague questions ("what about Character B?") produce vague responses. Be specific.
- **Synthesis is crucial.** The hard work happens after council: you integrate 4 viewpoints into one clear direction.
- **Avoid over-using.** Council costs tokens (4 subagents). Use for genuinely ambiguous decisions, not routine calls.
