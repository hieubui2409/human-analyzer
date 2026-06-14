# evl:standardize

> Psychometric battery preset — score a character against Big Five + Dark Triad SD3 + Attachment ECR-R with evidence citations, attachment quadrant mapping, and Dark Triad elevation flag.

## What it does

Validates the psychometric battery rubric, gathers per-criterion candidate evidence from the
character's profile, has the LLM judge each criterion (with a mandatory MAT evidence-tier
citation), aggregates the verified scores into domain + overall scores with a verdict, and writes
a standardized scorecard (markdown + JSON) under `docs/profiles/{char}/eval/`. After finalize,
the LLM adds two clinical summaries: attachment style quadrant (Secure / Preoccupied /
Dismissing-Avoidant / Fearful-Avoidant) and a Dark Triad elevation flag (elevated if any
subscale ≥ 4).

This is a thin preset over `evl:score` — the rubric defaults to `psychometric-big-five` and can
be overridden. Everything else is the generic engine.

## When to use

- **Trigger phrases:** "evl standardize", "psychometric battery", "big five score", "standardize character", "run psychometric battery"
- **Workflow position:** after MAT/PSY/GRO have populated a profile; feeds `EVL.scored` → CRE
- **Output user:** anyone needing a defensible, evidence-cited psychometric assessment

## Flags

| Flag | Effect |
|------|--------|
| `--character <name>` | Character to score (dynamic resolution) |
| `--rubric <id>` | Rubric id or path under `docs/rubrics/` (default: `psychometric-big-five`) |
| `--json` | Machine-readable scorecard summary |
| `--rescore` | Ignore cached scorecard |

## What it does NOT do

- **Not a judgment-in-script tool:** the script gathers + aggregates; the LLM judges. No scoring heuristic lives in the script.
- **Not a silent pass:** an uncited criterion is `[UNVERIFIED]` (excluded + counted), not a guessed score.
- **Not an auto-derived quadrant:** attachment quadrant and Dark Triad flag are narrated by the LLM from verified finalized scores, never computed in the script.
- **Not a cross-character normalizer below cohort threshold:** z-score needs ≥3 characters; below that raw scores are shown with a suppression note.

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

**Mục đích:** Preset đánh giá tâm trắc học — chấm điểm nhân vật theo bộ Big Five + Dark Triad SD3 + Attachment ECR-R, trích dẫn bằng chứng. Sau khi finalize, LLM thêm hai tóm tắt lâm sàng: phân ổ gắn bó (Secure / Preoccupied / Dismissing-Avoidant / Fearful-Avoidant) và cờ Dark Triad elevated (khi bất kỳ subscale nào ≥ 4).

**Khi nào dùng:** Sau khi MAT/PSY/GRO đã dựng hồ sơ; kết quả phát `EVL.scored` → CRE.

**Không làm được:** Không chấm điểm trong script (LLM chấm). Tiêu chí không trích dẫn → `[UNVERIFIED]`, không bao giờ pass ngầm. Phân ổ gắn bó và cờ Dark Triad do LLM diễn giải từ điểm đã xác minh, không tính trong script. z-score cần ≥3 nhân vật; dưới đó dùng điểm thô kèm ghi chú.
