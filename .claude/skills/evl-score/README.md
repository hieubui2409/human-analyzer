# evl:score

> Score a character against any versioned, evidence-cited rubric — the generic EVL engine.

## What it does

Validates a rubric, gathers per-criterion candidate evidence from the character's profile, has the LLM judge each criterion (with a mandatory MAT evidence-tier citation), aggregates the verified scores into domain + overall scores with a verdict, and writes a standardized scorecard (markdown + JSON) under `docs/profiles/{char}/eval/`. Handles psychometric, decision, clinical, and dyad rubrics from their own config — no per-kind forked logic.

## When to use

- **Trigger phrases:** "evl score", "score character against rubric", "run rubric", "evaluate character"
- **Workflow position:** after MAT/PSY/GRO have populated a profile; feeds `EVL.scored` → CRE
- **Output user:** anyone needing a defensible, evidence-cited assessment of a character

## Flags

| Flag | Effect |
|------|--------|
| `--character <name>` | Character to score (dynamic resolution) |
| `--rubric <id>` | Rubric id or path under `docs/rubrics/` |
| `--json` | Machine-readable scorecard summary |
| `--rescore` | Ignore cached scorecard (forced for clinical rubrics) |

## What it does NOT do

- **Not a judgment-in-script tool:** the script gathers + aggregates; the LLM judges. No scoring heuristic lives in the script.
- **Not a silent pass:** an uncited criterion is `[UNVERIFIED]` (excluded + counted), not a guessed score.
- **Not auto-converging divergence:** high-stakes disagreement returns `DIVERGED` + manual review, never an averaged fake.

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

**Mục đích:** Chấm điểm một nhân vật theo một rubric có phiên bản, trích dẫn bằng chứng. Script thu thập bằng chứng + tổng hợp trọng số; LLM chấm từng tiêu chí và bắt buộc trích dẫn tầng bằng chứng MAT (T1–T5). Xuất scorecard chuẩn (markdown + JSON) dưới `docs/profiles/{char}/eval/`.

**Khi nào dùng:** Sau khi MAT/PSY/GRO đã dựng hồ sơ; kết quả phát `EVL.scored` → CRE.

**Không làm được:** Không chấm điểm trong script (LLM chấm). Tiêu chí không trích dẫn → `[UNVERIFIED]`, không bao giờ pass ngầm. Bất đồng cao → `DIVERGED` + duyệt thủ công, không tự trung bình.
