# gro:career-forecast — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You want to explore **what-if scenarios** for a character's future. This skill takes their current career stage (via Super's Life-Career Rainbow), current skill levels (Dreyfus), learning pattern (Kolb), and age/education context, then projects forward 3–5 years. Think of it as an "if trends continue" forecast, not a prediction you'd bet money on — hence the [FORECAST — NOT FACTUAL] label on everything it outputs.

## 2. Core concepts (the mental model)

**Script-gathers, LLM judges.** The Python script pulls career data (stage, skills, learning style) from profile files. The LLM then applies three heuristic lenses:

1. **Super's career stages** (Growth → Exploration → Establishment → Maintenance → Disengagement): the script identifies current stage, LLM projects forward given age and trajectory direction.
2. **Dreyfus skill progression rates:** skills don't level up uniformly; proficiency growth slows as expertise deepens (Novice → Advanced Beginner is fast; Proficient → Expert takes years).
3. **Confidence is LOW by design.** The skill outputs a confidence flag because real careers have black-swan events, business decisions, luck. All output is speculative.

**Non-factual by design.** The [FORECAST — NOT FACTUAL] label appears in every output section. Use this when brainstorming content angles or exploring character arcs in fiction — not for factual claims.

## 3. Learning path

**First run:** `gro:career-forecast --character <name>` — see the projection format. Notice the [FORECAST] markers.

**Next:** `gro:career-forecast --all --horizon 5` — compare 5-year projections across all 3 characters. Spot diverging trajectories (e.g., one stabilizes, another accelerates).

**As you grow:** `gro:career-forecast --json` for machine-readable output; feed into downstream content generation or comparative analysis.

## 4. Use cases (each = a sample conversation)

### Use case: Explore a character's 3-year career arc for content planning

> **You:** "gro:career-forecast --character hieu --horizon 3"
> 
> **Skill:** Gathers Nhân vật A's current career stage (e.g., Exploration), Dreyfus levels (e.g., Competent in domain X, Advanced Beginner in Y), Kolb learning style. LLM projects: if current trajectory holds, Nhân vật A will likely enter Establishment by year 2–3, with expertise deepening in core domain but slower growth in new domains. Confidence: low (depends on job market, personal choices, etc.). Marks all projections [FORECAST — NOT FACTUAL].
>
> **Use:** You now see a plausible 3-year arc (Exploration → Establishment transition). Useful for character development, content angle mining, or validating a narrative timeline.

### Use case: Compare career projection across characters

> **You:** "gro:career-forecast --all --json | jq '.characters | map(.stage_projection)'"
>
> **Skill:** Returns all 3 characters' projected stages in 3 years. One might stabilize in Establishment, another might still be in Exploration, a third might hit Maintenance.
>
> **Use:** Reveals diverging career maturity. Useful for dyad/triad content (mentoring dynamics, peer comparisons).

## 5. Important caveats

- **[FORECAST — NOT FACTUAL]:** All projections are speculative. Never present a forecast as fact.
- **Confidence is deliberately LOW.** Career projections are unreliable because life happens (layoffs, pivots, health events, luck). Use this for exploration, not prediction.
- **Dreyfus progression rates are heuristic.** The LLM estimates how fast a skill will develop; this is educated guessing, not scientifically calibrated.
- **No PSY-domain forecasting.** This skill forecasts career stage and skill level only. It does NOT forecast psychological change, defense-mechanism evolution, trauma recovery, or attachment shifts — those belong in PSY domain (e.g., `psy:hypothesis` if you want behavioral prediction).
- **Boundary (Rule 15):** GRO→PSY is one-way. The forecast may reference PSY insights (e.g., "given resilience profile from PSY") but never makes PSY projections itself.
