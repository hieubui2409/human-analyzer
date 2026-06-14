# evl:fit

> Role / casting-fit decision engine — score a character against a role profile and get a CAST / CONDITIONAL / NO verdict with evidence citations.

## What it does

Validates a decision rubric (default: `role-casting-fit`), gathers per-criterion candidate evidence from the character's profile, has the LLM judge each criterion (with a mandatory MAT evidence-tier citation) using `min_judges` input-isolated judge agents, converges the judges deterministically, enforces the safety veto if a RED `safety-clearance` score appears, aggregates into an overall verdict, and writes a standardized scorecard (markdown + JSON) under `docs/profiles/{char}/eval/`. Thin preset over `evl:score` — same engine, role-decision defaults.

## When to use

- **Trigger phrases:** "evl fit", "casting fit", "role fit", "can character play role", "cast decision"
- **Workflow position:** after MAT/PSY/GRO have populated a profile; feeds `EVL.scored` → CRE
- **Output user:** anyone needing a defensible, evidence-cited casting or role-assignment decision

## Flags

| Flag | Effect |
|------|--------|
| `--character <name>` | Character to score (dynamic resolution) |
| `--rubric <id>` | Decision rubric id; defaults to `role-casting-fit` |
| `--json` | Machine-readable scorecard summary |
| `--rescore` | Ignore cached scorecard |

## What it does NOT do

- **Not a judgment-in-script tool:** the script gathers + aggregates; the LLM judges. No scoring heuristic lives in the script.
- **Not a silent pass:** an uncited criterion is `[UNVERIFIED]` (excluded + counted), not a guessed score.
- **Not auto-converging divergence:** high-stakes disagreement returns `DIVERGED` + manual review, never an averaged fake.
- **Not a safety override:** a RED `safety-clearance` score hard-blocks to NO — no aggregate can override it.

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

**Mục đích:** Đánh giá mức độ phù hợp vai diễn của một nhân vật và đưa ra phán quyết CAST / CONDITIONAL / NO kèm trích dẫn bằng chứng. Mặc định dùng rubric `role-casting-fit` (`high_stakes: true`, `min_judges: 2`). Spawn đúng `min_judges` giám khảo cô lập đầu vào cho mỗi tiêu chí; hội tụ bằng `evl_convergence`; điểm RED trên `safety-clearance` phủ quyết kết quả bất kể tổng điểm.

**Khi nào dùng:** Sau khi MAT/PSY/GRO đã dựng hồ sơ; kết quả phát `EVL.scored` → CRE.

**Không làm được:** Không chấm điểm trong script (LLM chấm). Tiêu chí không trích dẫn → `[UNVERIFIED]`. Bất đồng cao → `DIVERGED` + duyệt thủ công. Cờ đỏ `safety-clearance` → phủ quyết cứng thành NO.
